"use client"

import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import { setCalendarSynced } from "@/lib/storage"

export default function SignOutButton(): JSX.Element {
  const base = "absolute right-4"
  const layout = "flex items-center gap-2"
  const visuals = "!bg-white !text-foreground hover:!bg-gray-200"
  const focus = "focus:!ring-2 focus:!ring-offset-2 focus:!ring-gray-200"

  const handleSignOut = async () => {
    setCalendarSynced(false)

    const res = await fetch("/api/v1/auth/logout", {
      method: "POST",
      credentials: "include"
    })
    
    const { redirectTo } = await res.json() 
    window.location.href = redirectTo
  }

  return (
    <Button
      variant="outline"
      size="sm"
      onClick={handleSignOut}
      aria-label="Sign out"
      style={{ top: "calc(env(safe-area-inset-top, 0px) + 6mm)" }}
      className={cn(base, layout, visuals, focus)}
    >
      <span>Sign Out</span>
    </Button>
  )
}
