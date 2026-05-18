"""
Configuración de Celery para JESurvivor.
Message Broker: Redis
Comunicación asíncrona para notificaciones y reportes.
"""

import os
from celery import Celery

# Apunta al módulo de settings de Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "JESurvivor.settings")

app = Celery("JESurvivor")

# Usa el prefijo CELERY_ en settings.py para configurar Celery
app.config_from_object("django.conf:settings", namespace="CELERY")

# Descubre tareas automáticamente en todos los INSTALLED_APPS
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
