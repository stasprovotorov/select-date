"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import { stat } from "fs"

const months = [
  "January",
  "February",
  "March",
  "April",
  "May",
  "June",
  "July",
  "August",
  "September",
  "October",
  "November",
  "December",
]

const daysOfWeek = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

const colorOptions = [
  { name: "Blue", value: "bg-blue-500 hover:bg-blue-600", textColor: "text-white" },
  { name: "Green", value: "bg-green-500 hover:bg-green-600", textColor: "text-white" },
  { name: "Red", value: "bg-red-500 hover:bg-red-600", textColor: "text-white" },
  { name: "Purple", value: "bg-purple-500 hover:bg-purple-600", textColor: "text-white" },
  { name: "Orange", value: "bg-orange-500 hover:bg-orange-600", textColor: "text-white" },
  { name: "Pink", value: "bg-pink-500 hover:bg-pink-600", textColor: "text-white" },
  { name: "Yellow", value: "bg-yellow-500 hover:bg-yellow-600", textColor: "text-black" },
  { name: "Teal", value: "bg-teal-500 hover:bg-teal-600", textColor: "text-white" },
]

interface SelectedDate {
  year: number
  month: number
  day: number
  color?: string // Added optional color property
  textColor?: string // Added text color for contrast
}

function toStrIsoDate(date: SelectedDate) {
  const year = String(date.year).padStart(4, '0')
  const month = String(date.month).padStart(2, '0')
  const day = String(date.day).padStart(2, '0')
  return `${year}-${month}-${day}`
}

export default function Calendar() {
  const [selectedDates, setSelectedDates] = useState<SelectedDate[]>([])
  const [currentYear, setCurrentYear] = useState(new Date().getFullYear())
  const [selectedColor, setSelectedColor] = useState(colorOptions[0]) // Added selected color state

  useEffect(() => {
    const loadDatesFromStorage = () => {
      try {
        const storedDates = localStorage.getItem("calendar-selected-dates")
        if (storedDates) {
          const dates = JSON.parse(storedDates)
          setSelectedDates(dates)
        }
      } catch (error) {
        console.error("Error loading dates from localStorage:", error)
      }
    }

    loadDatesFromStorage()
  }, [])

  const saveDatesToStorage = (dates: SelectedDate[]) => {
    try {
      localStorage.setItem("calendar-selected-dates", JSON.stringify(dates))
    } catch (error) {
      console.error("Error saving dates to localStorage:", error)
    }
  }

  type Json = null | boolean | number | string | Json[] | { [key: string]: Json }
  type sendCalendarChangeResult =
    | { ok: true; status: number; data: Json | null }
    | { ok: false; status: number; error: string }

  async function sendCalendarChange(date: SelectedDate, method: "POST" | "DELETE"): Promise<sendCalendarChangeResult> {
    const strIsoDate = encodeURIComponent(toStrIsoDate(date))
    const url = `/api/calendar/${strIsoDate}`

    let reqInit: RequestInit
    if (method === "POST") {
      reqInit = {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(date)
      }
    } else {
      reqInit = { method }
    }

    try {
      const res = await fetch(url, reqInit)
      const status = res.status
      if (status === 204) {
        return { ok: true, status, data: null}
      } else {
        const data = await res.json()
        return res.ok ? {ok: true, status, data} : { ok: false, status, error: String(data)}
      }
    } catch (err: any) {
      return { ok: false, status: 0, error: String(err?.message ?? err) }
    }
  }

  const toggleDate = async (month: number, day: number) => {
    const existingDateIndex = selectedDates.findIndex(
      (date) => date.year === currentYear && date.month === month && date.day === day,
    )

    const newDate: SelectedDate = {
      year: currentYear,
      month,
      day,
      color: selectedColor.value, // Store selected color with date
      textColor: selectedColor.textColor, // Store text color for contrast
    }
    const prevDates = [...selectedDates]; // Save current dates state for rollback

    let newDates: SelectedDate[]
    let calendarChangeReqMethod: "POST" | "DELETE";

    if (existingDateIndex >= 0) {
      newDates = selectedDates.filter((_, index) => index !== existingDateIndex)
      calendarChangeReqMethod = "DELETE"
    } else {
      newDates = [...selectedDates, newDate]
      calendarChangeReqMethod = "POST"
    }

    setSelectedDates(newDates)
    saveDatesToStorage(newDates)

    try {
      const res = await sendCalendarChange(newDate, calendarChangeReqMethod)
      if (!res.ok) {
        throw new Error("Server synchronization error!")
      }
    } catch (err) {
      setSelectedDates(prevDates) // rollback
      saveDatesToStorage(prevDates)
      alert(err)
    }
  }

  const getDaysInMonth = (month: number, year: number) => {
    return new Date(year, month + 1, 0).getDate()
  }

  const getFirstDayOfMonth = (month: number, year: number) => {
    const firstDay = new Date(year, month, 1).getDay()
    return firstDay === 0 ? 6 : firstDay - 1
  }

  const isDateSelected = (year: number, month: number, day: number) => {
    return selectedDates.some((date) => date.year === year && date.month === month && date.day === day)
  }

  const getSelectedDate = (year: number, month: number, day: number) => {
    return selectedDates.find((date) => date.year === year && date.month === month && date.day === day)
  }

  const renderMonth = (monthIndex: number) => {
    const daysInMonth = getDaysInMonth(monthIndex, currentYear)
    const firstDay = getFirstDayOfMonth(monthIndex, currentYear)
    const days = []

    for (let i = 0; i < firstDay; i++) {
      days.push(<div key={`empty-${i}`} className="h-12 w-12" />)
    }

    for (let day = 1; day <= daysInMonth; day++) {
      const selectedDate = getSelectedDate(currentYear, monthIndex, day) // Get full selected date object
      const isSelected = !!selectedDate

      days.push(
        <Button
          key={day}
          variant={isSelected ? "default" : "ghost"}
          size="sm"
          className={cn(
            "h-12 w-12 p-0 font-normal transition-all duration-200 hover:scale-105 rounded-full",
            isSelected && selectedDate?.color, // Apply stored color
            isSelected && selectedDate?.textColor, // Apply stored text color
          )}
          onClick={() => toggleDate(monthIndex, day)}
        >
          <span className="text-sm">{day}</span>
        </Button>,
      )
    }

    return (
      <div key={monthIndex} className="space-y-4">
        <h2 className="text-lg font-semibold text-center text-foreground">
          {months[monthIndex]} {currentYear}
        </h2>
        <div className="space-y-2">
          <div className="grid grid-cols-7 gap-1">
            {daysOfWeek.map((day) => (
              <div key={day} className="h-8 flex items-center justify-center">
                <span className="text-xs font-medium text-muted-foreground">{day}</span>
              </div>
            ))}
          </div>
          <div className="grid grid-cols-7 gap-1">{days}</div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background p-4">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-4 mb-4">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setCurrentYear((prev) => prev - 1)}
              className="flex items-center gap-2"
            >
              ← {currentYear - 1}
            </Button>
            <h1 className="text-4xl font-bold text-foreground">{currentYear}</h1>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setCurrentYear((prev) => prev + 1)}
              className="flex items-center gap-2"
            >
              {currentYear + 1} →
            </Button>
          </div>

          <div className="mb-4">
            <p className="text-sm text-muted-foreground mb-3">Choose a color for new labels:</p>
            <div className="flex items-center justify-center gap-2 flex-wrap">
              {colorOptions.map((color) => (
                <Button
                  key={color.name}
                  size="sm"
                  className={cn(
                    "h-8 w-8 p-0 rounded-full border-2 transition-all duration-200",
                    color.value,
                    selectedColor.name === color.name
                      ? "ring-2 ring-offset-2 ring-foreground scale-110"
                      : "hover:scale-105",
                  )}
                  onClick={() => setSelectedColor(color)}
                  title={color.name}
                />
              ))}
            </div>
            <p className="text-xs text-muted-foreground mt-2">Selected: {selectedColor.name}</p>
          </div>

          <p className="text-muted-foreground">Click on any date to set or unset a label</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8">
          {months.map((_, index) => renderMonth(index))}
        </div>
      </div>
    </div>
  )
}
