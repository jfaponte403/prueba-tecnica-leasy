import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ApiError } from '../API/ApiClient.ts'
import { clearToken } from '../auth/token.ts'
import { reservationService } from '../services/reservationService.ts'
import type { Reservation } from '../services/reservationService.ts'

export function useReservations() {
  const navigate = useNavigate()
  const [reservations, setReservations] = useState<Reservation[]>([])
  const [error, setError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    let ignore = false

    reservationService
      .list()
      .then((data) => {
        if (!ignore) setReservations(data)
      })
      .catch((err) => {
        if (ignore) return
        if (err instanceof ApiError && err.status === 401) {
          clearToken()
          navigate('/login', { replace: true })
          return
        }
        setError('No se pudieron cargar las reservas. Intenta de nuevo.')
      })
      .finally(() => {
        if (!ignore) setIsLoading(false)
      })

    return () => {
      ignore = true
    }
  }, [navigate])

  const addReservation = (reservation: Reservation) => {
    setReservations((prev) => [reservation, ...prev])
  }

  return { reservations, error, isLoading, addReservation }
}
