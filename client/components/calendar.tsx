"use client"

import { useState, useEffect, useRef } from "react"
import { Button } from "@/components/ui/button"
import { cn, toStrIsoDate, parseIsoDate } from "@/lib/utils"
import { sendDateBatchToApi } from "@/lib/api-service"
import { useDebounceBatch, type DateBatchItem } from "@/app/api/hooks/use-debounce-batch"

const LOCAL_STORAGE_KEY = "calendar-selected-dates"

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

export type SelectedDate = {
  year: number
  month: number
  day: number
  color?: string
  textColor?: string
}

type CalendarProps = { serverDates?: DateBatchItem[] | null }

export default function Calendar({ serverDates = null }: CalendarProps) {
  const [selectedDates, setSelectedDates] = useState<SelectedDate[]>([])
  const [currentYear, setCurrentYear] = useState(new Date().getFullYear())
  const [selectedColor, setSelectedColor] = useState(colorOptions[0])
  const prevSelectedDatesRef = useRef<SelectedDate[]>([])

  // Initialize debounce batch hook to buffer date changes and send them to the API 
  const { dateBufferRef, bufferDateForSending, buildToRollback } = useDebounceBatch({
    delay: 700,
    maxBatchSize: 50,
    dateBatchSender: sendDateBatchToApi,
    clearBufferOnBeforeUnload: true
  })

  useEffect(() => {
    const loadDatesFromStorage = () => {
      let storedDates: SelectedDate[] = []

      if (serverDates?.length) {
        for (const serverDate of serverDates) {
          const { year, month, day } = parseIsoDate(serverDate.date)

          const selectedDate: SelectedDate = {
            year: year,
            month: month - 1,
            day,
            color: serverDate.color,
            textColor: serverDate.textColor
          }

          storedDates.push(selectedDate)
        }
        setSelectedDates(storedDates)
        return
      }

      try {
        const storedDates = localStorage.getItem(LOCAL_STORAGE_KEY)
        if (storedDates) {
          const dates = JSON.parse(storedDates)
          setSelectedDates(dates)
        }
      } catch (err) {
        console.error("Error loading dates from localStorage:", err)
      }
    }

    loadDatesFromStorage()
  }, [])

  const saveDatesToStorage = (dates: SelectedDate[]) => {
    try {
      localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(dates))
    } catch (error) {
      console.error("Error saving dates to localStorage:", error)
    }
  }

  const toggleDate = async (month: number, day: number) => {
    // If is not bufferind, freeze previous state of Сalendar
    const isBuffering = Boolean(dateBufferRef?.current && dateBufferRef.current.size > 0)
    if (!isBuffering) {
      prevSelectedDatesRef.current = [...selectedDates]
    }
    
    const newDate: SelectedDate = {
      year: currentYear,
      month,
      day,
      color: selectedColor.value,
      textColor: selectedColor.textColor,
    }

    // Find index of the newDate in selectedDates, or -1 if not found
    const existingDateIndex = selectedDates.findIndex(
      (date) => date.year === currentYear && date.month === month && date.day === day
    )

    let newSelectedDates: SelectedDate[]
    let action: "select" | "deselect"

    // Determine action for newDate and construct updated selectedDates as newSelectedDates
    if (existingDateIndex >= 0) {
      action = "deselect"
      newSelectedDates = selectedDates.filter((_, index) => index !== existingDateIndex)
    } else {
      action = "select"
      newSelectedDates = [...selectedDates, newDate]
    }

    // Provide optimistic updates for the user
    setSelectedDates(newSelectedDates)
    saveDatesToStorage(newSelectedDates)

    const dateToBuffer: DateBatchItem = {
      action: action,
      date: toStrIsoDate(newDate.year, newDate.month, newDate.day),
      color: action === "select" ? newDate.color : undefined,
      textColor: action == "select" ? newDate.textColor : undefined
    }

    // Buffer the new date for sending to the API when the debounce timer expires
    const apiDateResults = await bufferDateForSending(dateToBuffer)
    
    // Build an array of dates to rollback based on negative API responses
    const toRollbackDates = buildToRollback(apiDateResults)

    // Rollback optimistic updates if toRollbackDates is not empty
    if (toRollbackDates.length !== 0) {
      let rollbackSelectedDates: SelectedDate[] = []
      const toAddDates: SelectedDate[] = []
      const toRemoveDatesIndex = new Set()

      // Group dates by action to determine rollback operations
      for (const [action, rollbackDate] of toRollbackDates) {
        if (action === "select") {
          toRemoveDatesIndex.add(selectedDates.findIndex(
            (date) => 
              date.year === rollbackDate.year && 
              date.month === rollbackDate.month && 
              date.day === rollbackDate.day
          ))
        } else if (action === "deselect") { 
          toAddDates.push(rollbackDate)
        }
      }

      // Build updated selectedDates by removing dates marked for rollback (failed "select" actions)
      rollbackSelectedDates = prevSelectedDatesRef.current.filter((_, index) => !toRemoveDatesIndex.has(index))
      // Re-add dates that failed to be removed on the server (rollback failed "deselect" actions)
      rollbackSelectedDates.push(...toAddDates)

      // Apply rollback
      setSelectedDates(rollbackSelectedDates)
      saveDatesToStorage(rollbackSelectedDates) 
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
