from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotAuthenticated
from drf_spectacular.utils import extend_schema
from blog.Application.services import ReservaService
from blog.Presentation.serializers import (
    CrearReservaRequestSerializer,
    CrearReservaResponseSerializer,
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
            response_serializer = CrearReservaResponseSerializer({"reserva_id": reserva.id})
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
