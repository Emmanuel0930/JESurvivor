import logging
import os

logger = logging.getLogger("jesurvivor.notificaciones")


class EmailNotifier:
    def enviar_confirmacion(self, reserva):
        from django.core.mail import send_mail

        send_mail(
            subject=f"JESurvivor — Reserva #{reserva.id} confirmada",
            message=(
                f"Tu reserva del kit '{reserva.kit.nombre}' "
                f"({reserva.fecha_inicio} → {reserva.fecha_fin}) fue registrada."
            ),
            from_email="noreply@jesurvivor.com",
            recipient_list=[reserva.usuario.email],
            fail_silently=False,
        )
        logger.info("Email de confirmación enviado para reserva #%s", reserva.id)


class LoggingNotifier:
    """Confirmación síncrona cuando Celery no está disponible."""

    def enviar_confirmacion(self, reserva):
        logger.info(
            "Reserva #%s creada en BD — kit '%s', %s → %s",
            reserva.id,
            reserva.kit.nombre,
            reserva.fecha_inicio,
            reserva.fecha_fin,
        )


class NotificadorFactory:

    @staticmethod
    def crear():
        if os.getenv("ENV_TYPE", "DEV") == "PROD":
            return EmailNotifier()
        return LoggingNotifier()
