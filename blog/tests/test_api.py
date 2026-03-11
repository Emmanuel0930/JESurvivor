from datetime import date, timedelta

from django.test import TestCase
from rest_framework.test import APIClient

from blog.domain.models import CompraCurso, Curso, KitEspecializado, Producto, ReservaKit, Usuario


class ApiIntegrationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.usuario = Usuario.objects.create(
            nombre="Survivor Uno",
            email="survivor1@example.com",
            contrasena_hash="hash",
            nivel_experiencia=Usuario.NivelExperiencia.INTERMEDIO,
            ubicacion_climatica=Usuario.UbicacionClimatica.TEMPLADO,
        )
        self.kit = KitEspecializado.objects.create(
            nombre="Kit Urbano",
            descripcion="Equipo para escenarios urbanos",
            precio=85,
            tipo=Producto.TipoProducto.KIT,
            nivel_recomendado=Producto.NivelRecomendado.INTERMEDIO,
            stock=4,
            entorno=KitEspecializado.Entorno.URBANO,
            lista_items=["Linterna", "Radio"],
        )
        self.curso = Curso.objects.create(
            nombre="Curso de evacuación",
            descripcion="Aprende a evacuar con seguridad.",
            precio=39,
            nivel_recomendado=Curso.NivelRecomendado.BASICO,
            duracion_horas=6,
            activo=True,
        )

    def _user_headers(self):
        return {"HTTP_X_USER_ID": str(self.usuario.id)}

    def test_usuario_actual_devuelve_usuario_del_dominio(self):
        response = self.client.get("/api/usuario/actual/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"], self.usuario.id)

    def test_listar_kits_expone_datos_para_frontend(self):
        response = self.client.get("/api/kit/")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(len(payload), 1)
        self.assertEqual(payload[0]["nombre"], self.kit.nombre)
        self.assertEqual(payload[0]["lista_items"], self.kit.lista_items)

    def test_comprar_curso_con_usuario_header(self):
        response = self.client.post(
            "/api/curso/comprar/",
            {"curso_id": self.curso.id},
            format="json",
            **self._user_headers(),
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            CompraCurso.objects.filter(usuario=self.usuario, curso=self.curso).exists()
        )

    def test_crear_reserva_con_usuario_header(self):
        inicio = date.today() + timedelta(days=1)
        fin = date.today() + timedelta(days=3)

        response = self.client.post(
            "/api/reserva/crear/",
            {
                "kit_id": self.kit.id,
                "inicio": inicio.isoformat(),
                "fin": fin.isoformat(),
            },
            format="json",
            **self._user_headers(),
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            ReservaKit.objects.filter(
                usuario=self.usuario,
                kit=self.kit,
                fecha_inicio=inicio,
                fecha_fin=fin,
            ).exists()
        )
