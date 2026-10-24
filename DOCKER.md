# Docker

## Requisitos

- Docker Engine 24+ con Docker Compose v2 (`docker compose`, no `docker-compose`).
- BuildKit habilitado (viene por defecto en Docker 23+). Los Dockerfiles usan `RUN --mount=type=cache` y `--mount=type=bind`.
- Puertos `8000` y `8080` libres en el host (o configurar otros, ver [Variables de entorno](#variables-de-entorno)).

## Cómo correr la app

Para levantar la aplicación, se debe ejecutar el siguiente comando:

```bash
docker compose up --build
```

Ejecutará los servicios definidos en el archivo `docker-compose.yml`, construyendo las imágenes necesarias si no existen.

Se crearán los siguientes contenedores:
1. `client`: la cual hace referencia a la aplicación del cliente (React) `client-app` y se hosteará en el puerto `8080`.

2. `backend`: la cual hace referencia a la aplicación del servidor (Django) `src` y se hosteará en el puerto `8000`.

El contenedor `client` solo arranca cuando el `backend` reporta estado `healthy` (`depends_on: condition: service_healthy`).

### URLs disponibles

| Servicio | URL |
|---|---|
| App cliente (React) | http://localhost:8080 |
| Backoffice (Django) | http://localhost:8000/backoffice/reservations/ |
| Login del backoffice | http://localhost:8000/accounts/login/ |
| Admin de Django | http://localhost:8000/admin/ |
| API cliente | http://localhost:8000/api/v1/ |

### Usuarios de demo

Si `DJANGO_SEED_DEMO_DATA=true` (valor por defecto), en el primer arranque se cargan datos de prueba con el comando `seed_assessment_data`. Todos los usuarios usan la contraseña `demo1234`:

| Usuario | Email | Uso |
|---|---|---|
| `manager` | manager@example.com | Backoffice |
| `operator` | operator@example.com | Backoffice |
| `alice` | alice@example.com | App cliente |
| `bob` | bob@example.com | App cliente |


## Variables de entorno

Todas las variables tienen un valor por defecto en `docker-compose.yml`, por lo que la app funciona sin configuración adicional. Para personalizarlas, copiar el archivo de ejemplo y editarlo; Docker Compose lee automáticamente el `.env` de la raíz:

```bash
cp .env.example .env
```

### Imágenes

| Variable | Default | Descripción |
|---|---|---|
| `IMAGE_REGISTRY` | `leasy` | Prefijo/registro de las imágenes (`leasy/backend`, `leasy/client-app`). |
| `IMAGE_TAG` | `latest` | Tag principal de las imágenes. |
| `APP_VERSION` | `0.1.0` | Tag adicional de versión y label `org.opencontainers.image.version`. |

### Puertos

| Variable | Default | Descripción |
|---|---|---|
| `BACKEND_PORT` | `8000` | Puerto del host mapeado al backend. |
| `CLIENT_PORT` | `8080` | Puerto del host mapeado al cliente. |
