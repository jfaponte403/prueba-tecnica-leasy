import { useEffect, useRef } from 'react'
import { useCreateReservation } from '../hooks/useCreateReservation.ts'
import type { Reservation } from '../services/reservationService.ts'

interface CreateReservationModalProps {
  isOpen: boolean
  onClose: () => void
  onCreated: (reservation: Reservation) => void
}

function CreateReservationModal({ isOpen, onClose, onCreated }: CreateReservationModalProps) {
  const dialogRef = useRef<HTMLDialogElement>(null)
  const { values, error, isSubmitting, handleChange, handleSubmit, reset } = useCreateReservation({
    onCreated: (reservation) => {
      onCreated(reservation)
      onClose()
    },
  })

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
        </div>

        <label className="field">
          ID de la sala
          <input
            type="text"
            name="room_id"
            value={values.room_id}
            onChange={handleChange}
            required
          />
        </label>

        <div className="grid-2">
          <label className="field">
            Inicio
            <input
              type="datetime-local"
              name="starts_at"
              value={values.starts_at}
              onChange={handleChange}
              required
            />
          </label>

          <label className="field">
            Fin
            <input
              type="datetime-local"
              name="ends_at"
              min={values.starts_at || undefined}
              value={values.ends_at}
              onChange={handleChange}
              required
            />
          </label>
        </div>

        {error && (
          <p className="error" role="alert">
            {error}
          </p>
        )}

        <div className="actions modal__actions">
          <button className="btn" type="button" onClick={handleClose} disabled={isSubmitting}>
            Cancelar
          </button>
          <button className="btn btn-primary" type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Creando…' : 'Crear reserva'}
          </button>
        </div>
      </form>
    </dialog>
  )
}

export default CreateReservationModal
