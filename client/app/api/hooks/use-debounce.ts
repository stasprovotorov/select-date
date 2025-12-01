import { flushCompileCache } from "module";
import { useCallback, useEffect, useRef } from "react";

export type BatchItem = {
  action: "select" | "deselect"
  date: string
  color?: string
  textColor?: string
  operId?: number
}

export type Options = {
  delay?: number
  maxBatchSize?: number
  onFlush?: (items: BatchItem[]) => void | Promise<void>
  flushOnBeforeUnload?: boolean
}

export function useDebounceBatch({
  delay = 700,
  maxBatchSize,
  onFlush,
  flushOnBeforeUnload = true
}: Options) {
  const bufferRef = useRef<Map<string, {count: number; lastItem: BatchItem}>>(new Map())
  const timerRef = useRef<number | undefined>(undefined)
  const onFlushRef = useRef(onFlush)

  useEffect(() => {
    onFlushRef.current = onFlush
  }, [onFlush])

  const clearTimer = useCallback (() => {
    if (timerRef.current !== undefined) {
      window.clearTimeout(timerRef.current)
      timerRef.current = undefined
    }
  }, [])

  const getBufferedCount = useCallback(() => bufferRef.current.size, [])

  const buildFlushPayload = useCallback((): BatchItem[] => {
    const out: BatchItem[] = []
    for (const [date, { count, lastItem }] of bufferRef.current.entries()) {
      if (count % 2 === 1) {
        out.push(lastItem)
      }
    }
    return out
  }, [])

  const doFlush = useCallback(() => {
    clearTimer()
    if (!bufferRef.current.size) return
    const payload = buildFlushPayload()
    bufferRef.current.clear()
    const fn = onFlushRef.current
    if (fn && payload.length > 0) {
      void fn(payload)
    }
  }, [buildFlushPayload, clearTimer])

  const scheduleFlush = useCallback(() => {
    clearTimer()
    timerRef.current = window.setTimeout(() => {
      timerRef.current = undefined
      doFlush()
    }, delay) as unknown as number
  }, [clearTimer, delay, doFlush])

  const addEvent = useCallback((item: BatchItem | BatchItem[]) => {
    const items = Array.isArray(item) ? item : [item]
    for (const it of items) {
      const key = it.date
      const existing = bufferRef.current.get(key)
      if (existing) {
        existing.count += 1
        existing.lastItem = it
        bufferRef.current.set(key, existing)
      } else {
        bufferRef.current.set(key, { count: 1, lastItem: it})
      }
    }

    if (maxBatchSize && bufferRef.current.size >= maxBatchSize) {
        doFlush()
        return
    }

    scheduleFlush()
  }, [doFlush, maxBatchSize, scheduleFlush])

  const flush = useCallback(() => {
    doFlush()
  }, [doFlush])

  const cancel = useCallback(() => {
    clearTimer()
    bufferRef.current.clear()
  }, [clearTimer])

  useEffect(() => {
    if (!flushOnBeforeUnload) return

    const handler = () => { doFlush() }
    window.addEventListener("beforeunload", handler)

    return () => {
      window.addEventListener("beforeunload", handler)
      doFlush()
      clearTimer()
    }
  }, [clearTimer, doFlush, flushOnBeforeUnload])

  const peekBuffered = useCallback(() => {
    const res: { date: string; count: number; lastItem: BatchItem }[] = []
    for (const [date, v] of bufferRef.current.entries()) {
      res.push({ date, count: v.count, lastItem: v.lastItem })
    }
    return res
  }, [])

  return { addEvent, flush, cancel, getBufferedCount, peekBuffered }
}
