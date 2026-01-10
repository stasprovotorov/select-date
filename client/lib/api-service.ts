import { getErrorMessage } from "./utils"

const CLIENT_API_URL = process.env.NEXT_PUBLIC_CLIENT_API_URL ?? "/api/v1"

export type DateItem = { calendarDate: string, colorBg: string, colorText: string }
export type DateOperation = { operType: "insert" | "delete", item: DateItem }
export type DateBatchRequest = { batch: DateOperation[] }

export type DateOperationResult = 
  | { ok: true, operation: DateOperation }
  | { ok: false, operation: DateOperation, message: string }

export type DateBatchResponse = 
  | { ok: true, result: DateOperationResult[] }
  | { ok: false, message: string }

export async function sendDateBatch(dateBatch: DateBatchRequest): Promise<DateBatchResponse> {
  const url = `${CLIENT_API_URL}/dates/batch`
  const reqBody = JSON.stringify(dateBatch)

  try {
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: reqBody,
      keepalive: true
    })

    if (!res.ok) {
      return { ok: false, message: "The request to submit the batch of items with dates failed." }
    }

    try {
      const resBody = await res.json()

      return resBody
    } catch {
      return { ok: false, message: "Failed to parse response body as JSON from the server." }
    }
  } catch (err) {
    const message = getErrorMessage(err)
    return { ok: false, message }
  }
}

export type DateByUserResponse = 
  | { ok: true, item: DateItem[] }
  | { ok: false, message: string }

export async function getDateByUser(): Promise<DateByUserResponse> {
  const url = `${CLIENT_API_URL}/users/me/dates`

  try {
    const res = await fetch(url, { method: "GET" })
    
    if (!res.ok) {
      return { ok: false, message: "Failed to retrieve the user's date items." }
    }
  
    try {
      const body = await res.json()
      return body
    } catch {
      return { ok: false, message: "Failed to parse response body as JSON from the server." }
    }
    
  } catch (err) {
    const message = getErrorMessage(err)
    return { ok: false, message }
  }
}
