# JESurvivor/__init__.py
# Import defensivo de Celery: si el paquete no está instalado
# (contenedor sin rebuild), Django sigue funcionando normalmente.
try:
    from .celery import app as celery_app
    __all__ = ("celery_app",)
except Exception:
    pass