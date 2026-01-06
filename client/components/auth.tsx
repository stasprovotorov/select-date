"use client"

import { useEffect, useState } from "react"
import { AuthContext, type AuthState } from "./auth-context"

const CLIENT_URL = process.env.CLIENT_URL || ""
const SERVER_URL = process.env.SERVER_URL || ""
const SERVER_LOGIN_ENDPOINT = `${SERVER_URL}/api/v1/auth/login`

export default function Auth({ children }: { children: React.ReactNode }) {
  const [authState, setAuthState] = useState<AuthState>({ isAuthenticated: false, user: null})
  const [isLoading, setLoading] = useState(true)

  useEffect(() => {
    (async () => {
      try {
        const res = await fetch("api/v1/auth/me", { credentials: "include" })
        if (res.ok) {
          const user = await res.json()
          setAuthState({ isAuthenticated: true, user })
        } else {
          window.location.href = SERVER_LOGIN_ENDPOINT
        }
      } catch {
        window.location.href = SERVER_LOGIN_ENDPOINT
      } finally {
        setLoading(false)
      }
    })()
  }, [])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        Authorization...
      </div>
    )
  }

  if (!authState.isAuthenticated) return null 

  return (
    <AuthContext.Provider value={authState}>
      {children}
    </AuthContext.Provider>
  ) 
}
