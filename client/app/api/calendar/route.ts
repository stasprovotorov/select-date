import { NextResponse } from 'next/server'
import { getJwt } from '../../../lib/api-get-jwt'

const BACKEND_URL = process.env.FASTAPI_URL || ''
if (!BACKEND_URL) {
  throw new Error('Missing required environment variable FASTAPI_URL in .env.local')
}

async function handleRequest(request: Request): Promise<Response> {
  const backendURL = `${BACKEND_URL}/calendar`
  
  // Copy headers from client request
  const headers = new Headers(request.headers)

  // Get token and set Authorization header
  const authToken = await getJwt()
  headers.set('Authorization', `Bearer ${authToken}`)

  // Get JSON body and new bodylength
  const jsonBody = await new Response(request.body).json()
  const strJsonBody = JSON.stringify(jsonBody)
  const bodyLen = Buffer.byteLength(strJsonBody)
  
  // Set Content-Type and new Content-Length headers 
  headers.set('Content-Type', 'application/json')
  headers.set('Content-Length', String(bodyLen))

  // Proxy request to backend
  return await fetch(backendURL, {
    method: request.method,
    headers,
    body: strJsonBody
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

export async function DELETE(request: Request) {
  try {
    return await handleRequest(request)
  } catch (err) {
    return handleError(err, 'DELETE')
  }
}
