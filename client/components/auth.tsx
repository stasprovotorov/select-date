"use client"

import { useEffect, useState } from "react"
import { AuthContext, type AuthState } from "./auth-context"
import { isUserAuthenticated } from "@/lib/api-service"
import loadingMessage from "./ui/loading-message"

const SERVER_API_URL = `${process.env.NEXT_PUBLIC_SERVER_BASE_URL}${process.env.NEXT_PUBLIC_SERVER_API_URL}`

export default function Auth({ children }: { children: React.ReactNode }) {
  const [authState, setAuthState] = useState<AuthState>({ isAuthenticated: false })
  const [isLoading, setLoading] = useState<boolean>(true)

  useEffect(() => {
    let mounted = true

    async function doAuth() {
      try {
        const res = await isUserAuthenticated()

        if (!mounted) return

        if (res.ok) {
          setAuthState({ isAuthenticated: true })
        } else {
          window.location.replace(`${SERVER_API_URL}/auth/login`)
        }

      } catch {
        window.location.replace(`${SERVER_API_URL}/auth/login`)
      } finally {
        if (mounted) setLoading(false)
      }
    }

    doAuth()

    return () => { mounted = false }
  }, [])

  if (isLoading) return loadingMessage("Authorization...")
  if (!authState.isAuthenticated) return null 

  return (
    <AuthContext.Provider value={authState}>
      {children}
    </AuthContext.Provider>
  ) 
}
