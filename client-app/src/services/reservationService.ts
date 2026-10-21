import { apiClient } from '../API/ApiClient.ts'

export type ReservationStatus = 'requested' | 'confirmed' | 'cancelled'

export interface Reservation {
  id: string
  room_name: string
  status: ReservationStatus
  starts_at: string
  ends_at: string
  cancel_reason: string | null
}

export const reservationService = {
  list(): Promise<Reservation[]> {
    return apiClient.get<Reservation[]>('/reservations/')
  },
}
