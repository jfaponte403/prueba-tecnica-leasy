import { useNavigate } from 'react-router-dom'
import { clearToken, getToken } from '../auth/token.ts'

function AppHeader() {
  const navigate = useNavigate()
  const isAuthenticated = Boolean(getToken())

  const handleLogout = () => {
    clearToken()
    navigate('/login', { replace: true })
  }

  return (
    <header className="app-header">
      <div className="app-header__inner">
        <span className="brand">
          <span className="brand__mark">PC</span>
          <span className="brand__text">
            <span className="brand__title">Portal de clientes</span>
            <span className="brand__subtitle">Consulta y gestiona tus reservas.</span>
          </span>
        </span>

        {isAuthenticated && (
          <div className="header-actions">
            <button className="btn" type="button" onClick={handleLogout}>
              Cerrar sesión
            </button>
          </div>
        )}
      </div>
    </header>
  )
}

export default AppHeader
