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
