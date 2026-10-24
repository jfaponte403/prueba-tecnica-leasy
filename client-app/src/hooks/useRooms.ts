import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ApiError } from '../API/ApiClient.ts'
import { clearToken } from '../auth/token.ts'
import { roomService } from '../services/roomService.ts'
import type { Room } from '../services/roomService.ts'

export function useRooms() {
  const navigate = useNavigate()
  const [rooms, setRooms] = useState<Room[]>([])
  const [error, setError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    let ignore = false

    roomService
      .list()
      .then((data) => {
        if (!ignore) setRooms(data)
      })
      .catch((err) => {
        if (ignore) return
        if (err instanceof ApiError && err.status === 401) {
          clearToken()
          navigate('/login', { replace: true })
          return
        }
        setError('No se pudieron cargar las salas. Intenta de nuevo.')
      })
      .finally(() => {
        if (!ignore) setIsLoading(false)
      })

    return () => {
      ignore = true
    }
  }, [navigate])

  return { rooms, error, isLoading }
}
