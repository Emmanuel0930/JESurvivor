from blog.Application.Factories import NotificadorFactory
from blog.Domain.builders import ReservaBuilder
from blog.Infrastructure.repositories import KitRepository, ReservaRepository


class ReservaService:

    def __init__(self):
        self.notificador = NotificadorFactory.crear()
        self.kit_repository = KitRepository()
        self.reserva_repository = ReservaRepository()

    def crear_reserva(self, usuario, kit_id, fecha_inicio, fecha_fin):
        kit = self.kit_repository.obtener_por_id(kit_id)

        solapadas = self.reserva_repository.existe_solapamiento(
            kit=kit,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
        )

        if solapadas:
            raise ValueError("El kit no está disponible en esas fechas")

        reserva = (
            ReservaBuilder()
            .para_usuario(usuario)
            .con_kit(kit)
            .en_fechas(fecha_inicio, fecha_fin)
            .build()
        )

        self.reserva_repository.guardar(reserva)
        self.notificador.enviar_confirmacion(reserva)

        return reserva