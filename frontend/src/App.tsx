import { useEffect } from 'react'
import { QueryClientProvider } from '@tanstack/react-query'
import { RouterProvider, createBrowserRouter, createRoutesFromElements, Route } from 'react-router-dom'
import { queryClient } from '@/lib/queryClient'
import { attachBackendWakeupInterceptors } from '@/lib/api'
import { BackendWakeupPopup } from '@/components/BackendWakeupPopup'
import { ProtectedRoute } from '@/components/ProtectedRoute'
import { LoginPage } from '@/pages/LoginPage'
import { HomePage } from '@/pages/HomePage'

const router = createBrowserRouter(
  createRoutesFromElements(
    <>
      <Route path="/login" element={<LoginPage />} />
      <Route element={<ProtectedRoute />}>
        <Route path="/" element={<HomePage />} />
      </Route>
    </>
  )
)

function App() {
  useEffect(() => {
    attachBackendWakeupInterceptors()
  }, [])

  return (
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router} />
      <BackendWakeupPopup />
    </QueryClientProvider>
  )
}

export default App
