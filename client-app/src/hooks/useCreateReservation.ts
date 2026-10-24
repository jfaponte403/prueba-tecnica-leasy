import { useState } from 'react'
import type { ChangeEvent, FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { ApiError } from '../API/ApiClient.ts'
import { clearToken } from '../auth/token.ts'
import { reservationService } from '../services/reservationService.ts'
import type { Reservation } from '../services/reservationService.ts'

export interface CreateReservationFormValues {
  room_id: string
  starts_at: string
  ends_at: string
}

const INITIAL_VALUES: CreateReservationFormValues = { room_id: '', starts_at: '', ends_at: '' }

interface UseCreateReservationOptions {
  onCreated?: (reservation: Reservation) => void
}

function getErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    const detail = (error.data as { detail?: unknown } | null)?.detail
    if (typeof detail === 'string') {
      return detail
    }
  }
  return 'No se pudo crear la reserva. Intenta de nuevo.'
}

export function useCreateReservation({ onCreated }: UseCreateReservationOptions = {}) {
  const navigate = useNavigate()
  const [values, setValues] = useState<CreateReservationFormValues>(INITIAL_VALUES)
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleChange = (event: ChangeEvent<HTMLInputElement>) => {
    const { name, value } = event.target
    setValues((prev) => ({ ...prev, [name]: value }))
  }

  const reset = () => {
    setValues(INITIAL_VALUES)
    setError(null)
  }

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setError(null)

    // datetime-local values are in local time; send them to the API as ISO (UTC)
    const startsAt = new Date(values.starts_at)
    const endsAt = new Date(values.ends_at)
    if (endsAt <= startsAt) {
      setError('La fecha de fin debe ser posterior a la de inicio.')
      return
    }

    setIsSubmitting(true)
    try {
      const reservation = await reservationService.create({
        room_id: values.room_id.trim(),
        starts_at: startsAt.toISOString(),
        ends_at: endsAt.toISOString(),
      })
      reset()
      onCreated?.(reservation)
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

  return { values, error, isSubmitting, handleChange, handleSubmit, reset }
}
