# 🪓 JESurvivor

> Plataforma web de supervivencia outdoor — reservas de kits especializados, cursos, foro de comunidad y panel de integraciones en tiempo real.

[![Django](https://img.shields.io/badge/Django-5.0-green?style=flat-square&logo=django)](https://djangoproject.com)
[![DRF](https://img.shields.io/badge/DRF-3.16-red?style=flat-square)](https://www.django-rest-framework.org)
[![Flask](https://img.shields.io/badge/Flask-3-black?style=flat-square&logo=flask)](https://flask.palletsprojects.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue?style=flat-square&logo=postgresql)](https://postgresql.org)
[![Redis](https://img.shields.io/badge/Redis-7-red?style=flat-square&logo=redis)](https://redis.io)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue?style=flat-square&logo=docker)](https://docker.com)

---

## Tabla de contenidos

- [¿Qué es JESurvivor?](#qué-es-jesurvivor)
- [Arquitectura del sistema](#arquitectura-del-sistema)
- [Tecnologías y patrones de diseño](#tecnologías-y-patrones-de-diseño)
- [Estructura del repositorio](#estructura-del-repositorio)
- [Requisitos previos](#requisitos-previos)
- [Instalación y ejecución local](#instalación-y-ejecución-local)
- [Variables de entorno](#variables-de-entorno)
- [Endpoints de la API](#endpoints-de-la-api)
- [Integraciones externas (APIs de terceros)](#integraciones-externas-apis-de-terceros)
- [Frontend SPA](#frontend-spa)
- [Despliegue en AWS EC2](#despliegue-en-aws-ec2)
- [Datos de prueba](#datos-de-prueba)
- [Documentación interactiva](#documentación-interactiva)

---

## ¿Qué es JESurvivor?

JESurvivor es una aplicación full-stack orientada a la comunidad de supervivencia y outdoor. Permite a los usuarios:

- **Reservar kits especializados** de supervivencia (montaña, selva, urbano, desierto, nieve)
- **Comprar y acceder a cursos** de técnicas outdoor
- **Participar en un foro** de la comunidad con sistema de posts y tags
- **Consultar el clima en tiempo real** por entorno de supervivencia con recomendación de kit
- **Explorar una biblioteca** de libros de supervivencia obtenida en tiempo real desde Open Library
- **Gestionar suscripciones** premium
- **Disparar tareas asíncronas** (reportes del sistema procesados en background)

---

## Arquitectura del sistema

```
Cliente (Browser)
       │
       ▼
┌─────────────────────────────┐
│   Nginx :80  (API Gateway)  │   ← IP Elástica AWS / localhost
│   Patrón: Strangler Fig     │
└─────────┬──────────┬────────┘
          │          │
   /api/v2/reservas/*  todo lo demás
          │          │
          ▼          ▼
  ┌─────────────┐  ┌──────────────────┐
  │ Flask :5000 │  │  Django :8000    │
  │ Microserv.  │  │  Monolito + DRF  │
  │  Reservas   │  │  + Celery Worker │
  └──────┬──────┘  └───────┬──────────┘
         │                 │
         └────────┬────────┘
                  │
         ┌────────▼────────┐
         │  PostgreSQL :5432│
         │  (BD compartida) │
         └─────────────────┘

         ┌─────────────────┐
         │   Redis :6379   │  ← Broker de tareas async (Celery)
         └─────────────────┘
```

### Decisiones de arquitectura

| Componente | Patrón aplicado | Razón |
|---|---|---|
| **Nginx** | API Gateway / Strangler Fig | Enruta sin que el cliente sepa qué backend responde |
| **Flask** | Microservicio estrangulado | Módulo de reservas extraído del monolito como demostración |
| **Django** | Monolito estructurado por capas | Domain → Application → Infrastructure → Presentation |
| **Celery + Redis** | Message Broker / Worker asíncrono | Tareas de larga duración sin bloquear el servidor HTTP |
| **Adapters** | Adapter Pattern + DIP | Las APIs externas se consumen detrás de una interfaz abstracta; cambiar proveedor no modifica la lógica de negocio |

---

## Tecnologías y patrones de diseño

### Stack técnico

| Capa | Tecnología |
|---|---|
| Backend principal | Django 5.0 + Django REST Framework 3.16 |
| Microservicio | Flask 3 |
| Base de datos | PostgreSQL 16 |
| Broker async | Redis 7 + Celery 5.3 |
| API Gateway | Nginx 1.27 |
| Documentación API | drf-spectacular (OpenAPI 3 / Swagger) |
| Frontend | Vanilla JS (SPA sin framework) |
| Contenedores | Docker + Docker Compose |
| Infra | AWS EC2 + IP Elástica |

### Patrones de diseño implementados

- **Adapter Pattern** — `IClimaAdapter` / `IBibliotecaAdapter`: las APIs externas (Open-Meteo, Open Library) son consumidas a través de interfaces abstractas. Cambiar de proveedor requiere solo un nuevo adaptador concreto, sin tocar servicios ni vistas.
- **Dependency Inversion Principle (DIP)** — `ClimaService` y `BibliotecaService` dependen de la abstracción, nunca de la implementación concreta.
- **Repository Pattern** — `Infrastructure/repositories.py` centraliza el acceso a datos.
- **Builder Pattern** — `domain/builders.py` para construcción de entidades complejas.
- **Factory Pattern** — `Application/Factories.py` para creación desacoplada de objetos.
- **Strangler Fig Pattern** — El microservicio Flask reemplaza gradualmente el módulo de reservas del monolito Django sin interrupciones.

---

## Estructura del repositorio

```
JESurvivor/
├── blog/                          # App principal Django
│   ├── Application/
│   │   ├── adapters.py            # Adapter Pattern: Open-Meteo + Open Library
│   │   ├── Factories.py
│   │   └── services.py            # Lógica de negocio
│   ├── domain/
│   │   ├── models.py              # Modelos Django (ORM)
│   │   ├── builders.py
│   │   ├── entities.py
│   │   └── validators.py
│   ├── Infrastructure/
│   │   └── repositories.py        # Acceso a datos
│   ├── Presentation/
│   │   ├── views.py               # Vistas DRF (endpoints)
│   │   ├── urls.py                # Rutas de la API
│   │   └── serializers.py
│   └── management/commands/
│       └── seed_mock_data.py      # Carga de datos de prueba
│
├── flask_reservas/                # Microservicio Flask (Strangler)
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── Frontend/                      # SPA Vanilla JS
│   ├── index.html
│   ├── app.js                     # Router SPA
│   ├── styles.css
│   ├── api/api.js                 # Capa de comunicación con el backend
│   ├── components/                # Componentes reutilizables
│   └── pages/
│       ├── integrationPage.js     # Panel de integraciones en tiempo real
│       ├── coursesPage.js
│       ├── forumPage.js
│       ├── storePage.js
│       └── subscriptionPage.js
│
├── JESurvivor/                    # Configuración Django
│   ├── settings.py
│   ├── urls.py
│   └── celery.py
│
├── nginx/
│   └── nginx.conf                 # Configuración del API Gateway
│
├── docs/
│   ├── arquitectura_e2.md
│   └── service_layer.md
│
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

---

## Requisitos previos

- [Docker](https://docs.docker.com/get-docker/) ≥ 24
- [Docker Compose](https://docs.docker.com/compose/install/) ≥ 2.20
- Git

> **No necesitas** Python, PostgreSQL ni Redis instalados localmente. Docker lo gestiona todo.

---

## Instalación y ejecución local

### 1. Clonar el repositorio

```bash
git clone https://github.com/Emmanuel0930/JESurvivor.git
cd JESurvivor
```

### 2. Levantar todos los servicios

```bash
docker compose up --build -d
```

Esto levanta 6 contenedores: `nginx`, `django`, `flask_reservas`, `celery_worker`, `celery_beat` y `db` (PostgreSQL) + `redis`.

### 3. Aplicar migraciones y cargar datos de prueba

```bash
# Migraciones de base de datos
docker compose exec django python manage.py migrate

# Cargar datos de prueba (usuarios, kits, cursos, posts)
docker compose exec django python manage.py seed_mock_data
```

### 4. Acceder a la aplicación

| Servicio | URL |
|---|---|
| **Aplicación web** | http://localhost |
| **Swagger UI** | http://localhost/api/docs/ |
| **ReDoc** | http://localhost/api/redoc/ |
| **Admin Django** | http://localhost/admin/ |

### Comandos útiles

```bash
# Ver logs de todos los servicios
docker compose logs -f

# Ver logs de un servicio específico
docker compose logs -f django
docker compose logs -f celery_worker

# Detener todos los servicios
docker compose down

# Detener y eliminar volúmenes (borra la BD)
docker compose down -v

# Reiniciar un solo servicio tras cambios
docker compose up -d --build django

# Ver estado de los contenedores
docker compose ps
```

---

## Variables de entorno

Las variables se configuran en `docker-compose.yml` bajo cada servicio. Las más relevantes:

| Variable | Valor por defecto | Descripción |
|---|---|---|
| `DJANGO_SECRET_KEY` | `django-insecure-...` | Clave secreta Django (cambiar en producción) |
| `DJANGO_DEBUG` | `True` | Modo debug (poner `False` en producción) |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1,...` | Hosts permitidos (agregar IP/dominio en producción) |
| `DB_HOST` | `db` | Host de PostgreSQL (nombre del servicio Docker) |
| `DB_NAME` | `jesurvivor` | Nombre de la base de datos |
| `DB_USER` | `postgres` | Usuario de PostgreSQL |
| `DB_PASS` | `postgres` | Contraseña de PostgreSQL |
| `CELERY_BROKER_URL` | `redis://redis:6379/0` | URL del broker Redis para Celery |
| `ALIADO_API_URL` | `http://ALIADO_IP:PORT/api/info/` | URL del equipo aliado (reemplazar con IP real) |

---

## Endpoints de la API

La URL base de todos los endpoints es `/api/`. La documentación completa e interactiva está en `/api/docs/`.

### Usuario

| Método | Endpoint | Descripción |
|---|---|---|
| `GET` | `/api/usuario/actual/` | Obtiene el usuario activo del dominio |

### Kits y Reservas (Django — API v1)

| Método | Endpoint | Descripción |
|---|---|---|
| `GET` | `/api/kit/` | Lista todos los kits de supervivencia disponibles |
| `POST` | `/api/reserva/crear/` | Crea una nueva reserva de kit |
| `POST` | `/api/reserva/disponibilidad/` | Verifica disponibilidad en un rango de fechas |
| `POST` | `/api/reserva/cancelar/` | Cancela una reserva pendiente |
| `GET` | `/api/reserva/mis-reservas/` | Lista reservas del usuario actual |

### Reservas (Flask — API v2, Microservicio)

| Método | Endpoint | Descripción |
|---|---|---|
| `GET` | `/api/v2/reservas/health` | Health check del microservicio Flask |
| `GET` | `/api/v2/reservas/` | Lista reservas (microservicio estrangulado) |

### Cursos

| Método | Endpoint | Descripción |
|---|---|---|
| `GET` | `/api/curso/` | Lista cursos activos |
| `POST` | `/api/curso/comprar/` | Compra un curso para el usuario actual |

### Foro

| Método | Endpoint | Descripción |
|---|---|---|
| `GET` | `/api/posts/` | Lista posts del foro |
| `POST` | `/api/posts/crear/` | Crea un nuevo post |

### Sistema

| Método | Endpoint | Descripción |
|---|---|---|
| `GET` | `/api/sistema/info/` | Estadísticas y arquitectura del sistema |
| `POST` | `/api/tareas/reporte/` | Dispara generación de reporte (async, Celery) |
| `GET` | `/api/tareas/estado/<task_id>/` | Consulta estado de una tarea Celery |

### Integraciones externas (Adapter Pattern)

| Método | Endpoint | Descripción | API tercero |
|---|---|---|---|
| `GET` | `/api/clima/?entorno=X` | Clima actual + kit recomendado por entorno | Open-Meteo |
| `GET` | `/api/biblioteca/?tema=X` | Libros de supervivencia por tema | Open Library |
| `GET` | `/api/aliado/` | Servicio del equipo aliado (graceful si no disponible) | Equipo 9 |

**Entornos válidos para `/api/clima/`:** `urbano`, `montana`, `selva`, `desierto`, `nieve`

**Temas válidos para `/api/biblioteca/`:** `supervivencia`, `primeros_auxilios`, `navegacion`, `refugio`, `agua`, `plantas`

---

## Integraciones externas (APIs de terceros)

JESurvivor implementa el **Adapter Pattern** para consumir APIs de terceros, siguiendo el Principio de Inversión de Dependencias (DIP).

### Open-Meteo — Clima de supervivencia

- **URL:** https://open-meteo.com/
- **Autenticación:** Ninguna (gratuita, sin API key)
- **Uso:** Clima en tiempo real por coordenadas → recomendación de kit de supervivencia
- **Adaptador:** `OpenMeteoAdapter` implementa `IClimaAdapter`
- **Coordenadas incluidas:** Medellín, Cordillera Central, Amazonía, La Guajira, Nevado del Ruiz

### Open Library — Biblioteca de supervivencia

- **URL:** https://openlibrary.org/
- **Autenticación:** Ninguna (gratuita, sin API key)
- **Uso:** Catálogo de libros de supervivencia, primeros auxilios, navegación, refugio, agua y plantas
- **Adaptador:** `OpenLibraryAdapter` implementa `IBibliotecaAdapter`

### Extensibilidad

Para agregar un nuevo proveedor (ej. OpenWeatherMap), solo se necesita:

```python
class OpenWeatherMapAdapter(IClimaAdapter):
    def obtener_clima_actual(self, lat, lon): ...
    def obtener_nombre_proveedor(self): return "OpenWeatherMap"
```

Sin tocar `ClimaService`, `views.py` ni ninguna otra capa.

---

## Frontend SPA

El frontend es una Single Page Application escrita en Vanilla JS (sin React, sin Vue). Nginx lo sirve junto al backend.

### Navegación

| Página | Descripción |
|---|---|
| **Inicio / Tienda** | Catálogo de kits con carrito de compras |
| **Cursos** | Cursos de supervivencia disponibles y comprables |
| **Foro** | Posts de la comunidad con tags y likes |
| **Integraciones** | Panel en tiempo real: clima, biblioteca, estado del sistema, tarea asíncrona Celery |
| **Suscripciones** | Planes premium de la plataforma |

### Estructura de comunicación

```
integrationPage.js
    └── api/api.js          ← todas las llamadas HTTP centralizadas aquí
            └── /api/*      ← Django vía Nginx
            └── /api/v2/*   ← Flask vía Nginx
```

---

## Despliegue en AWS EC2

### Requisitos de la instancia

- **AMI:** Ubuntu 22.04 LTS
- **Tipo:** `t2.medium` o superior recomendado
- **Almacenamiento:** ≥ 20 GB
- **Security Group:** puertos `80` (HTTP) y `22` (SSH) abiertos
- **IP Elástica:** asignada a la instancia

### Proceso de deploy (actualización)

```bash
# 1. Conectarse a la instancia
ssh -i tu-key.pem ubuntu@<IP_ELASTICA>

# 2. Ir al directorio del proyecto
cd JESurvivor

# 3. Traer los últimos cambios del repositorio
git pull origin main

# 4. Reconstruir imágenes y reiniciar contenedores
docker compose up --build -d

# 5. Aplicar nuevas migraciones (si las hay)
docker compose exec django python manage.py migrate

# 6. Verificar que todo esté corriendo
docker compose ps
```

### Primera instalación en EC2

```bash
# Instalar Docker
sudo apt-get update
sudo apt-get install -y docker.io docker-compose-plugin
sudo usermod -aG docker ubuntu
newgrp docker

# Clonar el repositorio
git clone https://github.com/Emmanuel0930/JESurvivor.git
cd JESurvivor

# Levantar
docker compose up --build -d
docker compose exec django python manage.py migrate
docker compose exec django python manage.py seed_mock_data
```

### Acceso desde internet

Una vez levantado, la aplicación es accesible en:

```
http://<IP_ELASTICA>/          ← Aplicación web
http://<IP_ELASTICA>/api/docs/ ← Swagger UI
```

---

## Datos de prueba

El comando `seed_mock_data` carga automáticamente:

- 5 usuarios con diferentes niveles de experiencia
- 8 kits especializados (montaña, selva, urbano, etc.) con stock
- 6 cursos activos de supervivencia
- 10 posts en el foro con tags variados
- Reservas de ejemplo en distintos estados

```bash
docker compose exec django python manage.py seed_mock_data
```

---

## Documentación interactiva

| Herramienta | URL | Descripción |
|---|---|---|
| **Swagger UI** | `/api/docs/` | Explorar y probar todos los endpoints en el navegador |
| **ReDoc** | `/api/redoc/` | Documentación en formato legible |
| **OpenAPI Schema** | `/api/schema/` | Esquema JSON crudo (para importar en Postman, Insomnia, etc.) |

---

## Equipo

Proyecto desarrollado como parte del curso de Ingeniería de Software — **Equipo JESurvivor**.