import { getJwt } from '../../../../lib/api-get-jwt'

const BACKEND_URL = process.env.FASTAPI_URL || ''
if (!BACKEND_URL) {
  throw new Error('Missing required environment variable FASTAPI_URL in .env.local')
}

export async function POST(request: Request): Promise<Response> {
  const backendURL = `${BACKEND_URL}/batch`
  const authToken = await getJwt()
  const jsonBody = await new Response(request.body).json()
  const strJsonBody = JSON.stringify({ batch: jsonBody })
  const bodyLen = Buffer.byteLength(strJsonBody)
  const headers = new Headers(request.headers)
  
  headers.set('Authorization', `Bearer ${authToken}`)
  headers.set('Content-Type', 'application/json')
  headers.set('Content-Length', String(bodyLen))

  return await fetch(backendURL, {
    method: request.method,
    headers,
    body: strJsonBody
  })
}
