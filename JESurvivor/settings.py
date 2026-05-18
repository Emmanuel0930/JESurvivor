"""
Django settings for JESurvivor project — Entregable 2.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-051rcf3g-**t#lc$(u726#2f3@v@8i!osf+mv3-#&pdt#3bv56",
)

DEBUG = os.environ.get("DJANGO_DEBUG", "True") == "True"

ALLOWED_HOSTS_ENV = os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1")
ALLOWED_HOSTS = [h.strip() for h in ALLOWED_HOSTS_ENV.split(",")]

# ── Detectar si Celery/Beat están disponibles (instalados) ──────────────────
def _pkg_available(name):
    import importlib.util
    return importlib.util.find_spec(name) is not None

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "drf_spectacular",
    "blog",
]

# Agrega django_celery_beat solo si está instalado
if _pkg_available("django_celery_beat"):
    INSTALLED_APPS.append("django_celery_beat")

if _pkg_available("django_celery_results"):
    INSTALLED_APPS.append("django_celery_results")

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "JESurvivor API",
    "DESCRIPTION": (
        "API RESTful de JESurvivor — Plataforma de supervivencia. "
        "Reservas de kits, cursos e integración con servicios externos."
    ),
    "VERSION": "2.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "JESurvivor.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.i18n",
            ],
        },
    },
]

WSGI_APPLICATION = "JESurvivor.wsgi.application"

# ── Base de datos ────────────────────────────────────────────────────────────
if os.environ.get("DB_HOST"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get("DB_NAME", "jesurvivor"),
            "USER": os.environ.get("DB_USER", "postgres"),
            "PASSWORD": os.environ.get("DB_PASS", "postgres"),
            "HOST": os.environ.get("DB_HOST", "localhost"),
            "PORT": os.environ.get("DB_PORT", "5432"),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ── i18n ─────────────────────────────────────────────────────────────────────
LANGUAGE_CODE = "es"
LANGUAGES = [
    ("es", "Español"),
    ("en", "English"),
]
TIME_ZONE = "America/Bogota"
USE_I18N = True
USE_L10N = True
USE_TZ = True

LOCALE_PATHS = [
    BASE_DIR / "blog" / "locale",
]

STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
CORS_ALLOW_ALL_ORIGINS = True

# ── Celery + Redis (solo se activa si celery está instalado) ─────────────────
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://redis:6379/0")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "redis://redis:6379/0")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "America/Bogota"

# ── Email (DEV: solo consola) ─────────────────────────────────────────────────
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "noreply@jesurvivor.com"
ENV_TYPE = os.environ.get("ENV_TYPE", "DEV")

# ── URL del equipo aliado ─────────────────────────────────────────────────────
ALIADO_API_URL = os.environ.get("ALIADO_API_URL", "http://ALIADO_IP/api/info/")