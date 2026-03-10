from datetime import date


NIVELES = {
    "basico": 1,
    "intermedio": 2,
    "avanzado": 3,
}


def validar_fechas_reserva(inicio, fin):
    if inicio is None or fin is None:
        raise ValueError("Las fechas de reserva son obligatorias.")

    if inicio >= fin:
        raise ValueError("La fecha de inicio debe ser menor que la fecha fin.")

    if inicio < date.today():
        raise ValueError("No se puede reservar en fechas pasadas.")


def validar_campos_reserva(usuario, kit, fecha_inicio, fecha_fin):
    if not usuario:
        raise ValueError("El usuario es obligatorio.")
    if not kit:
        raise ValueError("El kit es obligatorio.")
    if not fecha_inicio or not fecha_fin:
        raise ValueError("Las fechas son obligatorias.")


def validar_compatibilidad_usuario_kit(usuario, kit):
    nivel_usuario = NIVELES.get(usuario.nivel_experiencia, 0)
    nivel_kit = NIVELES.get(kit.nivel_recomendado, 0)

    if nivel_usuario < nivel_kit:
        raise ValueError(
            "El nivel de experiencia del usuario no es suficiente para este kit."
        )


def validar_stock_kit(kit):
    if kit.stock <= 0:
        raise ValueError("El kit no tiene stock disponible para reserva.")