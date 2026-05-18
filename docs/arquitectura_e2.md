# Arquitectura JESurvivor — Entregable 2

## Diagrama General (AWS + Microservicios + Broker)

```mermaid
graph TD
    subgraph INTERNET["🌐 Internet"]
        Cliente["🖥️ Browser / Cliente"]
    end

    subgraph AWS["☁️ AWS Academy — EC2 (Ubuntu 22.04)"]
        subgraph DOCKER["🐳 Docker Compose"]
            Nginx["⚙️ Nginx :80\nAPI Gateway\n(Patrón Estrangulador)"]

            subgraph SERVICIOS["Servicios"]
                Django["🦄 Django :8000\nMonolito Legacy\n(API v1)"]
                Flask["🐍 Flask :5000\nMicroservicio Reservas\n(API v2 — Estrangulado)"]
                CeleryW["⚙️ Celery Worker\nTareas Asíncronas\n(Notificaciones / Reportes)"]
                CeleryB["🕐 Celery Beat\nTareas Periódicas\n(Limpieza / Reportes)"]
            end

            subgraph DATOS["Persistencia"]
                PG[("🐘 PostgreSQL :5432\nBD Compartida")]
                Redis[("🔴 Redis :6379\nMessage Broker")]
            end
        end
    end

    subgraph TERCEROS["🌍 APIs Externas"]
        OpenMeteo["🌤️ Open-Meteo API\n(Clima gratuito — Adapter Pattern)"]
        Aliado["🤝 Equipo Aliado\n(IP EC2 a configurar)"]
    end

    Cliente -->|"HTTP :80"| Nginx
    Nginx -->|"/api/v2/reservas/*"| Flask
    Nginx -->|"/* resto"| Django

    Django -->|"ORM"| PG
    Flask -->|"psycopg2"| PG
    CeleryW -->|"ORM"| PG
    CeleryB -->|"ORM"| PG

    Django -->|"encola tareas"| Redis
    Flask -->|"encola eventos"| Redis
    Redis -->|"consume tareas"| CeleryW
    Redis -->|"dispara periódicas"| CeleryB

    Django -->|"Adapter Pattern"| OpenMeteo
    Django -->|"HTTP GET"| Aliado
```

## Tabla de Rutas — API Gateway (Nginx)

| Ruta | Destino | Descripción |
|------|---------|-------------|
| `/api/v2/reservas/*` | Flask :5000 | Microservicio estrangulado |
| `/api/sistema/info/` | Django :8000 | Info expuesta al aliado |
| `/api/clima/` | Django :8000 | Adapter → Open-Meteo |
| `/api/aliado/` | Django :8000 | Consumo del equipo aliado |
| `/api/tareas/reporte/` | Django :8000 | Disparador Celery |
| `/api/docs/` | Django :8000 | Swagger UI |
| `/*` | Django :8000 | Frontend SPA |

## Patrón Adapter — Flujo

```mermaid
sequenceDiagram
    participant V as Vista Django
    participant S as ClimaService
    participant A as IClimaAdapter (Puerto)
    participant O as OpenMeteoAdapter
    participant API as Open-Meteo API

    V->>S: obtener_clima_para_entorno("montana")
    S->>A: obtener_clima_actual(lat, lon)
    A->>O: (implementación concreta)
    O->>API: GET /v1/forecast?latitude=...
    API-->>O: JSON {temperature, wind, ...}
    O-->>A: dict normalizado
    A-->>S: {temperatura_c, viento_kmh, ...}
    S-->>V: {entorno, clima, recomendacion_kit}
```

## Flujo Asíncrono — Celery + Redis

```mermaid
sequenceDiagram
    participant C as Cliente HTTP
    participant V as Vista Django
    participant S as ReservaService
    participant R as Redis (Broker)
    participant W as Celery Worker

    C->>V: POST /api/reserva/crear/
    V->>S: crear_reserva(datos)
    S->>S: ReservaKitBuilder.build()
    S->>S: guardar en PostgreSQL
    S->>R: enviar_confirmacion_reserva.delay(...)
    S-->>V: reserva creada
    V-->>C: 201 Created (INMEDIATO)
    Note over C,V: El cliente no espera el email

    R->>W: despacha tarea
    W->>W: envía email / loguea
    W-->>R: ACK tarea completada
```

## Componentes del Entregable 2

| Componente | Archivo | Patrón / Tecnología |
|-----------|---------|---------------------|
| Message Broker | `docker-compose.yml` → redis | Redis |
| Worker asíncrono | `blog/tasks.py` | Celery |
| Tareas periódicas | Celery Beat + django-celery-beat | Cron en BD |
| Adapter clima | `blog/Application/adapters.py` | Adapter + DIP |
| API propia expuesta | `GET /api/sistema/info/` | REST JSON |
| Consumo aliado | `GET /api/aliado/` | HTTP + fallback |
| i18n | `blog/locale/es,en` | gettext |
| API Gateway | `nginx/nginx.conf` | Reverse proxy |
| Infra | `docker-compose.yml` | Docker Compose en EC2 |
