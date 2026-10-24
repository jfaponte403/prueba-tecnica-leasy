# Supuestos

- Se asume que los customers/clients de la mini app pueden crear sus propias reservas, no solo cancelarlas.
- Toda reserva creada por un cliente empieza en estado `requested`. Confirmarla o ponerla en `on_hold` le toca al staff
  desde el backoffice, no al cliente.
- Las salas se reservan por horas completas
- La cancelación es definitiva: una reserva cancelada no se reactiva

# Decisiones técnicas

1. **Endpoint de creación de reservas para clientes (`POST /api/v1/reservations/`).**
   Además de cancelar, agregué la posibilidad de que el cliente cree sus propias
   reservas desde la mini app `clinet-app`

2. **Streaming de ocupación de salas (`GET /api/v1/rooms/occupancy/events`, SSE).**
   El objetivo es evitar que dos personas aparten la misma sala al mismo tiempo.
   El endpoint envía un `snapshot` inicial de los horarios ocupados y luego un
   evento `slot` por cada cambio, así la UI bloquea el horario en cuanto otro
   cliente lo reserva, sin recargar la página. Elegí Server-Sent Events en vez de
   WebSockets porque el flujo es unidireccional (servidor → cliente), funciona
   sobre HTTP normal con el mismo JWT y no requiere Channels ni Redis.

3. **Prevención de reservas duplicadas en el servidor.**
   El stream de ocupación sirve para que el usuario vea los cambios al instante,
   pero no garantiza nada por sí solo: dos clientes pueden enviar la misma reserva
   casi al mismo tiempo. Por eso la creación se hace dentro de una transacción que
   bloquea la fila de la sala (`select_for_update`).

## Alternativa descartada

1. **Webhooks para notificar cambios en las reservas.**
   La idea era que el backend enviara un `POST` a una URL registrada cada vez que
   se creara, cancelara o cambiara de estado una reserva. Lo descarté porque los
   webhooks sirven para comunicar un servidor con otro: el navegador del cliente
   no puede exponer una URL pública para recibirlos, así que igual haría falta un
   servicio intermedio que los reciba y los reenvíe a la UI por otro canal. Eso
   suma infraestructura, reintentos, firma de las peticiones y manejo de entregas
   fallidas, sin resolver lo que se necesita: que la pantalla del cliente se
   actualice al instante.
