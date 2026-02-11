from blog.models import KitEspecializado, ReservaKit
from blog.domain.builders import ReservaBuilder
from blog.infra.factories import NotificadorFactory


class ReservaService:

    def __init__(self):
        self.notificador = NotificadorFactory.crear()

    def crear_reserva(self, usuario, kit_id, fecha_inicio, fecha_fin):

        # 1️⃣ Obtener kit
        kit = KitEspecializado.objects.get(id=kit_id)

        # 2️⃣ Verificar disponibilidad
        solapadas = ReservaKit.objects.filter(
            kit=kit,
            fecha_inicio__lt=fecha_fin,
            fecha_fin__gt=fecha_inicio
        ).exists()

        if solapadas:
            raise ValueError("El kit no está disponible en esas fechas")

        # 3️⃣ Builder construye la reserva
        reserva = (
            ReservaBuilder()
            .para_usuario(usuario)
            .con_kit(kit)
            .en_fechas(fecha_inicio, fecha_fin)
            .build()
        )

        # 4️⃣ Guardar
        reserva.save()

        # 5️⃣ Notificar
        self.notificador.enviar_confirmacion(reserva)

        return reserva