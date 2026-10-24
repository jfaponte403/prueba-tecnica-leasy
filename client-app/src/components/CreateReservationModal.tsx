import { useEffect, useRef } from 'react'
import {
  formatHour,
  HOURS,
  isHourOccupied,
  ROOM_UNAVAILABLE_MESSAGE,
  useCreateReservation,
} from '../hooks/useCreateReservation.ts'
import { useRoomOccupancy } from '../hooks/useRoomOccupancy.ts'
import { useRooms } from '../hooks/useRooms.ts'
import type { Reservation } from '../services/reservationService.ts'

const slotFormatter = new Intl.DateTimeFormat('es-CO', {
  dateStyle: 'medium',
  timeStyle: 'short',
})

interface CreateReservationModalProps {
  isOpen: boolean
  onClose: () => void
  onCreated: (reservation: Reservation) => void
}

function CreateReservationModal({ isOpen, onClose, onCreated }: CreateReservationModalProps) {
  const dialogRef = useRef<HTMLDialogElement>(null)
  const { rooms, error: roomsError, isLoading: isLoadingRooms } = useRooms()
  const { slots, isConnected } = useRoomOccupancy()
  const { values, error, conflict, isSubmitting, handleChange, handleSubmit, reset } =
    useCreateReservation({
      occupiedSlots: slots,
      onCreated: (reservation) => {
        onCreated(reservation)
        onClose()
      },
    })

  const roomSlots = slots
    .filter((slot) => slot.room_id === values.room_id)
    .sort((a, b) => a.starts_at.localeCompare(b.starts_at))

  useEffect(() => {
    const dialog = dialogRef.current
    if (!dialog) return
    if (isOpen && !dialog.open) dialog.showModal()
    if (!isOpen && dialog.open) dialog.close()
  }, [isOpen])

  const handleClose = () => {
    reset()
    onClose()
  }

  return (
    <dialog ref={dialogRef} className="modal card" onClose={handleClose}>
      <form className="stack" onSubmit={handleSubmit}>
        <div>
          <h2>Nueva reserva</h2>
          <p className="muted">Indica la sala y el horario que necesitas.</p>
          <p className={`live-status ${isConnected ? 'live-status--on' : ''}`}>
            {isConnected ? 'Disponibilidad en tiempo real' : 'Conectando disponibilidad…'}
          </p>
        </div>

        <label className="field">
          Sala
          <select
            name="room_id"
            value={values.room_id}
            onChange={handleChange}
            disabled={isLoadingRooms || rooms.length === 0}
            required
          >
            <option value="" disabled>
              {isLoadingRooms ? 'Cargando salas…' : 'Selecciona una sala'}
            </option>
            {rooms.map((room) => (
              <option key={room.id} value={room.id}>
                {room.name} · Piso {room.floor} · {room.capacity} personas
              </option>
            ))}
          </select>
        </label>

        {roomsError && (
          <p className="error" role="alert">
            {roomsError}
          </p>
        )}

        {!isLoadingRooms && !roomsError && rooms.length === 0 && (
          <p className="muted">No hay salas disponibles.</p>
        )}

        <label className="field">
          Fecha
          <input type="date" name="date" value={values.date} onChange={handleChange} required />
        </label>

        <div className="grid-2">
          <label className="field">
            Hora de inicio
            <select name="start_hour" value={values.start_hour} onChange={handleChange} required>
              <option value="" disabled>
                Selecciona
              </option>
              {HOURS.slice(0, -1).map((hour) => {
                const isOccupied = isHourOccupied(slots, values.room_id, values.date, hour)
                return (
                  <option key={hour} value={hour} disabled={isOccupied}>
                    {formatHour(hour)}
                    {isOccupied ? ' · ocupada' : ''}
                  </option>
                )
              })}
            </select>
          </label>

          <label className="field">
            Hora de fin
            <select
              name="end_hour"
              value={values.end_hour}
              onChange={handleChange}
              disabled={values.start_hour === ''}
              required
            >
              <option value="" disabled>
                Selecciona
              </option>
              {HOURS.slice(Number(values.start_hour) + 1).map((hour) => (
                <option key={hour} value={hour}>
                  {formatHour(hour)}
                </option>
              ))}
            </select>
          </label>
        </div>

        {values.room_id && roomSlots.length > 0 && (
          <div className="occupied-slots">
            <p className="muted">Horarios ocupados en esta sala</p>
            <ul>
              {roomSlots.map((slot) => (
                <li
                  key={slot.reservation_id}
                  className={slot.reservation_id === conflict?.reservation_id ? 'is-conflict' : ''}
                >
                  {slotFormatter.format(new Date(slot.starts_at))} –{' '}
                  {slotFormatter.format(new Date(slot.ends_at))}
                </li>
              ))}
            </ul>
          </div>
        )}

        {conflict && !error && (
          <p className="error" role="alert">
            {ROOM_UNAVAILABLE_MESSAGE}
          </p>
        )}

        {error && (
          <p className="error" role="alert">
            {error}
          </p>
        )}

        <div className="actions modal__actions">
          <button className="btn" type="button" onClick={handleClose} disabled={isSubmitting}>
            Cancelar
          </button>
          <button
            className="btn btn-primary"
            type="submit"
            disabled={isSubmitting || conflict !== null}
          >
            {isSubmitting ? 'Creando…' : 'Crear reserva'}
          </button>
        </div>
      </form>
    </dialog>
  )
}

export default CreateReservationModal
