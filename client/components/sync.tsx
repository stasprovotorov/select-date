"use client"

import React, { useEffect, useState, ReactElement, useRef } from "react"
import { getDatesForUser } from "../lib/api-service"
import { type DateBatchItem } from "@/app/api/hooks/use-debounce-batch"
import { SyncContext } from "./sync-context"

type SyncProps = { children: ReactElement }

const SESSION_STORAGE_KEY = "isCalendarSynced"
const SESSION_STORAGE_VALUE = "true"

export default function Sync({ children }: SyncProps) {
  const [dates, setDates] = useState<DateBatchItem[] | null>(null)
  const isMountedRef = useRef(true)

  useEffect(() => {
    isMountedRef.current = true
    const wasSynced = sessionStorage.getItem(SESSION_STORAGE_KEY) === SESSION_STORAGE_VALUE

    async function doSync() {
      if (!wasSynced) {
        try {
        const serverResult = await getDatesForUser()
        if (!serverResult.ok) {
          throw new Error(`Synchronization request failed: ${serverResult.detail}`)
        }

        if (!isMountedRef.current) {
          return { serverDates: null }
        }

        setDates(serverResult.dates)
        sessionStorage.setItem(SESSION_STORAGE_KEY, SESSION_STORAGE_VALUE)
        } catch (err) {
          console.error("Synchronization failed (server API):", err)
        }
      }

      return { serverDates: null }
    }

    doSync()

    return () => { isMountedRef.current = false }
  }, [])

  if (dates === null) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        Synchronization...
      </div>
    )
  }
  
  return (
    <SyncContext.Provider value={dates}>
      {children}
    </SyncContext.Provider>
  )
}
