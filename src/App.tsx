import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useState, useEffect } from 'react'
import { tauriInvoke } from './lib/tauri'

// Layouts
import DashboardLayout from './layouts/DashboardLayout'

// Pages
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import DashboardPage from './pages/DashboardPage'
import ContentPage from './pages/ContentPage'
import GenerateContentPage from './pages/GenerateContentPage'
import CalendarPage from './pages/CalendarPage'
import AnalyticsPage from './pages/AnalyticsPage'
import CampaignsPage from './pages/CampaignsPage'
import GenerateCampaignPage from './pages/GenerateCampaignPage'
import AssistantPage from './pages/AssistantPage'
import ReportsPage from './pages/ReportsPage'
import SettingsPage from './pages/SettingsPage'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60 * 1000,
      refetchOnWindowFocus: false,
    },
  },
})

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(() => {
    return localStorage.getItem('token') !== null
  })

  // Validate token on mount
  useEffect(() => {
    const token = localStorage.getItem('token')
    if (token) {
      tauriInvoke<string>('verify_token', { token }).catch(() => {
        localStorage.removeItem('token')
        setIsAuthenticated(false)
      })
    }
  }, [])

  const handleLogin = (token: string) => {
    localStorage.setItem('token', token)
    setIsAuthenticated(true)
  }

  const handleLogout = () => {
    localStorage.removeItem('token')
    setIsAuthenticated(false)
  }

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          {/* Auth routes */}
          <Route path="/login" element={
            isAuthenticated ? <Navigate to="/dashboard" /> : <LoginPage onLogin={handleLogin} />
          } />
          <Route path="/register" element={
            isAuthenticated ? <Navigate to="/dashboard" /> : <RegisterPage onLogin={handleLogin} />
          } />

          {/* Dashboard routes */}
          <Route path="/" element={
            isAuthenticated ? <DashboardLayout onLogout={handleLogout} /> : <Navigate to="/login" />
          }>
            <Route index element={<Navigate to="/dashboard" />} />
            <Route path="dashboard" element={<DashboardPage />} />
            <Route path="content" element={<ContentPage />} />
            <Route path="content/generate" element={<GenerateContentPage />} />
            <Route path="calendar" element={<CalendarPage />} />
            <Route path="analytics" element={<AnalyticsPage />} />
            <Route path="campaigns" element={<CampaignsPage />} />
            <Route path="campaigns/generate" element={<GenerateCampaignPage />} />
            <Route path="assistant" element={<AssistantPage />} />
            <Route path="reports" element={<ReportsPage />} />
            <Route path="settings" element={<SettingsPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  )
}

export default App
