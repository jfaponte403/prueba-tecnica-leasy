import { useEffect, useRef } from 'react'
import { CANCEL_REASON_MAX_LENGTH, useCancelReservation } from '../hooks/useCancelReservation.ts'
import type { Reservation } from '../services/reservationService.ts'

interface CancelReservationModalProps {
  reservation: Reservation | null
  onClose: () => void
  onCancelled: (reservation: Reservation) => void
}

function CancelReservationModal({ reservation, onClose, onCancelled }: CancelReservationModalProps) {
  const dialogRef = useRef<HTMLDialogElement>(null)
  const isOpen = reservation !== null
  const { reason, error, isSubmitting, handleChange, handleSubmit, reset } = useCancelReservation({
    reservationId: reservation?.id ?? null,
    onCancelled: (cancelled) => {
      onCancelled(cancelled)
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
          <h2>Cancelar reserva</h2>
          {reservation && (
            <p className="muted">
              Vas a cancelar la reserva de <strong>{reservation.room_name}</strong>. Esta acción no
              se puede deshacer.
            </p>
          )}
        </div>

        <label className="field">
          Motivo de cancelación
          <textarea
            name="reason"
            rows={4}
            maxLength={CANCEL_REASON_MAX_LENGTH}
            value={reason}
            onChange={handleChange}
            required
          />
        </label>

        {error && (
          <p className="error" role="alert">
            {error}
          </p>
        )}

        <div className="actions modal__actions">
          <button className="btn" type="button" onClick={handleClose} disabled={isSubmitting}>
            Volver
          </button>
          <button className="btn btn-danger" type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Cancelando…' : 'Cancelar reserva'}
          </button>
        </div>
      </form>
    </dialog>
  )
}

export default CancelReservationModal
