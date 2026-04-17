"""
Microservicio Flask — Reservas de Kit
Patrón Estrangulador (Strangler Fig Pattern)
Ruta estrangulada: /api/v2/reservas/
"""

import json
import os
from datetime import date, datetime

import psycopg2
import psycopg2.extras
from flask import Flask, jsonify, request

app = Flask(__name__)

# ─────────────────────────────────────────────
# Configuración de base de datos (PostgreSQL compartida)
# ─────────────────────────────────────────────

DB_HOST = os.environ.get("DB_HOST", "db")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_NAME = os.environ.get("DB_NAME", "jesurvivor")
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASS = os.environ.get("DB_PASS", "postgres")


def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        cursor_factory=psycopg2.extras.RealDictCursor,
    )


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def error_response(message: str, status_code: int):
    return jsonify({"error": message}), status_code


def parse_date(value: str) -> date:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        raise ValueError(f"Fecha inválida '{value}'. Use el formato YYYY-MM-DD.")


def serialize_date(d):
    return d.isoformat() if d else None


# ─────────────────────────────────────────────
# Lógica de Negocio (extraída del monolito Django)
# ─────────────────────────────────────────────

def obtener_usuario(conn, usuario_id: int):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT id, nombre, email, nivel_experiencia, ubicacion_climatica "
            "FROM blog_usuario WHERE id = %s",
            (usuario_id,),
        )
        row = cur.fetchone()
    if not row:
        raise LookupError(f"Usuario {usuario_id} no encontrado.")
    return dict(row)


def listar_kits(conn, solo_con_stock: bool = False):
    query = (
        "SELECT p.id, p.nombre, p.descripcion, p.precio, p.tipo, "
        "       p.nivel_recomendado, p.stock, k.entorno, k.lista_items "
        "FROM blog_kitespecializado k "
        "JOIN blog_producto p ON k.producto_ptr_id = p.id"
    )
    if solo_con_stock:
        query += " WHERE p.stock > 0"

    with conn.cursor() as cur:
        cur.execute(query)
        rows = cur.fetchall()

    result = []
    for row in rows:
        kit = dict(row)
        # lista_items puede ser string JSON o lista; normalizamos
        li = kit.get("lista_items", [])
        if isinstance(li, str):
            try:
                li = json.loads(li)
            except json.JSONDecodeError:
                li = []
        kit["lista_items"] = li
        kit["precio"] = float(kit["precio"])
        result.append(kit)
    return result


def obtener_kit(conn, kit_id: int):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT p.id, p.nombre, p.descripcion, p.precio, p.tipo, "
            "       p.nivel_recomendado, p.stock, k.entorno, k.lista_items "
            "FROM blog_kitespecializado k "
            "JOIN blog_producto p ON k.producto_ptr_id = p.id "
            "WHERE p.id = %s",
            (kit_id,),
        )
        row = cur.fetchone()
    if not row:
        raise LookupError(f"Kit {kit_id} no encontrado.")
    return dict(row)


def existe_solapamiento(conn, kit_id: int, fecha_inicio: date, fecha_fin: date) -> bool:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT COUNT(*) AS cnt FROM blog_reservakit
            WHERE kit_id = %s
              AND estado IN ('pendiente', 'confirmada')
              AND fecha_inicio <= %s
              AND fecha_fin    >= %s
            """,
            (kit_id, fecha_fin, fecha_inicio),
        )
        row = cur.fetchone()
    return row["cnt"] > 0


def crear_reserva(conn, usuario_id: int, kit_id: int, fecha_inicio: date, fecha_fin: date):
    if fecha_inicio >= fecha_fin:
        raise ValueError("La fecha de inicio debe ser anterior a la fecha de fin.")
    if fecha_inicio < date.today():
        raise ValueError("La fecha de inicio no puede estar en el pasado.")

    if existe_solapamiento(conn, kit_id, fecha_inicio, fecha_fin):
        raise KitNoDisponible("El kit no está disponible en esas fechas.")

    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO blog_reservakit (usuario_id, kit_id, fecha_inicio, fecha_fin, estado)
            VALUES (%s, %s, %s, %s, 'pendiente')
            RETURNING id, usuario_id, kit_id, fecha_inicio, fecha_fin, estado
            """,
            (usuario_id, kit_id, fecha_inicio, fecha_fin),
        )
        row = cur.fetchone()
    conn.commit()
    return dict(row)


def cancelar_reserva(conn, usuario_id: int, reserva_id: int):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT id, usuario_id, estado FROM blog_reservakit WHERE id = %s",
            (reserva_id,),
        )
        row = cur.fetchone()

    if not row:
        raise LookupError("La reserva no existe.")
    row = dict(row)

    if row["usuario_id"] != usuario_id:
        raise LookupError("La reserva no existe para este usuario.")

    if row["estado"] != "pendiente":
        raise ReservaNoCancelable("Solo se pueden cancelar reservas en estado pendiente.")

    with conn.cursor() as cur:
        cur.execute(
            "UPDATE blog_reservakit SET estado = 'cancelada' WHERE id = %s "
            "RETURNING id, estado",
            (reserva_id,),
        )
        updated = cur.fetchone()
    conn.commit()
    return dict(updated)


def listar_reservas_usuario(conn, usuario_id: int):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT r.id, r.kit_id, r.fecha_inicio, r.fecha_fin, r.estado,
                   p.nombre AS kit_nombre
            FROM blog_reservakit r
            JOIN blog_kitespecializado k ON r.kit_id = k.producto_ptr_id
            JOIN blog_producto p ON k.producto_ptr_id = p.id
            WHERE r.usuario_id = %s
            ORDER BY r.fecha_inicio DESC
            """,
            (usuario_id,),
        )
        rows = cur.fetchall()
    return [
        {
            **dict(r),
            "fecha_inicio": serialize_date(r["fecha_inicio"]),
            "fecha_fin": serialize_date(r["fecha_fin"]),
        }
        for r in rows
    ]


# ─────────────────────────────────────────────
# Excepciones de dominio
# ─────────────────────────────────────────────

class KitNoDisponible(Exception):
    pass


class ReservaNoCancelable(Exception):
    pass


# ─────────────────────────────────────────────
# Endpoints REST
# ─────────────────────────────────────────────

@app.route("/api/v2/reservas/health", methods=["GET"])
def health():
    """Health check del microservicio."""
    return jsonify({"status": "ok", "service": "flask_reservas"}), 200


@app.route("/api/v2/reservas/kits", methods=["GET"])
def endpoint_listar_kits():
    """Lista todos los kits disponibles."""
    solo_con_stock = request.args.get("solo_con_stock", "false").lower() == "true"
    try:
        conn = get_connection()
        kits = listar_kits(conn, solo_con_stock=solo_con_stock)
        conn.close()
        return jsonify(kits), 200
    except Exception as e:
        return error_response(f"Error interno: {str(e)}", 500)


@app.route("/api/v2/reservas/crear", methods=["POST"])
def endpoint_crear_reserva():
    """
    Crea una reserva de kit.
    Body JSON: { "usuario_id": int, "kit_id": int, "inicio": "YYYY-MM-DD", "fin": "YYYY-MM-DD" }
    """
    data = request.get_json(silent=True)
    if not data:
        return error_response("El cuerpo de la solicitud debe ser JSON.", 400)

    required = ["usuario_id", "kit_id", "inicio", "fin"]
    missing = [f for f in required if f not in data]
    if missing:
        return error_response(f"Campos requeridos: {', '.join(missing)}", 400)

    try:
        usuario_id = int(data["usuario_id"])
        kit_id = int(data["kit_id"])
        fecha_inicio = parse_date(data["inicio"])
        fecha_fin = parse_date(data["fin"])
    except (ValueError, TypeError) as e:
        return error_response(str(e), 400)

    try:
        conn = get_connection()
        obtener_usuario(conn, usuario_id)  # valida que el usuario exista
        reserva = crear_reserva(conn, usuario_id, kit_id, fecha_inicio, fecha_fin)
        conn.close()
        return jsonify({
            "reserva_id": reserva["id"],
            "estado": reserva["estado"],
            "fecha_inicio": serialize_date(reserva["fecha_inicio"]),
            "fecha_fin": serialize_date(reserva["fecha_fin"]),
        }), 201
    except LookupError as e:
        return error_response(str(e), 404)
    except KitNoDisponible as e:
        return error_response(str(e), 409)
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f"Error interno: {str(e)}", 500)


@app.route("/api/v2/reservas/verificar-disponibilidad", methods=["POST"])
def endpoint_verificar_disponibilidad():
    """
    Verifica si un kit está disponible en un rango de fechas.
    Body JSON: { "kit_id": int, "inicio": "YYYY-MM-DD", "fin": "YYYY-MM-DD" }
    """
    data = request.get_json(silent=True)
    if not data:
        return error_response("El cuerpo de la solicitud debe ser JSON.", 400)

    required = ["kit_id", "inicio", "fin"]
    missing = [f for f in required if f not in data]
    if missing:
        return error_response(f"Campos requeridos: {', '.join(missing)}", 400)

    try:
        kit_id = int(data["kit_id"])
        fecha_inicio = parse_date(data["inicio"])
        fecha_fin = parse_date(data["fin"])
    except (ValueError, TypeError) as e:
        return error_response(str(e), 400)

    try:
        conn = get_connection()
        obtener_kit(conn, kit_id)  # valida que el kit exista
        hay_solapamiento = existe_solapamiento(conn, kit_id, fecha_inicio, fecha_fin)
        conn.close()
        if hay_solapamiento:
            return error_response("El kit no está disponible en esas fechas.", 409)
        return jsonify({"disponible": True, "kit_id": kit_id}), 200
    except LookupError as e:
        return error_response(str(e), 404)
    except Exception as e:
        return error_response(f"Error interno: {str(e)}", 500)


@app.route("/api/v2/reservas/cancelar", methods=["POST"])
def endpoint_cancelar_reserva():
    """
    Cancela una reserva pendiente.
    Body JSON: { "usuario_id": int, "reserva_id": int }
    """
    data = request.get_json(silent=True)
    if not data:
        return error_response("El cuerpo de la solicitud debe ser JSON.", 400)

    required = ["usuario_id", "reserva_id"]
    missing = [f for f in required if f not in data]
    if missing:
        return error_response(f"Campos requeridos: {', '.join(missing)}", 400)

    try:
        usuario_id = int(data["usuario_id"])
        reserva_id = int(data["reserva_id"])
    except (ValueError, TypeError) as e:
        return error_response(str(e), 400)

    try:
        conn = get_connection()
        resultado = cancelar_reserva(conn, usuario_id, reserva_id)
        conn.close()
        return jsonify({"reserva_id": resultado["id"], "estado": resultado["estado"]}), 200
    except LookupError as e:
        return error_response(str(e), 404)
    except ReservaNoCancelable as e:
        return error_response(str(e), 409)
    except Exception as e:
        return error_response(f"Error interno: {str(e)}", 500)


@app.route("/api/v2/reservas/", methods=["GET"])
@app.route("/api/v2/reservas/<int:usuario_id>", methods=["GET"])
def endpoint_listar_reservas(usuario_id: int = None):
    """
    Lista todas las reservas de un usuario.
    Se puede pasar el usuario_id en la URL o como query param ?usuario_id=X
    """
    if usuario_id is None:
        try:
            usuario_id = int(request.args.get("usuario_id", 0))
        except (ValueError, TypeError):
            return error_response("usuario_id debe ser un entero.", 400)

    if not usuario_id:
        return error_response("Se requiere usuario_id.", 400)

    try:
        conn = get_connection()
        obtener_usuario(conn, usuario_id)
        reservas = listar_reservas_usuario(conn, usuario_id)
        conn.close()
        return jsonify(reservas), 200
    except LookupError as e:
        return error_response(str(e), 404)
    except Exception as e:
        return error_response(f"Error interno: {str(e)}", 500)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
