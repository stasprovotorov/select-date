import { useCallback, useEffect, useRef } from "react"
import { type DateOperation, type DateBatchRequest, type DateBatchResponse } from "../../../lib/api-service"
import { type SelectedDate } from "../../../components/calendar"
import { parseIsoDate, getErrorMessage } from "../../../lib/utils"

type DateBuffer = { countForDate: number; lastDate: DateOperation }
type DateRollback = { operType: "insert" | "delete", selectedDate: SelectedDate }

type useDebounceOptions = {
  delay: number
  maxBatchSize: number
  clearBufferOnBeforeUnload: boolean
  batchSender: ((batch: DateBatchRequest) => DateBatchResponse | Promise<DateBatchResponse>)
}

export function useDebounce({ delay, maxBatchSize, clearBufferOnBeforeUnload, batchSender }: useDebounceOptions) {
  const bufferRef = useRef<Map<string, DateBuffer>>(new Map())
  const batchRef = useRef<DateOperation[]>([])
  const batchSenderRef = useRef(batchSender)
  const timerRef = useRef<number | undefined>(undefined)
  
  useEffect(() => {
    batchSenderRef.current = batchSender
  }, [batchSender])

  const clearTimer = useCallback(() => {
    if (timerRef.current !== undefined) {
      window.clearTimeout(timerRef.current)
      timerRef.current = undefined
    }
  }, [])

  const buildBatchFromBuffer = useCallback(() => {
    batchRef.current = [] 
    for (const [_, { countForDate, lastDate }] of bufferRef.current.entries()) {
      if (countForDate % 2 === 1) batchRef.current.push(lastDate)
    }
  }, [])

  const flushBufferAndSend = useCallback((): DateBatchResponse | Promise<DateBatchResponse> => {
    clearTimer()
    buildBatchFromBuffer()

    if (batchRef.current.length === 0) {
      const message = "Batch is empty after building. Nothing to send to the API."
      return { ok: true, result: [], message }
    }
    
    const batch: DateBatchRequest = { batch: batchRef.current }
    const sendBatch = batchSenderRef.current

    async function doSendBatch() {
      try {
        const res = await sendBatch(batch)
        if (res.ok) bufferRef.current.clear()
        return res
      } catch (err) {
        const message = getErrorMessage(err)
        throw new Error(`Failed to send batch request: ${message}`)
      }
    }

    return doSendBatch()
  }, [buildBatchFromBuffer, clearTimer])

  const scheduleFlushBufferAndSend = useCallback(async (): Promise<DateBatchResponse> => {
    clearTimer()

    return new Promise((resolve, reject) => {
      timerRef.current = window.setTimeout(() => {
        timerRef.current = undefined
        
        try {
          const res = flushBufferAndSend()
          resolve(res)
        } catch (err) {
          const message = getErrorMessage(err)
          reject(new Error(`Failed to schedule batch send request: ${message}`))
        }

      }, delay) as unknown as number
    })
  }, [clearTimer, delay, flushBufferAndSend])

  const bufferDateAndSend = useCallback(
    (dateOper: DateOperation): DateBatchResponse | Promise<DateBatchResponse> => { 
      const keyDate = dateOper.item.calendarDate
      const dateExistBuffer = bufferRef.current.get(keyDate)

      if (dateExistBuffer) {
        dateExistBuffer.countForDate += 1
        dateExistBuffer.lastDate = dateOper
        bufferRef.current.set(keyDate, dateExistBuffer)
      } else {
        const dateToBuffer: DateBuffer = { countForDate: 1, lastDate: dateOper }
        bufferRef.current.set(keyDate, dateToBuffer)
      }

      async function doSend() {
        if (maxBatchSize && bufferRef.current.size >= maxBatchSize) {
          return await flushBufferAndSend()
        } else {
          return await scheduleFlushBufferAndSend()
        }
      }
  
      return doSend()
    }, [maxBatchSize, flushBufferAndSend, scheduleFlushBufferAndSend]
  )

  const buildToRollback = useCallback((res: DateBatchResponse): Array<DateRollback> => {
      let toRollback = []

      if (!res.ok) {
        for (const dateOper of batchRef.current) {
          const dateItem = dateOper.item
          const { year, month, day } = parseIsoDate(dateItem.calendarDate)

          const toRollbackItem: SelectedDate = {
            year: year,
            monthIndex: month - 1,
            day: day,
            colorBg: dateItem.colorBg,
            colorText: dateItem.colorText
          }

          toRollback.push({ operType: dateOper.operType, selectedDate: toRollbackItem })
        }
      } else {
        for (const dateOperRes of res.result) {
          if (!dateOperRes.ok) {
            const dateOper = dateOperRes.operation
            const dateItem = dateOper.item
            const { year, month, day } = parseIsoDate(dateItem.calendarDate)

            const toRollbackItem: SelectedDate = {
              year: year,
              monthIndex: month - 1,
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
      bufferRef.current.clear() 
    }
    
    window.addEventListener("pagehide", clearBufferIfTabClosed)
    window.addEventListener("beforeunload", clearBufferIfTabClosed)

    return () => {
      window.removeEventListener("pagehide", clearBufferIfTabClosed)
      window.removeEventListener("beforeunload", clearBufferIfTabClosed)
      clearTimer()
    }
  }, [clearBufferOnBeforeUnload, clearTimer])

  return { bufferRef, bufferDateAndSend, buildToRollback }
}
