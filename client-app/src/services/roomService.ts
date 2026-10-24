import { apiClient } from '../API/ApiClient.ts'

export interface Room {
  id: string
  name: string
  floor: number
  capacity: number
}

export const roomService = {
  list(): Promise<Room[]> {
    return apiClient.get<Room[]>('/rooms/')
  },
}

export interface OccupiedSlot {
  reservation_id: string
  room_id: string
  starts_at: string
  ends_at: string
  is_blocking: boolean
}

export const ROOM_OCCUPANCY_EVENTS_ENDPOINT = '/rooms/occupancy/events'
