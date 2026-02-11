from datetime import date
from blog.models import ReservaKit


class ReservaBuilder:

    def __init__(self):
        self._usuario = None
        self._kit = None
        self._fecha_inicio = None
        self._fecha_fin = None

    def para_usuario(self, usuario):
        self._usuario = usuario
        return self

    def con_kit(self, kit):
        self._kit = kit
        return self

    def en_fechas(self, inicio, fin):
        if inicio >= fin:
            raise ValueError("La fecha de inicio debe ser menor que la fecha fin")

        if inicio < date.today():
            raise ValueError("No se puede reservar en fechas pasadas")

        self._fecha_inicio = inicio
        self._fecha_fin = fin
        return self

    def build(self):

        if not all([self._usuario, self._kit, self._fecha_inicio, self._fecha_fin]):
            raise ValueError("Faltan datos para construir la reserva")

        reserva = ReservaKit(
            usuario=self._usuario,
            kit=self._kit,
            fecha_inicio=self._fecha_inicio,
            fecha_fin=self._fecha_fin,
            estado="pendiente"
        )

        return reserva