## Parte B — Service Layer + Factory (Backend JESurvivor)

### 1. Objetivo de la Parte B

Implementar la **capa de servicios (Service Layer)** y el **Factory Pattern** para el dominio de JESurvivor, concentrando la lógica de negocio fuera de las views/serializers y exponiéndola a través de una API limpia que pueda ser consumida por el frontend.

El Service Layer se encarga de:

- Orquestar modelos de dominio, validadores, builders y repositorios.
- Implementar casos de uso claros (reservar kits, comprar cursos, listar datos).
- Manejar errores de dominio con excepciones específicas (para mapear a HTTP en la capa de presentación).

---

### 2. Clases principales del Service Layer

#### 2.1. `ReservaService` (`blog/Application/services.py`)

Casos de uso implementados:

- **`crear_reserva(usuario, kit_id, fecha_inicio, fecha_fin)`**
  - Obtiene el kit (`KitRepository`).
  - Verifica solapamiento de fechas (`ReservaRepository.existe_solapamiento`).
  - Si hay conflicto, lanza **`KitNoDisponible`**.
  - Usa `ReservaKitBuilder` para construir la reserva (validaciones de dominio incluidas).
  - Guarda la reserva (`ReservaRepository.guardar`) y envía confirmación por notificador (`NotificadorFactory`).

- **`verificar_disponibilidad(kit_id, fecha_inicio, fecha_fin)`**
  - Comprueba si ya existe una reserva solapada para el kit en esas fechas.
  - Si hay conflicto, lanza **`KitNoDisponible`**; si no, el kit está disponible.

- **`cancelar_reserva(usuario, reserva_id)`**
  - Obtiene la reserva (`ReservaRepository.obtener_por_id`).
  - Valida que la reserva pertenezca al usuario, si no lanza **`ReservaNoEncontrada`**.
  - Valida que esté en estado `PENDIENTE`, si no lanza **`ReservaNoCancelable`**.
  - Actualiza el estado a `CANCELADA` y persiste.

- **`listar_reservas_de_usuario(usuario)`**
  - Devuelve todas las reservas del usuario ordenadas por fecha (`ReservaRepository.listar_por_usuario`).

Excepciones de dominio usadas:

- `KitNoDisponible`
- `ReservaNoEncontrada`
- `ReservaNoCancelable`

Dependencias:

- Modelos: `Usuario`, `KitEspecializado`, `ReservaKit` (`blog/domain/models.py`).
- Builder: `ReservaKitBuilder` (`blog/domain/builders.py`).
- Validadores: `validar_fechas_reserva`, `validar_campos_reserva`, etc. (`blog/domain/validators.py`).
- Repositorios: `KitRepository`, `ReservaRepository` (`blog/Infrastructure/repositories.py`).
- Notificador: instancia creada por `NotificadorFactory`.

#### 2.2. `CursoService` (`blog/Application/services.py`)

Casos de uso:

- **`listar_cursos(solo_activos=True)`**
  - Recupera cursos desde `CursoRepository.listar_cursos`.
  - Por defecto devuelve solo cursos activos.

- **`comprar_curso(usuario, curso_id)`**
  - Obtiene el curso (`CursoRepository.obtener_por_id`).
  - Si no existe o está inactivo, lanza **`CursoNoEncontrado`**.
  - Si el usuario ya lo compró (`CompraCursoRepository.existe_compra`), lanza **`CursoYaComprado`**.
  - Crea y persiste una `CompraCurso`.

Excepciones:

- `CursoNoEncontrado`
- `CursoYaComprado`

Dependencias:

- Modelos: `Curso`, `CompraCurso`.
- Repositorios: `CursoRepository`, `CompraCursoRepository`.

---

### 3. Factory Pattern — Notificador

Archivo: `blog/Application/Factories.py`

- **`EmailNotifier`**
  - Implementación “real” de notificación (simulada con un print).
- **`MockNotifier`**
  - Implementación simulada para desarrollo/pruebas.
- **`NotificadorFactory`**
  - Método estático `crear()`:
    - Si `ENV_TYPE == "PROD"` → devuelve `EmailNotifier`.
    - En cualquier otro caso → devuelve `MockNotifier`.

El `ReservaService` solo sabe que tiene un objeto con método `enviar_confirmacion(reserva)`; no le importa si es real o mock → se cumple el principio **DIP (Dependency Inversion Principle)**.

---

### 4. Capa de Presentación (APIView + Serializers)

Archivo principal: `blog/Presentation/views.py`  
Serializers: `blog/Presentation/serializers.py`  
Rutas: `blog/Presentation/urls.py`

#### 4.1. Usuario / Dominio

- **`GET /api/usuario/actual/` → `UsuarioActualView`**
  - Usa `resolver_usuario_actual(request)`:
    - Si hay usuario autenticado, lo mapea a un `Usuario` de dominio.
    - Si viene `X-User-Id` o `usuario_id`, intenta cargar ese usuario.
    - Si no existe ninguno, crea un usuario demo.

#### 4.2. Kits y reservas (tag `reserva`)

- **`GET /api/kit/` → `ListarKitsView`**
  - Llama a `ReservaService.listar_kits(...)` (método de servicio que usa repositorios de kits).

- **`POST /api/reserva/crear/` → `CrearReservaView`**
  - Request serializer: `CrearReservaRequestSerializer`.
  - Usa `resolver_usuario_actual` para obtener el usuario de dominio.
  - Llama a `ReservaService.crear_reserva(...)`.
  - Mapea:
    - `KitNoEncontrado` → 404.
    - `KitNoDisponible` → 409.
    - `ValueError` → 400.

- **`POST /api/reserva/disponibilidad/` → `VerificarDisponibilidadView`**
  - Llama a `ReservaService.verificar_disponibilidad(...)`.
  - Devuelve 200 si está disponible; 404/409/400 según la excepción de dominio.

- **`POST /api/reserva/cancelar/` → `CancelarReservaView`**
  - Llama a `ReservaService.cancelar_reserva(usuario, reserva_id)`.
  - Mapea:
    - `ReservaNoEncontrada` → 404.
    - `ReservaNoCancelable` → 409.
    - `ValueError` → 400.

- **`GET /api/reserva/mis-reservas/` → `ListarReservasUsuarioView`**
  - Usa `resolver_usuario_actual` y `ReservaService.listar_reservas_de_usuario`.

#### 4.3. Cursos (tag `curso`)

- **`GET /api/curso/` → `ListarCursosView`**
  - Llama a `CursoService.listar_cursos(solo_activos=True)`.

- **`POST /api/curso/comprar/` → `ComprarCursoView`**
  - Request serializer: `ComprarCursoRequestSerializer`.
  - Usa `resolver_usuario_actual` y `CursoService.comprar_curso(usuario, curso_id)`.
  - Mapea:
    - `CursoNoEncontrado` → 404.
    - `CursoYaComprado` → 409.
    - `ValueError` → 400.

---

### 5. Datos de prueba (seed de base de datos)

Comando de management: `blog/management/commands/seed_mock_data.py`

Ejecutar:

```bash
python manage.py migrate
python manage.py seed_mock_data
```

Este comando crea:

- **Usuarios** (`Usuario`):
  - `basico@jesurvivor.local` (nivel básico).
  - `intermedio@jesurvivor.local` (nivel intermedio).
  - `avanzado@jesurvivor.local` (nivel avanzado).

- **Kits** (`KitEspecializado`):
  - “Kit Montaña Básico”
  - “Kit Selva Intermedio”
  - “Kit Nieve Avanzado”
  - “Kit Urbano Intermedio”
  - “Kit Desierto Básico”

- **Cursos** (`Curso`):
  - “Supervivencia 101”
  - “Navegación y orientación”
  - “Operaciones avanzadas en clima extremo”
  - “Refugio y fuego en montaña”
  - “Primeros auxilios de campo”

- **Ejemplos de negocio**:
  - Una compra de curso (`CompraCurso`) para uno de los usuarios.
  - Una reserva de kit (`ReservaKit`) para probar solapamientos.

Con esto, el frontend y Swagger pueden demostrar:

- Listado de kits y cursos.
- Creación/cancelación de reservas.
- Compra de cursos.

---

### 6. Cómo probar todo (flujo completo)

1. **Backend**

```bash
python manage.py migrate
python manage.py seed_mock_data
python manage.py runserver
```

2. **Swagger**

- `http://127.0.0.1:8000/api/docs/`
  - Probar:
    - `GET /api/curso/`
    - `POST /api/curso/comprar/`
    - `GET /api/kit/`
    - `POST /api/reserva/crear/`
    - `GET /api/reserva/mis-reservas/`

3. **Frontend**

- Abrir `http://127.0.0.1:8000/`
- Página de **Cursos**:
  - Lista cursos desde `GET /api/curso/`.
  - Compra cursos con `POST /api/curso/comprar/`.
- Página de **Tienda**:
  - Lista kits desde `GET /api/kit/`.
  - Puede integrarse con reserva de kits (`POST /api/reserva/crear/`).

