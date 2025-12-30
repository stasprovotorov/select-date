import React from "react"
import { type DateItem } from "../lib/api-service"

export type ServerDatesContextValue = DateItem[] | null

export const SyncContext = React.createContext<ServerDatesContextValue>(null)

export function useSyncDates() {
    return React.useContext(SyncContext)
}
