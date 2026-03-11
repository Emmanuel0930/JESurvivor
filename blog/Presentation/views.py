from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError
from drf_spectacular.utils import extend_schema
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

    requested_user_id = request.headers.get("X-User-Id") or request.query_params.get(
        "usuario_id"
    )
    if requested_user_id is not None:
        try:
            user_id = int(requested_user_id)
        except (TypeError, ValueError) as exc:
            raise ValidationError({"usuario_id": "Debe ser un entero válido."}) from exc

        try:
            return Usuario.objects.get(id=user_id)
        except Usuario.DoesNotExist as exc:
            raise NotFound("Usuario no encontrado.") from exc

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


class UsuarioActualView(APIView):
    @extend_schema(
        responses={200: UsuarioActualSerializer, 404: dict},
        tags=["usuario"],
        description="Obtiene el usuario actual del dominio o crea un usuario demo si aún no existe.",
    )
    def get(self, request):
        usuario = resolver_usuario_actual(request)
        serializer = UsuarioActualSerializer(usuario)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ListarKitsView(APIView):
    @extend_schema(
        responses={200: KitSerializer(many=True)},
        tags=["reserva"],
        description="Lista los kits disponibles para reservar.",
    )
    def get(self, request):
        service = ReservaService()
        kits = service.listar_kits(solo_con_stock=False)
        serializer = KitSerializer(kits, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CrearReservaView(APIView):
    @extend_schema(
        request=CrearReservaRequestSerializer,
        responses={
            201: CrearReservaResponseSerializer,
            400: dict,
            404: dict,
            403: dict,
        },
        tags=["reserva"],
        description="Crea una reserva de kit para el usuario actual del dominio.",
    )
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
            response_serializer = CrearReservaResponseSerializer(
                {"reserva_id": reserva.id}
            )
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        except KitNoEncontrado as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except KitNoDisponible as e:
            return Response({"error": str(e)}, status=status.HTTP_409_CONFLICT)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response({"error": "Error inesperado."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VerificarDisponibilidadView(APIView):
    @extend_schema(
        request=VerificarDisponibilidadRequestSerializer,
        responses={
            200: VerificarDisponibilidadResponseSerializer,
            400: dict,
            404: dict,
            409: dict,
        },
        tags=["reserva"],
        description="Verifica si un kit está disponible para un rango de fechas.",
    )
    def post(self, request):
        serializer = VerificarDisponibilidadRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        kit_id = serializer.validated_data["kit_id"]
        inicio = serializer.validated_data["inicio"]
        fin = serializer.validated_data["fin"]

        service = ReservaService()

        try:
            service.verificar_disponibilidad(kit_id, inicio, fin)
            response_serializer = VerificarDisponibilidadResponseSerializer(
                {"disponible": True}
            )
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        except KitNoEncontrado as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except KitNoDisponible as e:
            return Response({"error": str(e)}, status=status.HTTP_409_CONFLICT)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response({"error": "Error inesperado."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CancelarReservaView(APIView):
    @extend_schema(
        request=CancelarReservaRequestSerializer,
        responses={
            200: CancelarReservaResponseSerializer,
            400: dict,
            404: dict,
            409: dict,
        },
        tags=["reserva"],
        description="Cancela una reserva pendiente del usuario actual del dominio.",
    )
    def post(self, request):
        serializer = CancelarReservaRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        reserva_id = serializer.validated_data["reserva_id"]
        usuario = resolver_usuario_actual(request)

        service = ReservaService()

        try:
            reserva = service.cancelar_reserva(usuario, reserva_id)
            response_serializer = CancelarReservaResponseSerializer(
                {"reserva_id": reserva.id, "estado": reserva.estado}
            )
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        except ReservaNoEncontrada as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except ReservaNoCancelable as e:
            return Response({"error": str(e)}, status=status.HTTP_409_CONFLICT)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response({"error": "Error inesperado."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ListarReservasUsuarioView(APIView):
    @extend_schema(
        responses={
            200: ReservaSerializer(many=True),
            404: dict,
        },
        tags=["reserva"],
        description="Lista todas las reservas del usuario actual del dominio.",
    )
    def get(self, request):
        service = ReservaService()
        usuario = resolver_usuario_actual(request)
        reservas = service.listar_reservas_de_usuario(usuario)
        serializer = ReservaSerializer(reservas, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# --- Cursos ---

class ListarCursosView(APIView):
    @extend_schema(
        responses={
            200: CursoSerializer(many=True),
        },
        tags=["curso"],
        description="Lista todos los cursos disponibles (activos).",
    )
    def get(self, request):
        service = CursoService()
        cursos = service.listar_cursos(solo_activos=True)
        serializer = CursoSerializer(cursos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ComprarCursoView(APIView):
    @extend_schema(
        request=ComprarCursoRequestSerializer,
        responses={
            201: ComprarCursoResponseSerializer,
            400: dict,
            404: dict,
            409: dict,
        },
        tags=["curso"],
        description="Compra un curso para el usuario actual del dominio.",
    )
    def post(self, request):
        serializer = ComprarCursoRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        curso_id = serializer.validated_data["curso_id"]
        usuario = resolver_usuario_actual(request)

        service = CursoService()
        try:
            compra = service.comprar_curso(usuario, curso_id)
            response_serializer = ComprarCursoResponseSerializer(compra)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        except CursoNoEncontrado as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except CursoYaComprado as e:
            return Response({"error": str(e)}, status=status.HTTP_409_CONFLICT)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response({"error": "Error inesperado."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
