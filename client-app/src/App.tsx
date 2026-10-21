import { Outlet } from 'react-router-dom'
import AppHeader from './components/AppHeader.tsx'

function App() {
  return (
    <>
      <AppHeader />
      <Outlet />
    </>
  )
}

export default App
