import { createBrowserRouter, Navigate } from 'react-router-dom'
import App from '../App.tsx'
import ProtectedRoute from '../auth/ProtectedRoute.tsx'
import LoginPage from '../pages/LoginPage.tsx'
import NotFoundPage from '../pages/NotFoundPage.tsx'

export const router = createBrowserRouter([
  {
    element: <App />,
    children: [
      { path: '/login', element: <LoginPage /> },
      {
        // Todo lo que no sea /login requiere token
        element: <ProtectedRoute />,
        children: [
          { path: '/not-found', element: <NotFoundPage /> },
          { path: '*', element: <Navigate to="/not-found" replace /> },
        ],
      },
    ],
  },
])
