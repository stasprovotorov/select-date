// API service for calendar operations
// Encapsulates all HTTP request logic

import { BatchItem } from "@/app/api/hooks/use-debounce"
import { text } from "stream/consumers"

export interface SelectedDate {
  year: number
  month: number
  day: number
  color?: string
  textColor?: string
}

// Convert date to ISO string format (YYYY-MM-DD)
function toStrIsoDate(date: SelectedDate): string {
  const year = String(date.year).padStart(4, '0')
  const month = String(date.month).padStart(2, '0')
  const day = String(date.day).padStart(2, '0')
  return `${year}-${month}-${day}`
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

export async function sendCalendarBatch(items: BatchItem[]): Promise<void> {
  const payload = items.map((item) => ({
    action: item.action,
    date: item.date,
    color: item.color,
    textColor: item.textColor,
    operId: item.operId
  }))

  const body = JSON.stringify(payload)

  try {
    const res = await fetch("api/calendar/batch", {
      method: "POST",
      headers: { "Content-Type": "application/json"},
      body
    })
  } catch (error) {
    console.error(error)
  }
}
