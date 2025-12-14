import { useCallback, useEffect, useRef } from "react"
import { type ApiDateBatchResult } from "../../../lib/api-service"
import { SelectedDate } from "../../../components/calendar"
import { parseIsoDate } from "../../../lib/utils"

export type DateBatchItem = {
  action: "select" | "deselect"
  date: string
  color?: string
  textColor?: string
}

type DateBufferItem = { countForDate: number; lastDate: DateBatchItem }

type useDebounceBatchOptions = {
  delay: number
  maxBatchSize?: number
  dateBatchSender: ((payload: DateBatchItem[]) => ApiDateBatchResult | Promise<ApiDateBatchResult>)
  clearBufferOnBeforeUnload: boolean
}

export function useDebounceBatch({ 
  delay, 
  maxBatchSize, 
  dateBatchSender, 
  clearBufferOnBeforeUnload = true 
}: useDebounceBatchOptions) {
  const dateBufferRef = useRef<Map<string, DateBufferItem>>(new Map())
  const dateBatchRef = useRef<DateBatchItem[]>([])
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
  const flushBufferAndSend = useCallback((): ApiDateBatchResult | Promise<ApiDateBatchResult> => {
    clearTimer()
    buildBatchFromBuffer()
    dateBufferRef.current.clear()

    let apiResponse: ApiDateBatchResult | Promise<ApiDateBatchResult>

    // If the batch is empty (no useful data to send), skip sending a request to the server
    if (dateBatchRef.current.length === 0) {
      const message = "Batch is empty after building. Nothing to send to API"
      apiResponse = { ok: true, results: [], message }
      return apiResponse
    }

    const sendDateBatchToApi = dateBatchSenderRef.current
    apiResponse = sendDateBatchToApi(dateBatchRef.current)
    return apiResponse
  }, [buildBatchFromBuffer, clearTimer])

  /**
   * Wait for the timer to elapse, build a batch of operations from the buffer, clear the buffer, 
   * and send the batch to the server API.
   */
  const scheduleFlushBufferAndSend = useCallback(async (): Promise<ApiDateBatchResult> => {
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
    (dateBatchItem: DateBatchItem): ApiDateBatchResult | Promise<ApiDateBatchResult> => { 
      const keyDate = dateBatchItem.date
      const dateExistBuffer = dateBufferRef.current.get(keyDate)
      let apiResponse: ApiDateBatchResult | Promise<ApiDateBatchResult>

      if (dateExistBuffer) {
        dateExistBuffer.countForDate += 1
        dateExistBuffer.lastDate = dateBatchItem
        dateBufferRef.current.set(keyDate, dateExistBuffer)
      } else {
        const dateToBuffer: DateBufferItem = {
          countForDate: 1,
          lastDate: dateBatchItem
        }
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
    (apiResponse: ApiDateBatchResult): Array<[string, SelectedDate]> => {
      let toRollback: Array<[string, SelectedDate]> = []

      if (!apiResponse.ok) {
        // Build the rollback array based on the HTTP response to the request
        for (const dateItem of dateBatchRef.current) {
          const { year, month, day } = parseIsoDate(dateItem.date)

          const toRollbackItem: SelectedDate = {
            year: year,
            month: month,
            day: day,
            color: dateItem?.color,
            textColor: dateItem?.textColor
          }

          toRollback.push([dateItem.action, toRollbackItem])
        }
      } else {
        // Build the rollback array based on each item's API response
        for (const dateItem of apiResponse.results) {
          if (!dateItem.ok) {
            const { year, month, day } = parseIsoDate(dateItem.date)

            const toRollbackItem: SelectedDate = {
              year: year,
              month: month,
              day: day,
              color: dateItem?.color,
              textColor: dateItem?.textColor
            }

            toRollback.push([dateItem.action, toRollbackItem])
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
