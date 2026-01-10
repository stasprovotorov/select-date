"use client"

import React, { useEffect, useState, ReactElement, useRef, useContext } from "react"
import { getDateByUser, type DateItem } from "../lib/api-service"
import { SyncContext } from "./sync-context"
import { AuthContext } from "./auth-context"
import { getErrorMessage } from "@/lib/utils"

type SyncProps = { children: ReactElement }

const SESSION_STORAGE_KEY = "calendar-app:is-synced"
const SESSION_STORAGE_VALUE = "true"

export default function Sync({ children }: SyncProps) {
  const ranRef = useRef(false)
  const { isAuthenticated } = useContext(AuthContext)
  const [dates, setDates] = useState<DateItem[] | null>(null)

  const [wasSynced, setWasSynced] = useState<boolean>(() => {
    try {
      return sessionStorage.getItem(SESSION_STORAGE_KEY) === SESSION_STORAGE_VALUE
    } catch {
      return false
    }
  })
  
  useEffect(() => {
    if (!isAuthenticated) return
    if (wasSynced) return
    if (ranRef.current) return
    ranRef.current = true

    async function doSync() {
      try {
        const res = await getDateByUser()

        if (!res.ok) {
          throw new Error(`Falied synchronization: ${res.message}`)
        }

        setDates(res.item)
        sessionStorage.setItem(SESSION_STORAGE_KEY, SESSION_STORAGE_VALUE)
        setWasSynced(true)
      } catch (err) {
        const message = getErrorMessage(err)
        throw new Error(`Falied synchronization: ${message}`)
      }
    }

    doSync()
  }, [isAuthenticated, wasSynced])

  if (!wasSynced) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <p className="font-sans text-foreground text-base">Synchronization...</p>
      </div>
    )
  }

  return (
    <SyncContext.Provider value={dates}>
      {children}
    </SyncContext.Provider>
  )
}
