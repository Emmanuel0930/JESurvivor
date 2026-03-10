from blog.domain.entities import ReservaData
from blog.domain.models import ReservaKit
from blog.domain.validators import (
    validar_campos_reserva,
    validar_fechas_reserva,
    validar_compatibilidad_usuario_kit,
    validar_stock_kit,
)


class ReservaKitBuilder:
    def __init__(self):
        self._usuario = None
        self._kit = None
        self._fecha_inicio = None
        self._fecha_fin = None
        self._estado = ReservaKit.EstadoReserva.PENDIENTE

    def para_usuario(self, usuario):
        self._usuario = usuario
        return self

    def con_kit(self, kit):
        self._kit = kit
        return self

    def en_fechas(self, inicio, fin):
        validar_fechas_reserva(inicio, fin)
        self._fecha_inicio = inicio
        self._fecha_fin = fin
        return self

    def con_estado(self, estado):
        self._estado = estado
        return self

    def build(self):
        validar_campos_reserva(
            usuario=self._usuario,
            kit=self._kit,
            fecha_inicio=self._fecha_inicio,
            fecha_fin=self._fecha_fin,
        )

        validar_stock_kit(self._kit)
        validar_compatibilidad_usuario_kit(self._usuario, self._kit)

        reserva_data = ReservaData(
            usuario=self._usuario,
            kit=self._kit,
            fecha_inicio=self._fecha_inicio,
            fecha_fin=self._fecha_fin,
            estado=self._estado,
        )

        return ReservaKit(
            usuario=reserva_data.usuario,
            kit=reserva_data.kit,
            fecha_inicio=reserva_data.fecha_inicio,
            fecha_fin=reserva_data.fecha_fin,
            estado=reserva_data.estado,
        )