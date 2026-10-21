import { useReservations } from '../hooks/useReservations.ts'
import type { ReservationStatus } from '../services/reservationService.ts'

const STATUS_LABELS: Record<ReservationStatus, string> = {
  requested: 'Solicitada',
  confirmed: 'Confirmada',
  cancelled: 'Cancelada',
}

const dateFormatter = new Intl.DateTimeFormat('es-CO', {
  dateStyle: 'medium',
  timeStyle: 'short',
})

function formatDate(value: string): string {
  return dateFormatter.format(new Date(value))
}

function ReservationsPage() {
  const { reservations, error, isLoading } = useReservations()

  return (
    <main className="shell">
      <div className="topbar">
        <h1>Mis reservas</h1>
      </div>

      <section className="card">
        {isLoading && <p className="muted">Cargando reservas…</p>}

        {error && (
          <p className="error" role="alert">
            {error}
          </p>
        )}

        {!isLoading && !error && reservations.length === 0 && (
          <p className="muted">No tienes reservas.</p>
        )}

        {!isLoading && !error && reservations.length > 0 && (
          <table>
            <thead>
              <tr>
                <th>Sala</th>
                <th>Estado</th>
                <th>Inicio</th>
                <th>Fin</th>
                <th>Motivo de cancelación</th>
              </tr>
            </thead>
            <tbody>
              {reservations.map((reservation) => (
                <tr key={reservation.id}>
                  <td>{reservation.room_name}</td>
                  <td>
                    <span className="badge">
                      {STATUS_LABELS[reservation.status] ?? reservation.status}
                    </span>
                  </td>
                  <td>{formatDate(reservation.starts_at)}</td>
                  <td>{formatDate(reservation.ends_at)}</td>
                  <td>{reservation.cancel_reason ?? <span className="muted">—</span>}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </main>
  )
}

export default ReservationsPage
