// API service for calendar operations
// Encapsulates all HTTP request logic

export interface SelectedDate {
  year: number
  month: number
  day: number
  color?: string
  textColor?: string
}

type ApiResult<T = unknown> =
  | { ok: true; data: T | null }
  | { ok: false; error: string }

// Common function to make calendar API requests
async function makeCalendarRequest(
  method: 'POST' | 'DELETE',
  body: string
): Promise<ApiResult> {
  const url = '/api/calendar'
  const headers: HeadersInit = { 'Content-Type': 'application/json' }

  try {
    const res = await fetch(url, {
      method,
      headers,
      body
    })

    if (!res.ok) {
      const error = await res.json().catch(() => ({ error: 'Unknown error' }))
      return { ok: false, error: String(error) }
    }

    const data = res.status === 204 ? null : await res.json().catch(() => null)
    return { ok: true, data }
  } catch (err: unknown) {
    return { ok: false, error: err instanceof Error ? err.message : String(err) }
  }
}

// Select a date (POST)
export async function selectDate(date: SelectedDate): Promise<ApiResult> {
  return makeCalendarRequest('POST', JSON.stringify(date))
}

// Deselect a date (DELETE)
export async function deselectDate(date: SelectedDate): Promise<ApiResult> {
  return makeCalendarRequest('DELETE', JSON.stringify(date))
}
