export type DateItem = { calendarDate: string, colorBg: string, colorText: string }
export type DateOperation = { operType: "insert" | "delete", item: DateItem }
export type DateOperationResult = { ok: boolean, operation: DateOperation, message: string | null }
export type DateBatchRequest = { batch: DateOperation[] }
export type DateBatchResponse = { ok: boolean, results: DateOperationResult[], message: string | null }
export type DatesByUser = { ok: boolean, items: DateItem[], message?: string }

export async function sendDateBatchToApi(dateBatch: DateBatchRequest): Promise<DateBatchResponse> {
  const bodyReq = JSON.stringify(dateBatch)

  try {
    const response = await fetch("/api/v1/dates/batch", {
      method: "POST",
      headers: { "Content-Type": "application/json"},
      body: bodyReq,
      keepalive: true
    })

    if (!response.ok) {
      return { ok: false, results: [], message: `HTTP ${response.status}`}
    }

    let bodyRes: DateBatchResponse
    try {
      bodyRes = await response.json()
    } catch {
      return { ok: false, results: [], message: "Invalid JSON from server API"}
    }

    return bodyRes
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err)
    return { ok: false, results: [], message }
  }
}

export async function getDatesForUser(): Promise<DatesByUser> {
  try {
    const response = await fetch("/api/v1/dates/sync", { method: "GET" })
    let body: DatesByUser

    try {
      body = await response.json()
    } catch {
      return { ok: false, items: [], message: "Invalid JSON from server API"}
    }

    if (!response.ok) {
      return { ok: false, items: [], message: body.message }
    }
  
    return body
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err)
    return { ok: false, items: [], message: message }
  }
}
