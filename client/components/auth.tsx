"use client";

import { useUser } from "@auth0/nextjs-auth0"
import { useEffect } from "react"

export default function Auth({ children }: { children: React.ReactNode }) {
  const { user, isLoading } = useUser()

  useEffect(() => {
    if (!isLoading && !user) {
      window.location.href = "/auth/login"
    }
  }, [isLoading, user])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        Authorization...
      </div>
    )
  }

  if (!user) return null 

  return <>{children}</>
}
