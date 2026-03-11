from django.urls import path
from blog.Presentation.views import (
    CancelarReservaView,
    ComprarCursoView,
    CrearReservaView,
    ListarKitsView,
    ListarCursosView,
    ListarReservasUsuarioView,
    UsuarioActualView,
    VerificarDisponibilidadView,
)

urlpatterns = [
    path("usuario/actual/", UsuarioActualView.as_view(), name="usuario-actual"),
    path("kit/", ListarKitsView.as_view(), name="listar-kits"),
    path("reserva/crear/", CrearReservaView.as_view(), name="crear-reserva"),
    path(
        "reserva/disponibilidad/",
        VerificarDisponibilidadView.as_view(),
        name="verificar-disponibilidad",
    ),
    path(
        "reserva/cancelar/",
        CancelarReservaView.as_view(),
        name="cancelar-reserva",
    ),
    path(
        "reserva/mis-reservas/",
        ListarReservasUsuarioView.as_view(),
        name="listar-reservas-usuario",
    ),
    path("curso/", ListarCursosView.as_view(), name="listar-cursos"),
    path("curso/comprar/", ComprarCursoView.as_view(), name="comprar-curso"),
]
