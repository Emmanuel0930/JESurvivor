# Tests de la app blog: Service Layer (ReservaService, CursoService), etc.
# Ejecutar: python manage.py test blog

from blog.tests.test_services import ReservaServiceTests  # noqa: F401

__all__ = ["ReservaServiceTests"]
