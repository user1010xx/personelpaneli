import React, { createContext, useContext, useState, useEffect, useMemo, useCallback } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { authApi } from './api'
import apiClient from './api/client'
import LoginPage from './pages/Login'
import Dashboard from './pages/Dashboard'
import Sales from './pages/Sales'
import WhatsApp from './pages/WhatsApp'
import Personnel from './pages/Personnel'
import Attendance from './pages/Attendance'
import Warnings from './pages/Warnings'
import Training from './pages/Training'
import CallProcess from './pages/CallProcess'
import CallMonitoring from './pages/CallMonitoring'
import Users from './pages/Users'
import Navbar from './components/Navbar'
import './index.css'

const AuthContext = createContext(null)
const ACCESS_TOKEN_KEY = 'access_token'
const REFRESH_TOKEN_KEY = 'refresh_token'

export function useAuth() {
  return useContext(AuthContext)
}

function getTokenExpiry(token) {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]))
    return payload.exp ? payload.exp * 1000 : null
  } catch {
    return null
  }
}

function isTokenValid(token) {
  if (!token) {
    return false
  }
  const expiry = getTokenExpiry(token)
  return !expiry || expiry > Date.now()
}

function normalizeSession(tokens = {}) {
  return {
    accessToken: tokens.accessToken || null,
    refreshToken: tokens.refreshToken || null,
  }
}

const authStorage = {
  getSession() {
    const accessToken = localStorage.getItem(ACCESS_TOKEN_KEY)
    const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY)
    if (!isTokenValid(accessToken)) {
      localStorage.removeItem(ACCESS_TOKEN_KEY)
      return normalizeSession({ refreshToken })
    }
    return normalizeSession({ accessToken, refreshToken })
  },
  setSession({ accessToken, refreshToken }) {
    if (accessToken) {
      localStorage.setItem(ACCESS_TOKEN_KEY, accessToken)
    } else {
      localStorage.removeItem(ACCESS_TOKEN_KEY)
    }
    if (refreshToken) {
      localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken)
    } else {
      localStorage.removeItem(REFRESH_TOKEN_KEY)
    }
  },
  clearSession() {
    localStorage.removeItem(ACCESS_TOKEN_KEY)
    localStorage.removeItem(REFRESH_TOKEN_KEY)
  },
}

function AuthProvider({ children }) {
  const [session, setSessionState] = useState(() => authStorage.getSession())
  const [currentUser, setCurrentUser] = useState(null)
  const [isAuthReady, setIsAuthReady] = useState(() => !authStorage.getSession().accessToken)

  const setSession = useCallback(({ accessToken, refreshToken }) => {
    const nextSession = normalizeSession({ accessToken, refreshToken })
    setSessionState(nextSession)
    authStorage.setSession(nextSession)
    if (nextSession.accessToken) {
      setIsAuthReady(false)
    } else {
      setCurrentUser(null)
      setIsAuthReady(true)
    }
  }, [])

  const logout = useCallback(() => {
    setSessionState(normalizeSession())
    setCurrentUser(null)
    setIsAuthReady(true)
    authStorage.clearSession()
  }, [])

  const login = useCallback((tokens) => {
    setSession(tokens)
  }, [setSession])

  const token = session.accessToken
  const role = currentUser?.role || null
  const isAdmin = role === 'admin'

  const authClientStore = useMemo(() => ({
    getAccessToken: () => authStorage.getSession().accessToken,
    getRefreshToken: () => authStorage.getSession().refreshToken,
    setSession,
    clearSession: logout,
  }), [setSession, logout])

  useEffect(() => {
    apiClient.setAuthStore(authClientStore)
  }, [authClientStore])

  useEffect(() => {
    let cancelled = false

    async function loadCurrentUser() {
      if (!token || !isTokenValid(token)) {
        if (session.refreshToken) {
          setIsAuthReady(false)
          const refreshed = await apiClient.refreshSession()
          if (!cancelled && !refreshed) {
            logout()
          }
          return
        }
        if (!cancelled) {
          setCurrentUser(null)
          setIsAuthReady(true)
        }
        return
      }

      setIsAuthReady(false)
      try {
        const user = await authApi.getCurrentUser()
        if (!cancelled) {
          setCurrentUser(user)
          setIsAuthReady(true)
        }
      } catch {
        if (!cancelled) {
          logout()
        }
      }
    }

    loadCurrentUser()

    return () => {
      cancelled = true
    }
  }, [token, session.refreshToken, logout])

  useEffect(() => {
    const interval = setInterval(() => {
      if (token && !isTokenValid(token)) {
        apiClient.refreshSession().then((refreshed) => {
          if (!refreshed) {
            logout()
          }
        })
      }
    }, 30000)
    return () => clearInterval(interval)
  }, [token, logout])

  useEffect(() => {
    const handleStorage = () => {
      const storedSession = authStorage.getSession()
      if (storedSession.accessToken !== session.accessToken || storedSession.refreshToken !== session.refreshToken) {
        setSessionState(storedSession)
        if (!storedSession.accessToken) {
          setCurrentUser(null)
          setIsAuthReady(true)
        }
      }
    }
    window.addEventListener('storage', handleStorage)
    return () => window.removeEventListener('storage', handleStorage)
  }, [session])

  return (
    <AuthContext.Provider value={{ token, refreshToken: session.refreshToken, login, logout, role, isAdmin, setSession, currentUser, isAuthReady }}>
      {children}
    </AuthContext.Provider>
  )
}

function ProtectedRoute({ children }) {
  const { token, isAuthReady } = useAuth()
  if (!isAuthReady) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-950 text-sm font-semibold text-white/80">
        Oturum hazirlaniyor...
      </div>
    )
  }
  return token ? children : <Navigate to="/login" />
}

function AdminRoute({ children }) {
  const { token, isAdmin, isAuthReady } = useAuth()
  if (!isAuthReady) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-950 text-sm font-semibold text-white/80">
        Oturum hazirlaniyor...
      </div>
    )
  }
  if (!token) {
    return <Navigate to="/login" />
  }
  return isAdmin ? children : <Navigate to="/dashboard" />
}

function AppLayout({ children }) {
  return (
    <>
      <Navbar />
      <main className="app-shell">
        <section className="app-container page-surface">
          <div className="premium-divider" />
          {children}
        </section>
      </main>
    </>
  )
}

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<LoginPage />} />

          <Route path="/dashboard" element={
            <ProtectedRoute><AppLayout><Dashboard /></AppLayout></ProtectedRoute>
          } />
          <Route path="/personnel" element={
            <ProtectedRoute><AppLayout><Personnel /></AppLayout></ProtectedRoute>
          } />
          <Route path="/sales" element={
            <ProtectedRoute><AppLayout><Sales /></AppLayout></ProtectedRoute>
          } />
          <Route path="/attendance" element={
            <ProtectedRoute><AppLayout><Attendance /></AppLayout></ProtectedRoute>
          } />
          <Route path="/warnings" element={
            <ProtectedRoute><AppLayout><Warnings /></AppLayout></ProtectedRoute>
          } />
          <Route path="/training" element={
            <ProtectedRoute><AppLayout><Training /></AppLayout></ProtectedRoute>
          } />
          <Route path="/call-process" element={
            <ProtectedRoute><AppLayout><CallProcess /></AppLayout></ProtectedRoute>
          } />
          <Route path="/call-monitoring" element={
            <ProtectedRoute><AppLayout><CallMonitoring /></AppLayout></ProtectedRoute>
          } />
          <Route path="/whatsapp" element={
            <ProtectedRoute><AppLayout><WhatsApp /></AppLayout></ProtectedRoute>
          } />
          <Route path="/users" element={
            <AdminRoute><AppLayout><Users /></AppLayout></AdminRoute>
          } />

          <Route path="/" element={<Navigate to="/dashboard" />} />
          <Route path="*" element={<Navigate to="/dashboard" />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  )
}

export default App
