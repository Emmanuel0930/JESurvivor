from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotAuthenticated
from drf_spectacular.utils import extend_schema
from blog.Application.services import (
    CursoNoEncontrado,
    CursoService,
    CursoYaComprado,
    KitNoDisponible,
    ReservaNoCancelable,
    ReservaNoEncontrada,
    ReservaService,
)
from blog.Presentation.serializers import (
    CancelarReservaRequestSerializer,
    CancelarReservaResponseSerializer,
    ComprarCursoRequestSerializer,
    ComprarCursoResponseSerializer,
    CrearReservaRequestSerializer,
    CrearReservaResponseSerializer,
    CursoSerializer,
    ReservaSerializer,
    VerificarDisponibilidadRequestSerializer,
    VerificarDisponibilidadResponseSerializer,
)


class CrearReservaView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=CrearReservaRequestSerializer,
        responses={
            201: CrearReservaResponseSerializer,
            400: dict,
            401: dict,
            403: dict,
        },
        tags=["reserva"],
        description="Crea una reserva de kit para el usuario autenticado.",
    )
    def post(self, request):
        if not request.user or not request.user.is_authenticated:
            raise NotAuthenticated("Debes autenticarte para crear una reserva.")

        request_serializer = CrearReservaRequestSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)

        usuario = request.user
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
        except KitNoDisponible as e:
            return Response({"error": str(e)}, status=status.HTTP_409_CONFLICT)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": "Error inesperado."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VerificarDisponibilidadView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=VerificarDisponibilidadRequestSerializer,
        responses={
            200: VerificarDisponibilidadResponseSerializer,
            400: dict,
            401: dict,
            409: dict,
        },
        tags=["reserva"],
        description="Verifica si un kit está disponible para un rango de fechas.",
    )
    def post(self, request):
        if not request.user or not request.user.is_authenticated:
            raise NotAuthenticated("Debes autenticarte para verificar disponibilidad.")

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
        except KitNoDisponible as e:
            return Response({"error": str(e)}, status=status.HTTP_409_CONFLICT)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response({"error": "Error inesperado."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CancelarReservaView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=CancelarReservaRequestSerializer,
        responses={
            200: CancelarReservaResponseSerializer,
            400: dict,
            401: dict,
            404: dict,
            409: dict,
        },
        tags=["reserva"],
        description="Cancela una reserva pendiente del usuario autenticado.",
    )
    def post(self, request):
        if not request.user or not request.user.is_authenticated:
            raise NotAuthenticated("Debes autenticarte para cancelar una reserva.")

        serializer = CancelarReservaRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        reserva_id = serializer.validated_data["reserva_id"]
        usuario = request.user

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
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            200: ReservaSerializer(many=True),
            401: dict,
        },
        tags=["reserva"],
        description="Lista todas las reservas del usuario autenticado.",
    )
    def get(self, request):
        if not request.user or not request.user.is_authenticated:
            raise NotAuthenticated("Debes autenticarte para ver tus reservas.")

        service = ReservaService()
        reservas = service.listar_reservas_de_usuario(request.user)
        serializer = ReservaSerializer(reservas, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# --- Cursos ---

class ListarCursosView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            200: CursoSerializer(many=True),
            401: dict,
        },
        tags=["curso"],
        description="Lista todos los cursos disponibles (activos).",
    )
    def get(self, request):
        if not request.user or not request.user.is_authenticated:
            raise NotAuthenticated("Debes autenticarte para ver los cursos.")

        service = CursoService()
        cursos = service.listar_cursos(solo_activos=True)
        serializer = CursoSerializer(cursos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ComprarCursoView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=ComprarCursoRequestSerializer,
        responses={
            201: ComprarCursoResponseSerializer,
            400: dict,
            401: dict,
            404: dict,
            409: dict,
        },
        tags=["curso"],
        description="Compra un curso para el usuario autenticado.",
    )
    def post(self, request):
        if not request.user or not request.user.is_authenticated:
            raise NotAuthenticated("Debes autenticarte para comprar un curso.")

        serializer = ComprarCursoRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        curso_id = serializer.validated_data["curso_id"]
        usuario = request.user

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
