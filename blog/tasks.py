"""
Tareas asíncronas de JESurvivor — Celery + Redis
Requerimiento Entregable 2: Comunicación asíncrona para procesos de fondo.

Flujo:
  View/Service → .delay() → Redis (cola) → Celery Worker → ejecuta tarea
"""

import logging
from celery import shared_task
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger("jesurvivor.tasks")


# ─────────────────────────────────────────────────────────
# TAREA 1: Confirmación de reserva de kit
# Disparada por ReservaService.crear_reserva()
# ─────────────────────────────────────────────────────────

@shared_task(bind=True, max_retries=3, default_retry_delay=60, name="blog.tasks.enviar_confirmacion_reserva")
def enviar_confirmacion_reserva(
    self,
    reserva_id: int,
    usuario_email: str,
    usuario_nombre: str,
    kit_nombre: str,
    fecha_inicio: str,
    fecha_fin: str,
):
    """
    Envía un correo de confirmación cuando el usuario crea una reserva.
    En DEV: imprime en consola. En PROD: usa Django send_mail.
    """
    try:
        logger.info(
            "[CELERY] Procesando confirmación de reserva #%s para %s",
            reserva_id, usuario_email
        )

        import os
        env = os.environ.get("ENV_TYPE", "DEV")

        if env == "PROD":
            from django.core.mail import send_mail
            send_mail(
                subject=f"JESurvivor — Reserva #{reserva_id} confirmada",
                message=(
                    f"Hola {usuario_nombre},\n\n"
                    f"Tu reserva del kit '{kit_nombre}' ha sido registrada correctamente.\n"
                    f"Fechas: {fecha_inicio} al {fecha_fin}\n\n"
                    f"¡Prepárate para sobrevivir!\n— Equipo JESurvivor"
                ),
                from_email="noreply@jesurvivor.com",
                recipient_list=[usuario_email],
                fail_silently=False,
            )
        else:
            logger.info(
                "[CONFIRMACION] Para: %s | Reserva: #%s | Kit: %s | %s → %s",
                usuario_email, reserva_id, kit_nombre, fecha_inicio, fecha_fin,
            )

        return {
            "status": "enviado",
            "reserva_id": reserva_id,
            "destinatario": usuario_email,
        }

    except Exception as exc:
        logger.error("[CELERY] Error enviando confirmación reserva #%s: %s", reserva_id, exc)
        raise self.retry(exc=exc)


# ─────────────────────────────────────────────────────────
# TAREA 2: Notificación de cancelación de reserva
# ─────────────────────────────────────────────────────────

@shared_task(name="blog.tasks.enviar_notificacion_cancelacion")
def enviar_notificacion_cancelacion(
    reserva_id: int,
    usuario_email: str,
    usuario_nombre: str,
    kit_nombre: str,
):
    """Notifica al usuario que su reserva fue cancelada."""
    logger.info(
        "[CELERY] Notificando cancelación reserva #%s a %s",
        reserva_id, usuario_email
    )
    logger.info(
        "[CANCELACION] Para: %s | Kit: %s | Reserva #%s",
        usuario_email, kit_nombre, reserva_id,
    )
    return {"status": "cancelacion_notificada", "reserva_id": reserva_id}


# ─────────────────────────────────────────────────────────
# TAREA 3: Reporte periódico del sistema (Celery Beat)
# Configurado en django-celery-beat para ejecutarse cada hora
# ─────────────────────────────────────────────────────────

@shared_task(name="blog.tasks.generar_reporte_reservas")
def generar_reporte_reservas():
    """
    Genera un reporte de reservas del sistema.
    Esta tarea es periódica — se programa desde el panel de Celery Beat.
    """
    from blog.domain.models import ReservaKit, Usuario, KitEspecializado, Curso

    total_reservas = ReservaKit.objects.count()
    pendientes = ReservaKit.objects.filter(estado="pendiente").count()
    confirmadas = ReservaKit.objects.filter(estado="confirmada").count()
    canceladas = ReservaKit.objects.filter(estado="cancelada").count()
    finalizadas = ReservaKit.objects.filter(estado="finalizada").count()

    reporte = {
        "total_usuarios": Usuario.objects.count(),
        "total_kits": KitEspecializado.objects.count(),
        "total_cursos": Curso.objects.filter(activo=True).count(),
        "reservas": {
            "total": total_reservas,
            "pendientes": pendientes,
            "confirmadas": confirmadas,
            "canceladas": canceladas,
            "finalizadas": finalizadas,
        },
    }

    logger.info("[REPORTE SISTEMA] %s", reporte)
    return reporte


# ─────────────────────────────────────────────────────────
# TAREA 4: Limpieza de reservas vencidas (Celery Beat)
# Marca como FINALIZADA las reservas cuya fecha_fin ya pasó
# ─────────────────────────────────────────────────────────

@shared_task(name="blog.tasks.finalizar_reservas_vencidas")
def finalizar_reservas_vencidas():
    """
    Tarea periódica: finaliza reservas confirmadas cuya fecha_fin ya pasó.
    Debe ejecutarse diariamente.
    """
    from django.utils import timezone
    from blog.domain.models import ReservaKit

    hoy = timezone.now().date()
    vencidas = ReservaKit.objects.filter(
        estado=ReservaKit.EstadoReserva.CONFIRMADA,
        fecha_fin__lt=hoy,
    )
    count = vencidas.update(estado=ReservaKit.EstadoReserva.FINALIZADA)
    logger.info("[CELERY] %s reservas finalizadas automáticamente.", count)
    return {"finalizadas": count}
