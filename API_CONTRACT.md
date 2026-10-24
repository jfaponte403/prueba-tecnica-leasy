# Contrato base del API cliente

Base URL local:

- `http://127.0.0.1:8000/api/v1`

## Auth

### `POST /auth/login`

Request:

```json
{
  "email": "alice@example.com",
  "password": "demo1234"
}
```

Response `200`:

```json
{
  "access_token": "jwt-token",
  "token_type": "bearer"
}
```

### `GET /auth/me`

Header:

```text
Authorization: Bearer <token>
```

Response `200`:

```json
{
  "id": "uuid",
  "email": "alice@example.com",
  "display_name": "Alice Stone"
}
```

## Reservations

### `GET /reservations/`

Header:

```text
Authorization: Bearer <token>
```

Response `200`:

```json
[
  {
    "id": "uuid",
    "room_name": "Room A",
    "status": "requested",
    "starts_at": "2026-04-20T15:00:00-05:00",
    "ends_at": "2026-04-20T17:00:00-05:00",
    "cancel_reason": null
  }
]
```

## Error format

Los errores de dominio y auth deben mantenerse en este formato:

```json
{
  "type": "urn:assessment:problem:auth_invalid_credentials",
  "title": "Authentication Failed",
  "status": 401,
  "detail": "Invalid email or password.",
  "code": "auth_invalid_credentials",
  "instance": "/api/v1/auth/login",
  "errors": null
}
```

El endpoint de cancelación que debe construir el candidato debe seguir este
mismo contrato.

---
# Endpoints Nuevos

Todos requieren el header:

```text
Authorization: Bearer <token>
```

### `POST /reservations/`

Request:

```json
{
  "room_id": "uuid",
  "starts_at": "2026-04-20T15:00:00-05:00",
  "ends_at": "2026-04-20T17:00:00-05:00"
}
```

Response `200`:

```json
{
  "id": "uuid",
  "room_name": "Room A",
  "status": "requested",
  "starts_at": "2026-04-20T15:00:00-05:00",
  "ends_at": "2026-04-20T17:00:00-05:00",
  "cancel_reason": null
}
```

Errores: `400` (dominio), `422` (validación).

### `POST /reservations/{reservation_id}/cancel`

Request:

```json
{
  "reason": "Ya no necesito la sala"
}
```

Response `200`:

```json
{
  "id": "uuid",
  "room_name": "Room A",
  "status": "cancelled",
  "starts_at": "2026-04-20T15:00:00-05:00",
  "ends_at": "2026-04-20T17:00:00-05:00",
  "cancel_reason": "Ya no necesito la sala"
}
```

Errores: `400` (dominio), `422` (validación).

### `GET /rooms/`

Response `200`:

```json
[
  {
    "id": "uuid",
    "name": "Room A",
    "floor": 1,
    "capacity": 8
  }
]
```

### `GET /rooms/occupancy/events`

Stream SSE (`text/event-stream`). Envía un evento `snapshot` al conectar y
luego un evento `slot` por cada cambio.

Evento `snapshot`:

```json
[
  {
    "reservation_id": "uuid",
    "room_id": "uuid",
    "starts_at": "2026-04-20T15:00:00-05:00",
    "ends_at": "2026-04-20T17:00:00-05:00",
    "is_blocking": true
  }
]
```

Evento `slot`:

```json
{
  "reservation_id": "uuid",
  "room_id": "uuid",
  "starts_at": "2026-04-20T15:00:00-05:00",
  "ends_at": "2026-04-20T17:00:00-05:00",
  "is_blocking": false
}
```
