from blog.domain.models import KitEspecializado, ReservaKit


class KitRepository:
    def obtener_por_id(self, kit_id):
        return KitEspecializado.objects.get(id=kit_id)


class ReservaRepository:
    def existe_solapamiento(self, kit, fecha_inicio, fecha_fin):
        return ReservaKit.objects.filter(
            kit=kit,
            fecha_inicio__lt=fecha_fin,
            fecha_fin__gt=fecha_inicio,
        ).exists()

    def guardar(self, reserva):
        reserva.save()
        return reserva
