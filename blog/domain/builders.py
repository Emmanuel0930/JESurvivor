from django.conf import settings

from blog.domain.entities import ReservaData
from blog.domain.models import ReservaKit
from blog.domain.validators import (
    ReservaKitCreationValidator,
    validar_campos_reserva,
    validar_fechas_reserva,
    validar_compatibilidad_usuario_kit,
    validar_stock_kit,
)


class _LegacyReservaKitBuilder:
    """Flujo legacy conservado para transición progresiva."""

    @staticmethod
    def build(usuario, kit, fecha_inicio, fecha_fin, estado):
        validar_campos_reserva(
            usuario=usuario,
            kit=kit,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
        )

        validar_stock_kit(kit)
        validar_compatibilidad_usuario_kit(usuario, kit)

        reserva_data = ReservaData(
            usuario=usuario,
            kit=kit,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            estado=estado,
        )

        return ReservaKit(
            usuario=reserva_data.usuario,
            kit=reserva_data.kit,
            fecha_inicio=reserva_data.fecha_inicio,
            fecha_fin=reserva_data.fecha_fin,
            estado=reserva_data.estado,
        )


class _StranglerReservaKitBuilder:
    """Nueva ruta para creación de reserva; reemplaza progresivamente al flujo legacy."""

    @staticmethod
    def build(usuario, kit, fecha_inicio, fecha_fin, estado):
        ReservaKitCreationValidator.validar_creacion(
            usuario=usuario,
            kit=kit,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
        )

        reserva_data = ReservaData(
            usuario=usuario,
            kit=kit,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            estado=estado,
        )

        return ReservaKit(
            usuario=reserva_data.usuario,
            kit=reserva_data.kit,
            fecha_inicio=reserva_data.fecha_inicio,
            fecha_fin=reserva_data.fecha_fin,
            estado=reserva_data.estado,
        )


class ReservaKitBuilder:
    """
    Fachada Strangler Pattern para la creación de reservas de kits.
    - Nuevo flujo: RESERVA_KIT_STRANGLER_ENABLED=True (default)
    - Fallback legacy: RESERVA_KIT_STRANGLER_ENABLED=False
    """

    def __init__(self):
        self._usuario = None
        self._kit = None
        self._fecha_inicio = None
        self._fecha_fin = None
        self._estado = ReservaKit.EstadoReserva.PENDIENTE
        self._usar_strangler = getattr(settings, "RESERVA_KIT_STRANGLER_ENABLED", True)

    def para_usuario(self, usuario):
        self._usuario = usuario
        return self

    def con_kit(self, kit):
        self._kit = kit
        return self

    def en_fechas(self, inicio, fin):
        if self._usar_strangler:
            ReservaKitCreationValidator.validar_fechas_creacion(inicio, fin)
        else:
            validar_fechas_reserva(inicio, fin)
        self._fecha_inicio = inicio
        self._fecha_fin = fin
        return self

    def con_estado(self, estado):
        self._estado = estado
        return self

    def build(self):
        builder_impl = (
            _StranglerReservaKitBuilder if self._usar_strangler else _LegacyReservaKitBuilder
        )
        return builder_impl.build(
            usuario=self._usuario,
            kit=self._kit,
            fecha_inicio=self._fecha_inicio,
            fecha_fin=self._fecha_fin,
            estado=self._estado,
        )