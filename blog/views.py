from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from blog.services import ReservaService

class CrearReservaView(APIView):
    def post(self, request):
        usuario = request.user
        kit_id = request.data.get("kit_id")
        inicio = request.data.get("inicio")
        fin = request.data.get("fin")
        service = ReservaService()
        try:
            reserva = service.crear_reserva(usuario, kit_id, inicio, fin)
            return Response({"reserva_id": reserva.id}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
