import { apiClient } from '../API/ApiClient.ts'

export type ReservationStatus = 'requested' | 'confirmed' | 'cancelled' | 'on_hold'

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

export interface CancelReservationPayload {
  reason: string
}

export const reservationService = {
  list(): Promise<Reservation[]> {
    return apiClient.get<Reservation[]>('/reservations/')
  },

  create(payload: CreateReservationPayload): Promise<Reservation> {
    return apiClient.post<Reservation>('/reservations/', payload)
  },

  cancel(id: string, payload: CancelReservationPayload): Promise<Reservation> {
    return apiClient.post<Reservation>(`/reservations/${id}/cancel`, payload)
  },
}
