from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class ReservaData:
    usuario: object
    kit: object
    fecha_inicio: date
    fecha_fin: date
    estado: str = "pendiente"