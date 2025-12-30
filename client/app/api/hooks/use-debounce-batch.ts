import { useCallback, useEffect, useRef } from "react"
import { type DateOperation, type DateBatchRequest, type DateBatchResponse } from "../../../lib/api-service"
import { SelectedDate } from "../../../components/calendar"
import { parseIsoDate } from "../../../lib/utils"

type DateBuffer = { countForDate: number; lastDate: DateOperation }
type DateRollback = Array<{ operType: string, selectedDate: SelectedDate }>

type useDebounceBatchOptions = {
  delay: number
  maxBatchSize?: number
  dateBatchSender: ((payload: DateBatchRequest) => DateBatchResponse | Promise<DateBatchResponse>)
  clearBufferOnBeforeUnload: boolean
}

export function useDebounceBatch({ 
  delay, 
  maxBatchSize, 
  dateBatchSender, 
  clearBufferOnBeforeUnload = true 
}: useDebounceBatchOptions) {
  const dateBufferRef = useRef<Map<string, DateBuffer>>(new Map())
  const dateBatchRef = useRef<DateOperation[]>([])
  const dateBatchSenderRef = useRef(dateBatchSender)
  const timerRef = useRef<number | undefined>(undefined)
  
  useEffect(() => {
    dateBatchSenderRef.current = dateBatchSender
  }, [dateBatchSender])

  const clearTimer = useCallback(() => {
    if (timerRef.current !== undefined) {
      window.clearTimeout(timerRef.current)
      timerRef.current = undefined
    }
  }, [])

  /**
   * Build a batch of date operations to be sent to the server API.
   */
  const buildBatchFromBuffer = useCallback(() => {
    // Clear batch
    dateBatchRef.current = [] 

    // Add only useful actions to the batch
    for (const [, { countForDate, lastDate }] of dateBufferRef.current.entries()) {
      if (countForDate % 2 === 1) {
        dateBatchRef.current.push(lastDate)
      }
    }
  }, [])

  /**
   * Build a batch of operations from the buffer, clear the buffer, and send the batch to the server API.
   */
  const flushBufferAndSend = useCallback((): DateBatchResponse | Promise<DateBatchResponse> => {
    clearTimer()
    buildBatchFromBuffer()
    dateBufferRef.current.clear()

    let apiResponse: DateBatchResponse | Promise<DateBatchResponse>

    // If the batch is empty (no useful data to send), skip sending a request to the server
    if (dateBatchRef.current.length === 0) {
      const message = "Batch is empty after building. Nothing to send to API."
      apiResponse = { ok: true, results: [], message }
      return apiResponse
    }

    const sendDateBatchToApi = dateBatchSenderRef.current
    const batchForSend: DateBatchRequest = { batch: dateBatchRef.current }
    apiResponse = sendDateBatchToApi(batchForSend)
    return apiResponse
  }, [buildBatchFromBuffer, clearTimer])

  /**
   * Wait for the timer to elapse, build a batch of operations from the buffer, clear the buffer, 
   * and send the batch to the server API.
   */
  const scheduleFlushBufferAndSend = useCallback(async (): Promise<DateBatchResponse> => {
    clearTimer()
    return new Promise((resolve, reject) => {
      timerRef.current = window.setTimeout(() => {
        timerRef.current = undefined
        try {
          const apiResponse = flushBufferAndSend()
          resolve(apiResponse)
        } catch (err) {
          const message = "scheduleFlushBufferAndSend(): Execution flushBufferAndSend() failed!"
          const wrapped_err = new Error(message) as any
          wrapped_err.originalError = err
          reject(wrapped_err)
        }
      }, delay) as unknown as number
    })
  }, [clearTimer, delay, flushBufferAndSend])

  /**
   * Add date item into buffer to be sent to server API.
   */
  const bufferDateForSending = useCallback(
    (dateOper: DateOperation): DateBatchResponse | Promise<DateBatchResponse> => { 
      const keyDate = dateOper.item.calendarDate
      const dateExistBuffer = dateBufferRef.current.get(keyDate)
      let apiResponse: DateBatchResponse | Promise<DateBatchResponse>

      if (dateExistBuffer) {
        dateExistBuffer.countForDate += 1
        dateExistBuffer.lastDate = dateOper
        dateBufferRef.current.set(keyDate, dateExistBuffer)
      } else {
        const dateToBuffer: DateBuffer = { countForDate: 1, lastDate: dateOper }
        dateBufferRef.current.set(keyDate, dateToBuffer)
      }

      if (maxBatchSize && dateBufferRef.current.size >= maxBatchSize) {
        apiResponse = flushBufferAndSend()
      } else {
        apiResponse = scheduleFlushBufferAndSend()
      }
      
      return apiResponse
    }, [maxBatchSize, flushBufferAndSend, scheduleFlushBufferAndSend]
  )

  /**
   * // Build an array of dates to be rolled back based on the server API response.
   */
  const buildToRollback = useCallback(
    (apiResponse: DateBatchResponse): DateRollback => {
      let toRollback: DateRollback = []

      if (!apiResponse.ok) {
        // Build the rollback array based on the HTTP response to the request
        for (const dateOper of dateBatchRef.current) {
          const dateItem = dateOper.item
          const { year, month, day } = parseIsoDate(dateItem.calendarDate)

          const toRollbackItem: SelectedDate = {
            year: year,
            monthIndex: month,
            day: day,
            colorBg: dateItem.colorBg,
            colorText: dateItem.colorText
          }

          toRollback.push({ operType: dateOper.operType, selectedDate: toRollbackItem })
        }
      } else {
        // Build the rollback array based on each item's API response
        for (const dateOperRes of apiResponse.results) {
          if (!dateOperRes.ok) {
            const dateOper = dateOperRes.operation
            const dateItem = dateOper.item
            const { year, month, day } = parseIsoDate(dateItem.calendarDate)

            const toRollbackItem: SelectedDate = {
              year: year,
              monthIndex: month,
              day: day,
              colorBg: dateItem.colorBg,
              colorText: dateItem.colorText
            }

            toRollback.push({ operType: dateOper.operType, selectedDate: toRollbackItem })
          }
        }
      }
      return toRollback
    }, []
  )

  useEffect(() => {
    if (!clearBufferOnBeforeUnload) return

    const clearBufferIfTabClosed = () => { 
      clearTimer()
      dateBufferRef.current.clear() 
    }
    window.addEventListener("pagehide", clearBufferIfTabClosed)
    window.addEventListener("beforeunload", clearBufferIfTabClosed)

    return () => {
      window.removeEventListener("pagehide", clearBufferIfTabClosed)
      window.removeEventListener("beforeunload", clearBufferIfTabClosed)
      clearTimer()
    }
  }, [clearBufferOnBeforeUnload, clearTimer])

  return { dateBufferRef, bufferDateForSending, buildToRollback }
}
