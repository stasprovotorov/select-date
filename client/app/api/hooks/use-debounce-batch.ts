import { useCallback, useEffect, useRef } from "react";
import { type ApiDateBatchResult } from "../../../lib/api-service"

export type DateBatchItem = {
  action: "select" | "deselect"
  date: string
  color?: string
  textColor?: string
}

type BufferDate = { countForDate: number; lastDate: DateBatchItem }

type useDebounceBatchOptions = {
  delay: number
  maxBatchSize?: number
  datesBatchSender: ((payload: DateBatchItem[]) => ApiDateBatchResult | Promise<ApiDateBatchResult>)
  clearBufferOnBeforeUnload?: boolean
}

export function useDebounceBatch({ 
  delay, 
  maxBatchSize, 
  datesBatchSender, 
  clearBufferOnBeforeUnload = true 
}: useDebounceBatchOptions) {
  const datesBufferRef = useRef<Map<string, BufferDate>>(new Map())
  const timerRef = useRef<number | undefined>(undefined)
  const datesBatchSenderRef = useRef(datesBatchSender)

  useEffect(() => {
    datesBatchSenderRef.current = datesBatchSender
  }, [datesBatchSender])

  const clearTimer = useCallback (() => {
    if (timerRef.current !== undefined) {
      window.clearTimeout(timerRef.current)
      timerRef.current = undefined
    }
  }, [])

  const buildPayloadFromBuffer = useCallback((): DateBatchItem[] => {
    const payload: DateBatchItem[] = []
    for (const [, { countForDate, lastDate }] of datesBufferRef.current.entries()) {
      if (countForDate % 2 === 1) {
        payload.push(lastDate)
      }
    }
    return payload
  }, [])

  const flushBufferAndSend = useCallback((): ApiDateBatchResult | Promise<ApiDateBatchResult> => {
    clearTimer()
    const payload = buildPayloadFromBuffer()
    datesBufferRef.current.clear()
    const sendDatesBatchToApi = datesBatchSenderRef.current
    const apiResponse = sendDatesBatchToApi(payload)
    return apiResponse
  }, [buildPayloadFromBuffer, clearTimer])

  const scheduleFlushBufferAndSend = useCallback((): Promise<ApiDateBatchResult> => {
    clearTimer()
    return new Promise((resolve, reject) => {
      timerRef.current = window.setTimeout(() => {
        timerRef.current = undefined
        try {
          const apiResponse = flushBufferAndSend()
          resolve(apiResponse)
        } catch (err) {
          const message = "scheduleFlushBufferAndSend: Execution flushBufferAndSend failed"
          const wrapped_err = new Error(message) as any
          wrapped_err.originalError = err
          reject(wrapped_err)
        }
      }, delay) as unknown as number
    })
  }, [clearTimer, delay, flushBufferAndSend])

  const bufferDateForSending = useCallback(
    (dateBatchItem: DateBatchItem): ApiDateBatchResult | Promise<ApiDateBatchResult> => { 
      const keyDate = dateBatchItem.date
      const dateExistBuffer = datesBufferRef.current.get(keyDate)
      let apiResponse: ApiDateBatchResult | Promise<ApiDateBatchResult>

      if (dateExistBuffer) {
        dateExistBuffer.countForDate += 1
        dateExistBuffer.lastDate = dateBatchItem
        datesBufferRef.current.set(keyDate, dateExistBuffer)
      } else {
        const dateToBuffer: BufferDate = {
          countForDate: 1,
          lastDate: dateBatchItem
        }
        datesBufferRef.current.set(keyDate, dateToBuffer)
      }

      if (maxBatchSize && datesBufferRef.current.size >= maxBatchSize) {
        apiResponse = flushBufferAndSend()
      } else {
        apiResponse = scheduleFlushBufferAndSend()
      }
      
      return apiResponse
    }, [maxBatchSize, flushBufferAndSend, scheduleFlushBufferAndSend]
  )

  useEffect(() => {
    if (!clearBufferOnBeforeUnload) return

    const clearBufferIfTabClosed = () => { 
      clearTimer()
      datesBufferRef.current.clear() 
    }
    window.addEventListener("pagehide", clearBufferIfTabClosed)
    window.addEventListener("beforeunload", clearBufferIfTabClosed)

    return () => {
      window.removeEventListener("pagehide", clearBufferIfTabClosed)
      window.removeEventListener("beforeunload", clearBufferIfTabClosed)
      clearTimer()
    }
  }, [clearBufferOnBeforeUnload, clearTimer])

  return { bufferDateForSending }
}
