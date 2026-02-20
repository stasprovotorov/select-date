const SESSION_STORAGE_KEY = "calendar-app:is-synced"

function getSessionStorage(): Storage | null {
  if (typeof window === "undefined") return null
  return window.sessionStorage
}

export function setCalendarSynced(value: boolean) {
  const storage = getSessionStorage()
  if (!storage) return

  storage.setItem(SESSION_STORAGE_KEY, JSON.stringify(value))
}

export function isCalendarSynced(): boolean {
  const storage = getSessionStorage()
  if (!storage) return false

  const value = storage.getItem(SESSION_STORAGE_KEY)
  if (value === null) return false

  return JSON.parse(value) as boolean
}
