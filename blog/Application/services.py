"""
Capa de Aplicación — Service Layer de JESurvivor.
Entregable 2: Integra tareas asíncronas de Celery para notificaciones.
"""

from blog.Application.Factories import NotificadorFactory
from blog.domain.builders import ReservaKitBuilder
from blog.domain.models import CompraCurso, Curso, KitEspecializado, ReservaKit
from blog.Infrastructure.repositories import (
    CompraCursoRepository,
    CursoRepository,
    KitRepository,
    ReservaRepository,
)


class ReservaNoEncontrada(Exception):
    """Se lanza cuando una reserva no existe o no pertenece al usuario."""


class ReservaNoCancelable(Exception):
    """Se lanza cuando una reserva no puede ser cancelada por su estado."""


class KitNoDisponible(Exception):
    """Se lanza cuando un kit no está disponible para las fechas solicitadas."""


class KitNoEncontrado(Exception):
    """Se lanza cuando un kit no existe."""


class CursoNoEncontrado(Exception):
    """Se lanza cuando un curso no existe o no está activo."""


class CursoYaComprado(Exception):
    """Se lanza cuando el usuario ya compró ese curso."""


class ReservaService:
    """
    Service Layer para la gestión de reservas de kits.
    Orquesta dominio, builders, validadores, repositorios y tareas asíncronas.
    """

    def __init__(self):
        self.notificador = NotificadorFactory.crear()
        self.kit_repository = KitRepository()
        self.reserva_repository = ReservaRepository()

    def listar_kits(self, solo_con_stock=False):
        return self.kit_repository.listar_kits(solo_con_stock=solo_con_stock)

    def crear_reserva(self, usuario, kit_id, fecha_inicio, fecha_fin):
        try:
            kit = self.kit_repository.obtener_por_id(kit_id)
        except KitEspecializado.DoesNotExist as exc:
            raise KitNoEncontrado("El kit no existe.") from exc

        if self.reserva_repository.existe_solapamiento(
            kit=kit,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
        ):
            raise KitNoDisponible("El kit no está disponible en esas fechas.")

        reserva = (
            ReservaKitBuilder()
            .para_usuario(usuario)
            .con_kit(kit)
            .en_fechas(fecha_inicio, fecha_fin)
            .build()
        )

        self.reserva_repository.guardar(reserva)

        # ──────────────────────────────────────────────────────────
        # Tarea asíncrona: enviar confirmación en background (Celery)
        # No bloquea la respuesta HTTP — se procesa en el worker
        # ──────────────────────────────────────────────────────────
        try:
            from blog.tasks import enviar_confirmacion_reserva
            enviar_confirmacion_reserva.delay(
                reserva_id=reserva.id,
                usuario_email=getattr(usuario, "email", ""),
                usuario_nombre=getattr(usuario, "nombre", ""),
                kit_nombre=kit.nombre,
                fecha_inicio=str(fecha_inicio),
                fecha_fin=str(fecha_fin),
            )
        except Exception:
            # Si Celery/Redis no está disponible, usa notificador síncrono (fallback)
            self.notificador.enviar_confirmacion(reserva)

        return reserva

    def verificar_disponibilidad(self, kit_id, fecha_inicio, fecha_fin):
        try:
            kit = self.kit_repository.obtener_por_id(kit_id)
        except KitEspecializado.DoesNotExist as exc:
            raise KitNoEncontrado("El kit no existe.") from exc

        if self.reserva_repository.existe_solapamiento(
            kit=kit,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
        ):
            raise KitNoDisponible("El kit no está disponible en esas fechas.")

    def cancelar_reserva(self, usuario, reserva_id):
        try:
            reserva = self.reserva_repository.obtener_por_id(reserva_id)
        except ReservaKit.DoesNotExist as exc:
            raise ReservaNoEncontrada("La reserva no existe.") from exc

        if reserva.usuario != usuario:
            raise ReservaNoEncontrada("La reserva no existe para este usuario.")

        if reserva.estado != ReservaKit.EstadoReserva.PENDIENTE:
            raise ReservaNoCancelable(
                "Solo se pueden cancelar reservas en estado pendiente."
            )

        reserva.estado = ReservaKit.EstadoReserva.CANCELADA
        self.reserva_repository.guardar(reserva)

        # Tarea asíncrona: notificar cancelación
        try:
            from blog.tasks import enviar_notificacion_cancelacion
            enviar_notificacion_cancelacion.delay(
                reserva_id=reserva.id,
                usuario_email=getattr(usuario, "email", ""),
                usuario_nombre=getattr(usuario, "nombre", ""),
                kit_nombre=reserva.kit.nombre,
            )
        except Exception:
            pass  # No bloquear si Celery no está disponible

        return reserva

    def listar_reservas_de_usuario(self, usuario):
        return self.reserva_repository.listar_por_usuario(usuario)


class CursoService:
    """
    Service Layer para la gestión de cursos y compras.
    """

    def __init__(self):
        self.curso_repository = CursoRepository()
        self.compra_curso_repository = CompraCursoRepository()

    def listar_cursos(self, solo_activos=True):
        return self.curso_repository.listar_cursos(solo_activos=solo_activos)

    def comprar_curso(self, usuario, curso_id):
        try:
            curso = self.curso_repository.obtener_por_id(curso_id)
        except Curso.DoesNotExist:
            raise CursoNoEncontrado("El curso no existe.")

        if not curso.activo:
            raise CursoNoEncontrado("El curso no está disponible.")

        if self.compra_curso_repository.existe_compra(usuario, curso):
            raise CursoYaComprado("Ya has comprado este curso.")

        compra = CompraCurso(usuario=usuario, curso=curso)
        self.compra_curso_repository.guardar(compra)
        return compra
