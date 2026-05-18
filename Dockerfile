FROM python:3.12-slim

WORKDIR /app

# Dependencias del sistema para psycopg2 y compilación
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc \
    gettext \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Compilar archivos de traducción (.po → .mo)
RUN python manage.py compilemessages || true

EXPOSE 8000

# Comando por defecto: Django + seed
# El Celery worker usa su propio comando en docker-compose
CMD ["sh", "-c", \
     "python manage.py migrate && \
      python manage.py seed_mock_data --kits 5 --usuarios 3 && \
      gunicorn JESurvivor.wsgi:application --bind 0.0.0.0:8000 --workers 2"]
