# JESurvivor - Guía de Ejecución

Este proyecto es una aplicación web construida con **Django** y **Django Rest Framework**, que incluye documentación interactiva con **Swagger**.

## Requisitos Previos

- Python 3.10 o superior
- Pip (gestor de paquetes de Python)

## Instalación y Configuración

Sigue estos pasos para configurar el proyecto en tu entorno local:

### 1. Clonar el repositorio
Si aún no lo tienes localmente:
```bash
git clone https://github.com/Emmanuel0930/JESurvivor.git
cd JESurvivor
```

### 2. Crear un entorno virtual
Es recomendable usar un entorno virtual para aislar las dependencias:
```bash
# En macOS/Linux
python3 -m venv venv

# En Windows
python -m venv venv
```

### 3. Activar el entorno virtual
```bash
# En macOS/Linux
source venv/bin/activate

# En Windows
venv\Scripts\activate
```

### 4. Instalar dependencias
Instala todos los paquetes necesarios listados en el archivo `requirements.txt`:
```bash
pip install -r requirements.txt
```

### 5. Configurar la base de datos
Ejecuta las migraciones para crear las tablas necesarias en la base de datos local (SQLite):
```bash
python manage.py migrate
```

## Ejecución del Proyecto

Para iniciar el servidor de desarrollo, asegúrate de tener el entorno virtual activado y ejecuta:

```bash
python manage.py runserver
```

El servidor estará disponible en: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

## Documentación de la API (Swagger)

Una vez que el servidor esté corriendo, puedes acceder a la documentación interactiva de los endpoints en:

- **Swagger UI:** [http://127.0.0.1:8000/api/docs/](http://127.0.0.1:8000/api/docs/)
- **Redoc:** [http://127.0.0.1:8000/api/redoc/](http://127.0.0.1:8000/api/redoc/)

## Notas Adicionales
- El archivo `.gitignore` está configurado para no subir el entorno virtual (`venv/`), la base de datos local (`db.sqlite3`) ni archivos temporales.
- Si agregas nuevas dependencias, recuerda actualizar el archivo de requerimientos con `pip freeze > requirements.txt`.
