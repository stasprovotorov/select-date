import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function toStrIsoDate(year: number, month: number, day: number): string {
  const yearStr = String(year).padStart(4, '0')
  const monthStr = String(month).padStart(2, '0')
  const dayStr = String(day).padStart(2, '0')
  return `${yearStr}-${monthStr}-${dayStr}`
}

type DateParts = { year: number; month: number; day: number }

export function parseIsoDate(isoDate: string): DateParts {
  const [yearStr, monthStr, dayStr] = isoDate.split("-")
  const year = Number(yearStr)
  const month = Number(monthStr)
  const day = Number(dayStr)
  return { year, month, day}
}
