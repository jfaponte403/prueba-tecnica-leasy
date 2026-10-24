import { useState } from 'react'
import type { ChangeEvent, FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { ApiError } from '../API/ApiClient.ts'
import { clearToken } from '../auth/token.ts'
import { reservationService } from '../services/reservationService.ts'
import type { Reservation } from '../services/reservationService.ts'
import type { OccupiedSlot } from '../services/roomService.ts'

export interface CreateReservationFormValues {
  room_id: string
  date: string
  start_hour: string
  end_hour: string
}

const INITIAL_VALUES: CreateReservationFormValues = {
  room_id: '',
  date: '',
  start_hour: '',
  end_hour: '',
}

interface UseCreateReservationOptions {
  occupiedSlots?: OccupiedSlot[]
  onCreated?: (reservation: Reservation) => void
}

export const ROOM_UNAVAILABLE_MESSAGE = 'La sala ya está reservada en ese horario. Elige otro.'

export const HOURS = Array.from({ length: 25 }, (_, hour) => hour)

export function formatHour(hour: number): string {
  return `${String(hour).padStart(2, '0')}:00`
}

export function buildDate(date: string, hour: number): Date {
  const result = new Date(`${date}T00:00`)
  result.setHours(hour)
  return result
}

function findOverlap(
  slots: OccupiedSlot[],
  roomId: string,
  startsAt: Date,
  endsAt: Date,
): OccupiedSlot | null {
  return (
    slots.find(
      (slot) =>
        slot.room_id === roomId &&
        new Date(slot.starts_at).getTime() < endsAt.getTime() &&
        new Date(slot.ends_at).getTime() > startsAt.getTime(),
    ) ?? null
  )
}

export function isHourOccupied(
  slots: OccupiedSlot[],
  roomId: string,
  date: string,
  hour: number,
): boolean {
  if (!roomId || !date) return false
  return findOverlap(slots, roomId, buildDate(date, hour), buildDate(date, hour + 1)) !== null
}

function findConflict(
  slots: OccupiedSlot[],
  { room_id, date, start_hour, end_hour }: CreateReservationFormValues,
): OccupiedSlot | null {
  if (!room_id || !date || start_hour === '' || end_hour === '') return null
  if (Number(end_hour) <= Number(start_hour)) return null
  return findOverlap(
    slots,
    room_id,
    buildDate(date, Number(start_hour)),
    buildDate(date, Number(end_hour)),
  )
}

function getErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    const { code, detail } = (error.data as { code?: unknown; detail?: unknown } | null) ?? {}
    if (code === 'reservation_room_unavailable') {
      return ROOM_UNAVAILABLE_MESSAGE
    }
    if (typeof detail === 'string') {
      return detail
    }
  }
  return 'No se pudo crear la reserva. Intenta de nuevo.'
}

export function useCreateReservation({
  occupiedSlots = [],
  onCreated,
}: UseCreateReservationOptions = {}) {
  const navigate = useNavigate()
  const [values, setValues] = useState<CreateReservationFormValues>(INITIAL_VALUES)
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const conflict = findConflict(occupiedSlots, values)

  const handleChange = (event: ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = event.target
    setValues((prev) => {
      const next = { ...prev, [name]: value }
      if (name === 'start_hour' && value !== '' && Number(prev.end_hour) <= Number(value)) {
        next.end_hour = String(Number(value) + 1)
      }
      return next
    })
  }

  const reset = () => {
    setValues(INITIAL_VALUES)
    setError(null)
  }

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setError(null)

    const startHour = Number(values.start_hour)
    const endHour = Number(values.end_hour)
    if (endHour <= startHour) {
      setError('La hora de fin debe ser posterior a la de inicio.')
      return
    }
    if (conflict) {
      setError(ROOM_UNAVAILABLE_MESSAGE)
      return
    }

    setIsSubmitting(true)
    try {
      const reservation = await reservationService.create({
        room_id: values.room_id,
        starts_at: buildDate(values.date, startHour).toISOString(),
        ends_at: buildDate(values.date, endHour).toISOString(),
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

  return { values, error, conflict, isSubmitting, handleChange, handleSubmit, reset }
}
