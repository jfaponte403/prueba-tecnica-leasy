import { useState } from 'react'
import type { ChangeEvent, FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { ApiError } from '../API/ApiClient.ts'
import { clearToken } from '../auth/token.ts'
import { reservationService } from '../services/reservationService.ts'
import type { Reservation } from '../services/reservationService.ts'

export const CANCEL_REASON_MAX_LENGTH = 1000

interface UseCancelReservationOptions {
  reservationId: string | null
  onCancelled?: (reservation: Reservation) => void
}

function getErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    const detail = (error.data as { detail?: unknown } | null)?.detail
    if (typeof detail === 'string') {
      return detail
    }
  }
  return 'No se pudo cancelar la reserva. Intenta de nuevo.'
}

export function useCancelReservation({ reservationId, onCancelled }: UseCancelReservationOptions) {
  const navigate = useNavigate()
  const [reason, setReason] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleChange = (event: ChangeEvent<HTMLTextAreaElement>) => {
    setReason(event.target.value)
  }

  const reset = () => {
    setReason('')
    setError(null)
  }

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setError(null)
    if (!reservationId) return

    const trimmedReason = reason.trim()
    if (!trimmedReason) {
      setError('Debes indicar el motivo de la cancelación.')
      return
    }

    setIsSubmitting(true)
    try {
      const reservation = await reservationService.cancel(reservationId, { reason: trimmedReason })
      reset()
      onCancelled?.(reservation)
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        clearToken()
        navigate('/login', { replace: true })
        return
      }
      setError(getErrorMessage(err))
    } finally {
      setIsSubmitting(false)
    }
  }

  return { reason, error, isSubmitting, handleChange, handleSubmit, reset }
}
