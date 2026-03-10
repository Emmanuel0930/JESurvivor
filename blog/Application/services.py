from blog.Application.Factories import NotificadorFactory
from blog.domain.builders import ReservaKitBuilder
from blog.domain.models import CompraCurso, Curso, ReservaKit
from blog.Infrastructure.repositories import (
    CompraCursoRepository,
    CursoRepository,
    KitRepository,
    ReservaRepository,
)


class ReservaNoEncontrada(Exception):
    """Se lanza cuando una reserva no existe o no pertenece al usuario."""


class ReservaNoCancelable(Exception):
    """Se lanza cuando una reserva no puede ser cancelada por su estado."""


class KitNoDisponible(Exception):
    """Se lanza cuando un kit no está disponible para las fechas solicitadas."""


class CursoNoEncontrado(Exception):
    """Se lanza cuando un curso no existe o no está activo."""


class CursoYaComprado(Exception):
    """Se lanza cuando el usuario ya compró ese curso."""


class ReservaService:
    """
    Service Layer para la gestión de reservas de kits.
    Orquesta el uso de modelos de dominio, builders, validadores y repositorios.
    """

    def __init__(self):
        self.notificador = NotificadorFactory.crear()
        self.kit_repository = KitRepository()
        self.reserva_repository = ReservaRepository()

    def crear_reserva(self, usuario, kit_id, fecha_inicio, fecha_fin):
        kit = self.kit_repository.obtener_por_id(kit_id)

        if self.reserva_repository.existe_solapamiento(
            kit=kit,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
        ):
            raise KitNoDisponible("El kit no está disponible en esas fechas.")

        reserva = (
            ReservaKitBuilder()
            .para_usuario(usuario)
            .con_kit(kit)
            .en_fechas(fecha_inicio, fecha_fin)
            .build()
        )

        self.reserva_repository.guardar(reserva)
        self.notificador.enviar_confirmacion(reserva)

        return reserva

    def verificar_disponibilidad(self, kit_id, fecha_inicio, fecha_fin):
        """
        Caso de uso: verificar si un kit está disponible en un rango de fechas.
        Levanta KitNoDisponible si hay conflicto, en caso contrario no levanta excepción.
        """
        kit = self.kit_repository.obtener_por_id(kit_id)

        if self.reserva_repository.existe_solapamiento(
            kit=kit,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
        ):
            raise KitNoDisponible("El kit no está disponible en esas fechas.")

    def cancelar_reserva(self, usuario, reserva_id):
        """
        Caso de uso: cancelar una reserva pendiente del usuario.
        - Levanta ReservaNoEncontrada si la reserva no existe o no pertenece al usuario.
        - Levanta ReservaNoCancelable si la reserva no está en estado pendiente.
        """
        reserva = self.reserva_repository.obtener_por_id(reserva_id)

        if reserva.usuario != usuario:
            raise ReservaNoEncontrada("La reserva no existe para este usuario.")

        if reserva.estado != ReservaKit.EstadoReserva.PENDIENTE:
            raise ReservaNoCancelable(
                "Solo se pueden cancelar reservas en estado pendiente."
            )

        reserva.estado = ReservaKit.EstadoReserva.CANCELADA
        self.reserva_repository.guardar(reserva)

        return reserva

    def listar_reservas_de_usuario(self, usuario):
        """
        Caso de uso: listar todas las reservas asociadas a un usuario.
        """
        return self.reserva_repository.listar_por_usuario(usuario)


class CursoService:
    """
    Service Layer para la gestión de cursos y compras.
    Orquesta repositorios y reglas de negocio de cursos.
    """

    def __init__(self):
        self.curso_repository = CursoRepository()
        self.compra_curso_repository = CompraCursoRepository()

    def listar_cursos(self, solo_activos=True):
        """
        Caso de uso: listar todos los cursos (por defecto solo activos).
        """
        return self.curso_repository.listar_cursos(solo_activos=solo_activos)

    def comprar_curso(self, usuario, curso_id):
        """
        Caso de uso: comprar un curso para el usuario.
        - Levanta CursoNoEncontrado si el curso no existe o no está activo.
        - Levanta CursoYaComprado si el usuario ya compró ese curso.
        """
        try:
            curso = self.curso_repository.obtener_por_id(curso_id)
        except Curso.DoesNotExist:
            raise CursoNoEncontrado("El curso no existe.")

        if not curso.activo:
            raise CursoNoEncontrado("El curso no está disponible.")

        if self.compra_curso_repository.existe_compra(usuario, curso):
            raise CursoYaComprado("Ya has comprado este curso.")

        compra = CompraCurso(usuario=usuario, curso=curso)
        self.compra_curso_repository.guardar(compra)
        return compra