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

export interface CreateReservationPayload {
  room_id: string
  starts_at: string
  ends_at: string
}

export const reservationService = {
  list(): Promise<Reservation[]> {
    return apiClient.get<Reservation[]>('/reservations/')
  },

  create(payload: CreateReservationPayload): Promise<Reservation> {
    return apiClient.post<Reservation>('/reservations/', payload)
  },
}
