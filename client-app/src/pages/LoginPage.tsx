import { useLogin } from '../hooks/useLogin.ts'

function LoginPage() {
  const { values, error, isSubmitting, handleChange, handleSubmit } = useLogin()

  return (
    <main className="shell auth-shell">
      <section className="card stack">
        <div>
          <h1>Iniciar sesión</h1>
          <p className="muted">Ingresa con tu correo y contraseña.</p>
        </div>

        <form className="stack" onSubmit={handleSubmit}>
          <label className="field">
            Correo electrónico
            <input
              type="email"
              name="email"
              autoComplete="email"
              value={values.email}
              onChange={handleChange}
              required
            />
          </label>

          <label className="field">
            Contraseña
            <input
              type="password"
              name="password"
              autoComplete="current-password"
              minLength={4}
              value={values.password}
              onChange={handleChange}
              required
            />
          </label>

          {error && (
            <p className="error" role="alert">
              {error}
            </p>
          )}

          <button className="btn btn-primary" type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Entrando…' : 'Entrar'}
          </button>
        </form>
      </section>
    </main>
  )
}

export default LoginPage
