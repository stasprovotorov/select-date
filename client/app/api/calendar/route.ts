import { NextResponse } from 'next/server'
import { getJwt } from '../../../lib/api-get-jwt'

const BACKEND_URL = process.env.FASTAPI_URL || ''
if (!BACKEND_URL) {
  throw new Error('Missing required environment variable FASTAPI_URL in .env.local')
}

async function handleRequest(request: Request): Promise<Response> {
  const authToken = await getJwt()
  const backendURL = `${BACKEND_URL}/calendar`
  
  // Copy headers from client request
  const headers = new Headers(request.headers)
  
  // Add/override Authorization header
  headers.set('Authorization', `Bearer ${authToken}`)
  
  // Proxy request to backend
  return fetch(backendURL, {
    method: request.method,
    headers,
    body: request.body // Proxy body directly as stream, no parsing/serialization
  })
}

function handleError(err: unknown, method: string): NextResponse {
  console.error(`Error in ${method} /api/calendar:`, err)
  return NextResponse.json(
    { error: 'Bad gateway' },
    { status: 502 }
  )
}

export async function POST(request: Request) {
  try {
    return await handleRequest(request)
  } catch (err) {
    return handleError(err, 'POST')
  }
}

export async function DELETE(
  request: Request,
  context: { params: Promise<{ date: string }> }
) {
  try {
    return await handleRequest(request)
  } catch (err) {
    return handleError(err, 'DELETE')
  }
}
