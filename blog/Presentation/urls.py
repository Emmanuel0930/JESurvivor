from django.urls import path
from blog.Presentation.views import (
    # Existentes
    CancelarReservaView,
    ComprarCursoView,
    CrearReservaView,
    ListarKitsView,
    ListarCursosView,
    ListarReservasUsuarioView,
    UsuarioActualView,
    VerificarDisponibilidadView,
    # Nuevos — Entregable 2
    SistemaInfoView,
    ClimaSupervivenciaView,
    AliadoView,
    DisparadoReporteView,
)

urlpatterns = [
    # ── Usuario ─────────────────────────────────────────
    path("usuario/actual/", UsuarioActualView.as_view(), name="usuario-actual"),

    # ── Kits y Reservas ─────────────────────────────────
    path("kit/", ListarKitsView.as_view(), name="listar-kits"),
    path("reserva/crear/", CrearReservaView.as_view(), name="crear-reserva"),
    path("reserva/disponibilidad/", VerificarDisponibilidadView.as_view(), name="verificar-disponibilidad"),
    path("reserva/cancelar/", CancelarReservaView.as_view(), name="cancelar-reserva"),
    path("reserva/mis-reservas/", ListarReservasUsuarioView.as_view(), name="listar-reservas-usuario"),

    # ── Cursos ──────────────────────────────────────────
    path("curso/", ListarCursosView.as_view(), name="listar-cursos"),
    path("curso/comprar/", ComprarCursoView.as_view(), name="comprar-curso"),

    # ── Sistema (Entregable 2) ───────────────────────────
    # Endpoint propio expuesto para el equipo aliado
    path("sistema/info/", SistemaInfoView.as_view(), name="sistema-info"),

    # Tarea asíncrona Celery — disparo de reporte en background
    path("tareas/reporte/", DisparadoReporteView.as_view(), name="disparar-reporte"),

    # ── Integraciones externas (Entregable 2) ────────────
    # Adapter Pattern → Open-Meteo (clima por entorno de supervivencia)
    path("clima/", ClimaSupervivenciaView.as_view(), name="clima-supervivencia"),

    # Consumo del servicio del equipo aliado
    path("aliado/", AliadoView.as_view(), name="servicio-aliado"),
]
