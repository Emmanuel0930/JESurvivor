from datetime import date


def validar_fechas_reserva(inicio, fin):
    if inicio >= fin:
        raise ValueError("La fecha de inicio debe ser menor que la fecha fin")

    if inicio < date.today():
        raise ValueError("No se puede reservar en fechas pasadas")


def validar_campos_reserva(usuario, kit, fecha_inicio, fecha_fin):
    if not all([usuario, kit, fecha_inicio, fecha_fin]):
        raise ValueError("Faltan datos para construir la reserva")
