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

// Convert date to ISO string format (YYYY-MM-DD)
function toStrIsoDate(date: SelectedDate): string {
  const year = String(date.year).padStart(4, '0')
  const month = String(date.month).padStart(2, '0')
  const day = String(date.day).padStart(2, '0')
  return `${year}-${month}-${day}`
}

// Common function to make calendar API requests
async function makeCalendarRequest(
  date: SelectedDate,
  method: 'POST' | 'DELETE',
  body?: string
): Promise<ApiResult> {
  const strIsoDate = encodeURIComponent(toStrIsoDate(date))
  const url = `/api/calendar/${strIsoDate}`

  const headers: HeadersInit = {}
  if (body) {
    headers['Content-Type'] = 'application/json'
  }

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
  return makeCalendarRequest(date, 'POST', JSON.stringify(date))
}

// Deselect a date (DELETE)
export async function deselectDate(date: SelectedDate): Promise<ApiResult> {
  return makeCalendarRequest(date, 'DELETE')
}

