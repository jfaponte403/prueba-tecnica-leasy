import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ApiError } from '../API/ApiClient.ts'
import { readEventStream } from '../API/EventStream.ts'
import type { ServerEvent } from '../API/EventStream.ts'
import { clearToken } from '../auth/token.ts'
import { ROOM_OCCUPANCY_EVENTS_ENDPOINT } from '../services/roomService.ts'
import type { OccupiedSlot } from '../services/roomService.ts'

const RECONNECT_DELAY_MS = 3000

type SlotsById = Record<string, OccupiedSlot>

function applyEvent(slots: SlotsById, { event, data }: ServerEvent): SlotsById {
  if (event === 'snapshot') {
    return Object.fromEntries((data as OccupiedSlot[]).map((slot) => [slot.reservation_id, slot]))
  }

  if (event === 'slot') {
    const slot = data as OccupiedSlot
    const next = { ...slots }
    if (slot.is_blocking) next[slot.reservation_id] = slot
    else delete next[slot.reservation_id]
    return next
  }

  return slots
}

export function useRoomOccupancy() {
  const navigate = useNavigate()
  const [slotsById, setSlotsById] = useState<SlotsById>({})
  const [isConnected, setIsConnected] = useState(false)

  useEffect(() => {
    const controller = new AbortController()
    let reconnectTimer: ReturnType<typeof setTimeout> | undefined

    const connect = () => {
      readEventStream(
        ROOM_OCCUPANCY_EVENTS_ENDPOINT,
        (event) => {
          if (event.event === 'snapshot') setIsConnected(true)
          setSlotsById((prev) => applyEvent(prev, event))
        },
        controller.signal,
      )
        .then(() => true)
        .catch((err) => {
          if (err instanceof ApiError && err.status === 401) {
            clearToken()
            navigate('/login', { replace: true })
            return false
          }
          return true
        })
        .then((shouldReconnect) => {
          if (controller.signal.aborted) return
          setIsConnected(false)
          if (shouldReconnect) reconnectTimer = setTimeout(connect, RECONNECT_DELAY_MS)
        })
    }

    connect()

    return () => {
      controller.abort()
      clearTimeout(reconnectTimer)
    }
  }, [navigate])

  return { slots: Object.values(slotsById), isConnected }
}
