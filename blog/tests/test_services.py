from datetime import date, timedelta

from django.test import TestCase

from blog.domain.models import Usuario, KitEspecializado, Producto, ReservaKit
from blog.Application.services import (
    ReservaService,
    KitNoDisponible,
    ReservaNoCancelable,
    ReservaNoEncontrada,
)


class ReservaServiceTests(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create(
            nombre="Juan",
            email="juan@example.com",
            contrasena_hash="hash",
            nivel_experiencia=Usuario.NivelExperiencia.INTERMEDIO,
            ubicacion_climatica=Usuario.UbicacionClimatica.TEMPLADO,
        )
        self.kit = KitEspecializado.objects.create(
            nombre="Kit montaña",
            descripcion="Kit para montaña",
            precio=100,
            tipo=Producto.TipoProducto.KIT,
            nivel_recomendado=Producto.NivelRecomendado.INTERMEDIO,
            stock=5,
            entorno=KitEspecializado.Entorno.MONTANA,
        )
        self.service = ReservaService()

    def _rango_fechas(self):
        inicio = date.today() + timedelta(days=1)
        fin = date.today() + timedelta(days=3)
        return inicio, fin

    def test_crear_reserva_exito(self):
        inicio, fin = self._rango_fechas()

        reserva = self.service.crear_reserva(
            usuario=self.usuario,
            kit_id=self.kit.id,
            fecha_inicio=inicio,
            fecha_fin=fin,
        )

        self.assertIsInstance(reserva, ReservaKit)
        self.assertEqual(reserva.usuario, self.usuario)
        self.assertEqual(reserva.kit, self.kit)

    def test_crear_reserva_kit_no_disponible(self):
        inicio, fin = self._rango_fechas()
        # Crear una reserva previa que solape
        ReservaKit.objects.create(
            usuario=self.usuario,
            kit=self.kit,
            fecha_inicio=inicio,
            fecha_fin=fin,
            estado=ReservaKit.EstadoReserva.PENDIENTE,
        )

        with self.assertRaises(KitNoDisponible):
            self.service.crear_reserva(
                usuario=self.usuario,
                kit_id=self.kit.id,
                fecha_inicio=inicio,
                fecha_fin=fin,
            )

    def test_verificar_disponibilidad_conflicto(self):
        inicio, fin = self._rango_fechas()
        ReservaKit.objects.create(
            usuario=self.usuario,
            kit=self.kit,
            fecha_inicio=inicio,
            fecha_fin=fin,
            estado=ReservaKit.EstadoReserva.PENDIENTE,
        )

        with self.assertRaises(KitNoDisponible):
            self.service.verificar_disponibilidad(self.kit.id, inicio, fin)

    def test_cancelar_reserva_exito(self):
        inicio, fin = self._rango_fechas()
        reserva = ReservaKit.objects.create(
            usuario=self.usuario,
            kit=self.kit,
            fecha_inicio=inicio,
            fecha_fin=fin,
            estado=ReservaKit.EstadoReserva.PENDIENTE,
        )

        reserva_cancelada = self.service.cancelar_reserva(self.usuario, reserva.id)

        self.assertEqual(
            reserva_cancelada.estado, ReservaKit.EstadoReserva.CANCELADA
        )

    def test_cancelar_reserva_no_pendiente(self):
        inicio, fin = self._rango_fechas()
        reserva = ReservaKit.objects.create(
            usuario=self.usuario,
            kit=self.kit,
            fecha_inicio=inicio,
            fecha_fin=fin,
            estado=ReservaKit.EstadoReserva.CONFIRMADA,
        )

        with self.assertRaises(ReservaNoCancelable):
            self.service.cancelar_reserva(self.usuario, reserva.id)

    def test_cancelar_reserva_de_otro_usuario(self):
        inicio, fin = self._rango_fechas()
        otro_usuario = Usuario.objects.create(
            nombre="Ana",
            email="ana@example.com",
            contrasena_hash="hash2",
            nivel_experiencia=Usuario.NivelExperiencia.INTERMEDIO,
            ubicacion_climatica=Usuario.UbicacionClimatica.TEMPLADO,
        )
        reserva = ReservaKit.objects.create(
            usuario=otro_usuario,
            kit=self.kit,
            fecha_inicio=inicio,
            fecha_fin=fin,
            estado=ReservaKit.EstadoReserva.PENDIENTE,
        )

        with self.assertRaises(ReservaNoEncontrada):
            self.service.cancelar_reserva(self.usuario, reserva.id)

    def test_listar_reservas_de_usuario(self):
        inicio, fin = self._rango_fechas()
        ReservaKit.objects.create(
            usuario=self.usuario,
            kit=self.kit,
            fecha_inicio=inicio,
            fecha_fin=fin,
            estado=ReservaKit.EstadoReserva.PENDIENTE,
        )

        reservas = self.service.listar_reservas_de_usuario(self.usuario)
        self.assertEqual(reservas.count(), 1)

