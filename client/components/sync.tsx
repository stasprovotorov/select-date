"use client"

import React, { useEffect, useState, ReactElement, useRef, useContext } from "react"
import { getDateByUser, type DateItem } from "../lib/api-service"
import { SyncContext } from "./sync-context"
import { AuthContext } from "./auth-context"
import { getErrorMessage } from "@/lib/utils"
import { setCalendarSynced, isCalendarSynced } from "@/lib/storage"
import loadingMessage from "./ui/loading-message"

type SyncProps = { children: ReactElement }

export default function Sync({ children }: SyncProps) {
  const ranRef = useRef(false)
  const { isAuthenticated } = useContext(AuthContext)
  const [dates, setDates] = useState<DateItem[] | null>(null)
  const [wasSynced, setWasSynced] = useState<boolean>(isCalendarSynced())

  useEffect(() => {
    const onHide = () => {
      setCalendarSynced(false)
      setWasSynced(false)
    }
    window.addEventListener("pagehide", onHide)
    return () => {
      window.removeEventListener("pagehide", onHide)
    }
  }, [])

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
        setCalendarSynced(true)
        setWasSynced(true)

      } catch (err) {
        const message = getErrorMessage(err)
        throw new Error(`Falied synchronization: ${message}`)
      }
    }

    doSync()
  }, [isAuthenticated, wasSynced])

  if (!wasSynced) return loadingMessage("Synchronization...")

  return (
    <SyncContext.Provider value={dates}>
      {children}
    </SyncContext.Provider>
  )
}
