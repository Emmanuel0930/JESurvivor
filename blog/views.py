from django.views import View
from django.http import JsonResponse
from blog.services import ReservaService

class CrearReservaView(View):
    def post(self, request):
        usuario = request.user
        kit_id = request.POST.get("kit_id")
        inicio = request.POST.get("inicio")
        fin = request.POST.get("fin")
        service = ReservaService()
        reserva = service.crear_reserva(usuario, kit_id, inicio, fin)
        return JsonResponse({"reserva_id": reserva.id})
