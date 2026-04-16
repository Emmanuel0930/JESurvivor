from datetime import date

from django.core.exceptions import ValidationError
from django.utils import timezone


NIVELES = {
    "basico": 1,
    "intermedio": 2,
    "avanzado": 3,
}


class ReservaKitCreationValidator:
    """
    Nueva implementación de validación para creación de reservas.
    Se usa como objetivo del Strangler Pattern.
    """

    @classmethod
    def validar_creacion(cls, usuario, kit, fecha_inicio, fecha_fin):
        cls.validar_campos(usuario, kit, fecha_inicio, fecha_fin)
        cls.validar_fechas_creacion(fecha_inicio, fecha_fin)
        cls.validar_stock(kit)
        cls.validar_compatibilidad(usuario, kit)

    @staticmethod
    def validar_fechas_creacion(inicio, fin):
        if inicio is None or fin is None:
            raise ValueError("Las fechas de reserva son obligatorias.")

        if inicio >= fin:
            raise ValueError("La fecha de inicio debe ser menor que la fecha fin.")

        if inicio < date.today():
            raise ValueError("No se puede reservar en fechas pasadas.")

    @staticmethod
    def validar_campos(usuario, kit, fecha_inicio, fecha_fin):
        if not usuario:
            raise ValueError("El usuario es obligatorio.")
        if not kit:
            raise ValueError("El kit es obligatorio.")
        if not fecha_inicio or not fecha_fin:
            raise ValueError("Las fechas son obligatorias.")

    @staticmethod
    def validar_compatibilidad(usuario, kit):
        nivel_usuario = NIVELES.get(usuario.nivel_experiencia, 0)
        nivel_kit = NIVELES.get(kit.nivel_recomendado, 0)

        if nivel_usuario < nivel_kit:
            raise ValueError(
                "El nivel de experiencia del usuario no es suficiente para este kit."
            )

    @staticmethod
    def validar_stock(kit):
        if kit.stock <= 0:
            raise ValueError("El kit no tiene stock disponible para reserva.")


def validar_rango_fechas_modelo_reserva(fecha_inicio, fecha_fin, hoy=None):
    """Nueva validación reutilizable del modelo ReservaKit (ruta strangler)."""
    hoy = hoy or timezone.localdate()

    if fecha_inicio is None or fecha_fin is None:
        return

    if fecha_inicio >= fecha_fin:
        raise ValidationError(
            {"fecha_fin": "La fecha fin debe ser posterior a la fecha inicio."}
        )

    if fecha_inicio < hoy:
        raise ValidationError(
            {"fecha_inicio": "No se permiten reservas en fechas pasadas."}
        )


def validar_fechas_reserva(inicio, fin):
    ReservaKitCreationValidator.validar_fechas_creacion(inicio, fin)


def validar_campos_reserva(usuario, kit, fecha_inicio, fecha_fin):
    ReservaKitCreationValidator.validar_campos(usuario, kit, fecha_inicio, fecha_fin)


def validar_compatibilidad_usuario_kit(usuario, kit):
    ReservaKitCreationValidator.validar_compatibilidad(usuario, kit)


def validar_stock_kit(kit):
    ReservaKitCreationValidator.validar_stock(kit)