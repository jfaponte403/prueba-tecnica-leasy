import type { FormEvent } from 'react'

function LoginPage() {
  // Pendiente: conectar con el endpoint de login y guardar el token con setToken
  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
  }

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
            <input type="email" name="email" autoComplete="email" required />
          </label>

          <label className="field">
            Contraseña
            <input
              type="password"
              name="password"
              autoComplete="current-password"
              minLength={4}
              required
            />
          </label>

          <button className="btn btn-primary" type="submit">
            Entrar
          </button>
        </form>
      </section>
    </main>
  )
}

export default LoginPage
