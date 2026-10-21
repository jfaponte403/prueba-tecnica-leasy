import { useState } from 'react'
import type { ChangeEvent, FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { ApiError } from '../API/ApiClient.ts'
import { clearToken, setToken } from '../auth/token.ts'
import { authService } from '../services/authService.ts'
import type { AuthUser, LoginCredentials } from '../services/authService.ts'

const INITIAL_VALUES: LoginCredentials = { email: '', password: '' }

function getErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    const detail = (error.data as { detail?: unknown } | null)?.detail
    if (typeof detail === 'string') {
      return detail
    }
    if (error.status === 401) {
      return 'Correo o contraseña incorrectos.'
    }
  }
  return 'No se pudo iniciar sesión. Intenta de nuevo.'
}

export function useLogin() {
  const navigate = useNavigate()
  const [values, setValues] = useState<LoginCredentials>(INITIAL_VALUES)
  const [user, setUser] = useState<AuthUser | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleChange = (event: ChangeEvent<HTMLInputElement>) => {
    const { name, value } = event.target
    setValues((prev) => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setError(null)
    setIsSubmitting(true)

    try {
      const { access_token } = await authService.login(values)
      setToken(access_token)
      setUser(await authService.me())
      navigate('/', { replace: true })
    } catch (err) {
      clearToken()
      setError(getErrorMessage(err))
    } finally {
      setIsSubmitting(false)
    }
  }

  return { values, user, error, isSubmitting, handleChange, handleSubmit }
}
