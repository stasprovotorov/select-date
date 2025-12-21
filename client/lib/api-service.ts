import { type DateBatchItem } from "@/app/api/hooks/use-debounce-batch"

export type ApiDateItemResult = {
  ok: boolean
  action: "select" | "deselect"
  date: string
  color?: string
  textColor?: string
  message?: string
}

export type ApiDateBatchResult = 
 | { ok: true; results: ApiDateItemResult[]; message?: string }
 | { ok: false; message: string }

export async function sendDateBatchToApi(dateBatch: DateBatchItem[]): Promise<ApiDateBatchResult> {
  const payload = dateBatch.map((dateItem) => ({
    action: dateItem.action,
    date: dateItem.date,
    color: dateItem.action === "select" ? dateItem.color : undefined,
    textColor: dateItem.action === "select" ? dateItem.textColor : undefined
  }))

  const bodyReq = JSON.stringify(payload)

  try {
    const response = await fetch("api/calendar/batch", {
      method: "POST",
      headers: { "Content-Type": "application/json"},
      body: bodyReq,
      keepalive: true
    })

    if (!response.ok) {
      return { ok: false, message: `HTTP ${response.status}`}
    }

    let bodyRes: ApiDateBatchResult
    try {
      bodyRes = await response.json()
    } catch {
      return { ok: false, message: "Invalid JSON from server API"}
    }

    return bodyRes
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err)
    return { ok: false, message }
  }
}

type getDatesForUserResult = 
 | { ok: true, dates: DateBatchItem[]}
 | { ok: false, message: string }

export async function getDatesForUser(): Promise<getDatesForUserResult> {
  try {
    const response = await fetch("api/calendar/sync", { method: "GET" })

    if (!response.ok) {
      return { ok: false, message: `HTTP ${response.status}`}
    }

    let body: getDatesForUserResult
    try {
      body = await response.json()
    } catch {
      return { ok: false, message: "Invalid JSON from server API"}
    }

    return body
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err)
    return { ok: false, message }
  }
}
