import React from "react"
import { type DateBatchItem } from "@/app/api/hooks/use-debounce-batch"

export type ServerDatesContextValue = DateBatchItem[] | null

export const SyncContext = React.createContext<ServerDatesContextValue>(null)

export function useSyncDates() {
    return React.useContext(SyncContext)
}
