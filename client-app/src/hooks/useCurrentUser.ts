import { useEffect, useState } from 'react'
import { authService } from '../services/authService.ts'
import type { AuthUser } from '../services/authService.ts'

// El header no se desmonta al hacer login/logout, por eso se recarga cuando cambia el token
export function useCurrentUser(token: string | null) {
  const [loaded, setLoaded] = useState<{ token: string; user: AuthUser } | null>(null)

  useEffect(() => {
    if (!token) return

    let ignore = false

    authService
      .me()
      .then((user) => {
        if (!ignore) setLoaded({ token, user })
      })
      .catch(() => {
        // Sin usuario visible; los hooks de datos ya manejan el 401
      })

    return () => {
      ignore = true
    }
  }, [token])

  // Solo se muestra el usuario si corresponde al token actual
  const user = loaded && loaded.token === token ? loaded.user : null

  return { user }
}
