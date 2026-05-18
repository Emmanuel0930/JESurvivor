"""
Capa de Presentación — Vistas de JESurvivor.
Entregable 2: Endpoints para servicio propio, aliado y terceros (Adapter).

FIX: 'import requests' movido al interior del método AliadoView.get()
para evitar que un ImportError rompa todo el módulo si el paquete
no está instalado todavía en el contenedor.
"""

import os

from django.conf import settings
from django.utils.translation import gettext as _
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from blog.Application.services import (
    CursoNoEncontrado,
    CursoService,
    CursoYaComprado,
    KitNoEncontrado,
    KitNoDisponible,
    ReservaNoCancelable,
    ReservaNoEncontrada,
    ReservaService,
)
from blog.domain.models import Usuario
from blog.Presentation.serializers import (
    CancelarReservaRequestSerializer,
    CancelarReservaResponseSerializer,
    ComprarCursoRequestSerializer,
    ComprarCursoResponseSerializer,
    CrearReservaRequestSerializer,
    CrearReservaResponseSerializer,
    CursoSerializer,
    KitSerializer,
    ReservaSerializer,
    UsuarioActualSerializer,
    VerificarDisponibilidadRequestSerializer,
    VerificarDisponibilidadResponseSerializer,
)


def resolver_usuario_actual(request):
    auth_user = getattr(request, "user", None)
    if auth_user and getattr(auth_user, "is_authenticated", False):
        username = auth_user.get_username() or "survivor"
        email = getattr(auth_user, "email", "") or f"{username}@jesurvivor.local"
        usuario, _ = Usuario.objects.get_or_create(
            email=email,
            defaults={
                "nombre": auth_user.get_full_name() or username,
                "contrasena_hash": "django-auth",
                "nivel_experiencia": Usuario.NivelExperiencia.INTERMEDIO,
                "ubicacion_climatica": Usuario.UbicacionClimatica.TEMPLADO,
            },
        )
        return usuario

    requested_user_id = request.headers.get("X-User-Id") or request.query_params.get("usuario_id")
    if requested_user_id is not None:
        try:
            user_id = int(requested_user_id)
        except (TypeError, ValueError) as exc:
            raise ValidationError({"usuario_id": _("Debe ser un entero válido.")}) from exc
        try:
            return Usuario.objects.get(id=user_id)
        except Usuario.DoesNotExist as exc:
            raise NotFound(_("Usuario no encontrado.")) from exc

    usuario = Usuario.objects.order_by("id").first()
    if usuario is not None:
        return usuario

    usuario, _ = Usuario.objects.get_or_create(
        email="demo@jesurvivor.local",
        defaults={
            "nombre": "Survivor Demo",
            "contrasena_hash": "demo",
            "nivel_experiencia": Usuario.NivelExperiencia.INTERMEDIO,
            "ubicacion_climatica": Usuario.UbicacionClimatica.TEMPLADO,
        },
    )
    return usuario


class SistemaInfoView(APIView):
    @extend_schema(
        tags=["sistema"],
        description="Información pública del sistema JESurvivor. Expuesto para consumo del equipo aliado.",
        responses={200: dict},
    )
    def get(self, request):
        from blog.domain.models import KitEspecializado, ReservaKit, Curso

        info = {
            "sistema": "JESurvivor",
            "version": "2.0.0",
            "descripcion": "Plataforma de supervivencia con reservas de kits, cursos especializados y comunidad outdoor.",
            "estadisticas": {
                "usuarios_registrados": Usuario.objects.count(),
                "kits_disponibles": KitEspecializado.objects.filter(stock__gt=0).count(),
                "reservas_activas": ReservaKit.objects.filter(estado__in=["pendiente", "confirmada"]).count(),
                "cursos_activos": Curso.objects.filter(activo=True).count(),
            },
            "endpoints_publicos": {
                "kits": "/api/kit/",
                "cursos": "/api/curso/",
                "reservas_v2": "/api/v2/reservas/",
                "clima_supervivencia": "/api/clima/",
                "docs": "/api/docs/",
            },
            "arquitectura": {
                "monolito": "Django 5 + DRF",
                "microservicio_reservas": "Flask 3 (Strangler Pattern)",
                "gateway": "Nginx",
                "broker_asincrono": "Redis + Celery",
                "base_datos": "PostgreSQL 16",
                "infra": "AWS EC2 + Docker Compose",
            },
        }
        return Response(info, status=status.HTTP_200_OK)


class ClimaSupervivenciaView(APIView):
    @extend_schema(
        tags=["integracion"],
        description="Consulta clima actual por entorno. Adapter Pattern sobre Open-Meteo (sin API key).",
        parameters=[
            OpenApiParameter(
                name="entorno",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Entorno: montana, selva, urbano, desierto, nieve",
                required=False,
                default="urbano",
            )
        ],
        responses={200: dict},
    )
    def get(self, request):
        # Import lazy — no rompe el módulo si 'requests' no está instalado aún
        from blog.Application.adapters import ClimaService

        entorno = request.query_params.get("entorno", "urbano")
        entornos_validos = ["montana", "selva", "urbano", "desierto", "nieve"]

        if entorno not in entornos_validos:
            return Response(
                {"error": f"Entorno no válido. Opciones: {', '.join(entornos_validos)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        servicio = ClimaService()
        resultado = servicio.obtener_clima_para_entorno(entorno)
        return Response(resultado, status=status.HTTP_200_OK)


class AliadoView(APIView):
    @extend_schema(
        tags=["integracion"],
        description="Consume el servicio del equipo aliado. Manejo graceful si no está disponible.",
        responses={200: dict, 503: dict},
    )
    def get(self, request):
        # ─────────────────────────────────────────────────────
        # Import DENTRO del método para no romper el módulo
        # si 'requests' no está instalado en el contenedor.
        # ─────────────────────────────────────────────────────
        import requests as http_requests

        aliado_url = getattr(settings, "ALIADO_API_URL", "")

        if not aliado_url or "ALIADO_IP" in aliado_url:
            return Response(
                {
                    "fuente": "equipo_aliado",
                    "estado": "pendiente_configuracion",
                    "mensaje": "La URL del equipo aliado aún no ha sido configurada.",
                    "instrucciones": {
                        "variable": "ALIADO_API_URL",
                        "ejemplo": "http://54.xxx.xxx.xxx:80/api/info/",
                        "ubicacion": "docker-compose.yml → servicio django → environment",
                    },
                },
                status=status.HTTP_200_OK,
            )

        try:
            response = http_requests.get(aliado_url, timeout=5)
            response.raise_for_status()
            return Response(
                {"fuente": "equipo_aliado", "estado": "conectado", "datos": response.json()},
                status=status.HTTP_200_OK,
            )
        except http_requests.Timeout:
            return Response(
                {"fuente": "equipo_aliado", "estado": "timeout", "mensaje": "El servicio aliado no respondió."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except http_requests.ConnectionError:
            return Response(
                {"fuente": "equipo_aliado", "estado": "no_disponible", "mensaje": "Sin conexión al aliado."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except Exception as exc:
            return Response(
                {"fuente": "equipo_aliado", "estado": "error", "mensaje": str(exc)},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )


class DisparadoReporteView(APIView):
    @extend_schema(
        tags=["sistema"],
        description="Dispara generación asíncrona de reporte mediante Celery + Redis.",
        responses={202: dict},
    )
    def post(self, request):
        try:
            from blog.tasks import generar_reporte_reservas  # import lazy
            task = generar_reporte_reservas.delay()
            return Response(
                {
                    "mensaje": "Reporte en proceso. Se generará en background.",
                    "task_id": task.id,
                    "estado": "encolado",
                    "broker": "Redis + Celery",
                },
                status=status.HTTP_202_ACCEPTED,
            )
        except Exception as exc:
            return Response(
                {
                    "error": "No se pudo encolar la tarea. Verifica que Redis esté activo.",
                    "detalle": str(exc),
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )


# ─── Vistas existentes (sin cambio de lógica) ───────────────

class UsuarioActualView(APIView):
    @extend_schema(responses={200: UsuarioActualSerializer}, tags=["usuario"],
                   description="Obtiene el usuario actual del dominio.")
    def get(self, request):
        usuario = resolver_usuario_actual(request)
        return Response(UsuarioActualSerializer(usuario).data, status=status.HTTP_200_OK)


class ListarKitsView(APIView):
    @extend_schema(responses={200: KitSerializer(many=True)}, tags=["reserva"],
                   description="Lista los kits disponibles para reservar.")
    def get(self, request):
        service = ReservaService()
        kits = service.listar_kits(solo_con_stock=False)
        return Response(KitSerializer(kits, many=True).data, status=status.HTTP_200_OK)


class CrearReservaView(APIView):
    @extend_schema(request=CrearReservaRequestSerializer,
                   responses={201: CrearReservaResponseSerializer, 400: dict, 404: dict, 409: dict},
                   tags=["reserva"], description="Crea una reserva de kit.")
    def post(self, request):
        request_serializer = CrearReservaRequestSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)

        usuario = resolver_usuario_actual(request)
        kit_id = request_serializer.validated_data["kit_id"]
        inicio = request_serializer.validated_data["inicio"]
        fin = request_serializer.validated_data["fin"]
        service = ReservaService()

        try:
            reserva = service.crear_reserva(usuario, kit_id, inicio, fin)
            return Response(CrearReservaResponseSerializer({"reserva_id": reserva.id}).data,
                            status=status.HTTP_201_CREATED)
        except KitNoEncontrado as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except KitNoDisponible as e:
            return Response({"error": str(e)}, status=status.HTTP_409_CONFLICT)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response({"error": "Error inesperado."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VerificarDisponibilidadView(APIView):
    @extend_schema(request=VerificarDisponibilidadRequestSerializer,
                   responses={200: VerificarDisponibilidadResponseSerializer, 400: dict, 404: dict, 409: dict},
                   tags=["reserva"], description="Verifica disponibilidad de un kit en fechas.")
    def post(self, request):
        serializer = VerificarDisponibilidadRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        kit_id = serializer.validated_data["kit_id"]
        inicio = serializer.validated_data["inicio"]
        fin = serializer.validated_data["fin"]
        service = ReservaService()

        try:
            service.verificar_disponibilidad(kit_id, inicio, fin)
            return Response(VerificarDisponibilidadResponseSerializer({"disponible": True}).data)
        except KitNoEncontrado as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except KitNoDisponible as e:
            return Response({"error": str(e)}, status=status.HTTP_409_CONFLICT)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response({"error": "Error inesperado."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CancelarReservaView(APIView):
    @extend_schema(request=CancelarReservaRequestSerializer,
                   responses={200: CancelarReservaResponseSerializer, 400: dict, 404: dict, 409: dict},
                   tags=["reserva"], description="Cancela una reserva pendiente.")
    def post(self, request):
        serializer = CancelarReservaRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reserva_id = serializer.validated_data["reserva_id"]
        usuario = resolver_usuario_actual(request)
        service = ReservaService()

        try:
            reserva = service.cancelar_reserva(usuario, reserva_id)
            return Response(CancelarReservaResponseSerializer(
                {"reserva_id": reserva.id, "estado": reserva.estado}).data)
        except ReservaNoEncontrada as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except ReservaNoCancelable as e:
            return Response({"error": str(e)}, status=status.HTTP_409_CONFLICT)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response({"error": "Error inesperado."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ListarReservasUsuarioView(APIView):
    @extend_schema(responses={200: ReservaSerializer(many=True)}, tags=["reserva"],
                   description="Lista todas las reservas del usuario actual.")
    def get(self, request):
        service = ReservaService()
        usuario = resolver_usuario_actual(request)
        reservas = service.listar_reservas_de_usuario(usuario)
        return Response(ReservaSerializer(reservas, many=True).data, status=status.HTTP_200_OK)


class ListarCursosView(APIView):
    @extend_schema(responses={200: CursoSerializer(many=True)}, tags=["curso"],
                   description="Lista todos los cursos disponibles (activos).")
    def get(self, request):
        service = CursoService()
        cursos = service.listar_cursos(solo_activos=True)
        return Response(CursoSerializer(cursos, many=True).data, status=status.HTTP_200_OK)


class ComprarCursoView(APIView):
    @extend_schema(request=ComprarCursoRequestSerializer,
                   responses={201: ComprarCursoResponseSerializer, 400: dict, 404: dict, 409: dict},
                   tags=["curso"], description="Compra un curso para el usuario actual.")
    def post(self, request):
        serializer = ComprarCursoRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        curso_id = serializer.validated_data["curso_id"]
        usuario = resolver_usuario_actual(request)
        service = CursoService()

        try:
            compra = service.comprar_curso(usuario, curso_id)
            return Response(ComprarCursoResponseSerializer(compra).data, status=status.HTTP_201_CREATED)
        except CursoNoEncontrado as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except CursoYaComprado as e:
            return Response({"error": str(e)}, status=status.HTTP_409_CONFLICT)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response({"error": "Error inesperado."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)