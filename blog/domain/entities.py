from dataclasses import dataclass


@dataclass
class ReservaData:
    usuario: object
    kit: object
    fecha_inicio: object
    fecha_fin: object
    estado: str = "pendiente"
