import { getJwt } from '../../../../../lib/api-get-jwt'

const BACKEND_URL = process.env.FASTAPI_URL || ''
if (!BACKEND_URL) {
  throw new Error('Missing required environment variable FASTAPI_URL in .env.local')
}

export async function GET(request: Request): Promise<Response> {
  const backendURL = `${BACKEND_URL}/api/v1/users/me/dates`
  const authToken = await getJwt()
  const headers = new Headers(request.headers)
  
  headers.set('Authorization', `Bearer ${authToken}`)

  return await fetch(backendURL, {
    method: request.method,
    headers
  })
}
