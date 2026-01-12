"use client"

import { useState, useEffect, useRef } from "react"
import { Button } from "@/components/ui/button"
import { cn, toStrIsoDate, parseIsoDate, getErrorMessage } from "@/lib/utils"
import { sendDateBatch, DateItem, DateOperation } from "@/lib/api-service"
import { useDebounce } from "@/app/api/hooks/use-debounce-batch"
import { useSyncDates } from "./sync-context"

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
  monthIndex: number
  day: number
  colorBg: string
  colorText: string
}

export default function Calendar() {
  const [selectedDates, setSelectedDates] = useState<SelectedDate[]>([])
  const [currentYear, setCurrentYear] = useState(new Date().getFullYear())
  const [selectedColor, setSelectedColor] = useState(colorOptions[0])
  const prevSelectedDatesRef = useRef<SelectedDate[]>([])
  const serverDates = useSyncDates()

  const { bufferRef, bufferDateAndSend, buildToRollback } = useDebounce({
    delay: 700,
    maxBatchSize: 50,
    batchSender: sendDateBatch,
    clearBufferOnBeforeUnload: true
  })

  useEffect(() => {
    const loadDatesFromStorage = () => {
      let storedDates: SelectedDate[] = []

      if (serverDates?.length) {
        for (const serverDate of serverDates) {
          const { year, month, day } = parseIsoDate(serverDate.calendarDate)

          const selectedDate: SelectedDate = {
            year: year,
            monthIndex: month - 1,
            day,
            colorBg: serverDate.colorBg,
            colorText: serverDate.colorText
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
        const message = getErrorMessage(err)
        console.error(`Failed to load dates from localStorage: ${message}`)
      }
    }
    loadDatesFromStorage()
  }, [])

  const saveDatesToStorage = (dates: SelectedDate[]) => {
    try {
      localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(dates))
    } catch (err) {
      const message = getErrorMessage(err)
      console.error(`Failed to save dates to localStorage: ${message}`)
    }
  }

  const toggleDate = async (month: number, day: number) => {
    const isBuffering = Boolean(bufferRef?.current && bufferRef.current.size > 0)
    
    if (!isBuffering) {
      prevSelectedDatesRef.current = [...selectedDates]
    }
    
    const newDate: SelectedDate = {
      year: currentYear,
      monthIndex: month,
      day,
      colorBg: selectedColor.value,
      colorText: selectedColor.textColor,
    }

    const existingDateIndex = selectedDates.findIndex(
      (date) => date.year === currentYear && date.monthIndex === month && date.day === day
    )

    let newSelectedDates: SelectedDate[]
    let operType: "insert" | "delete"

    if (existingDateIndex >= 0) {
      operType = "delete"
      newSelectedDates = selectedDates.filter((_, index) => index !== existingDateIndex)
    } else {
      operType = "insert"
      newSelectedDates = [...selectedDates, newDate]
    }

    setSelectedDates(newSelectedDates)
    saveDatesToStorage(newSelectedDates)

    const dateItem: DateItem = {
      calendarDate: toStrIsoDate(newDate.year, newDate.monthIndex + 1, newDate.day),
      colorBg: newDate.colorBg,
      colorText: newDate.colorText
    }

    const dateOper: DateOperation = { operType, item: dateItem }
    const apiDateResults = await bufferDateAndSend(dateOper)
    const toRollbackDates = buildToRollback(apiDateResults)

    if (toRollbackDates.length !== 0) {
      let rollbackSelectedDates: SelectedDate[] = []
      const toAddDates: SelectedDate[] = []
      const toRemoveDatesIndex = new Set()

      for (const { operType, selectedDate } of toRollbackDates) {
        if (operType === "insert") {
          toRemoveDatesIndex.add(selectedDates.findIndex(
            (date) => 
              date.year === selectedDate.year && 
              date.monthIndex === selectedDate.monthIndex && 
              date.day === selectedDate.day
          ))
        } else if (operType === "delete") { 
          toAddDates.push(selectedDate)
        }
      }

      rollbackSelectedDates = prevSelectedDatesRef.current.filter((_, index) => !toRemoveDatesIndex.has(index))
      rollbackSelectedDates.push(...toAddDates)

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
    return selectedDates.some((date) => date.year === year && date.monthIndex === month && date.day === day)
  }

  const getSelectedDate = (year: number, month: number, day: number) => {
    return selectedDates.find((date) => date.year === year && date.monthIndex === month && date.day === day)
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
            isSelected && selectedDate?.colorBg, // Apply stored color
            isSelected && selectedDate?.colorText, // Apply stored text color
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
