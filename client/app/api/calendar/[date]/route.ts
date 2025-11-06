import { auth0 } from '../../../../lib/auth0'

const BACKEND_URL = process.env.FASTAPI_URL || ''
if (!BACKEND_URL) {
  throw new Error('Missing required environment variable FASTAPI_URL in .env.local')
}

export async function POST(
  request: Request, 
  { params }: { params: Promise<{ date: string }> }
) {
  const { token: authToken } = await auth0.getAccessToken()
  const { date: dateID } = await params
  const fullBackendURL = `${BACKEND_URL}/calendar/${encodeURIComponent(dateID)}`
  const dateData = await request.json()
  const dateDataJsonText = JSON.stringify(dateData)

  try {
    const backendRes = await fetch(fullBackendURL, 
      {
        method: "POST",
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${authToken}`
        },
        body: dateDataJsonText
      }
    )

    return new Response(dateDataJsonText, { status: backendRes.status })

  } catch (err) {
    console.error(`Error in POST with route: ${fullBackendURL}\n`, err)

    return new Response(
      JSON.stringify({ error: 'Bad gateway' }),
      { 
        status: 502, 
        headers: { 'Content-Type': 'application/json' }
      }
    )
  }
}

export async function DELETE(
  _request: Request, 
  { params }: { params: Promise<{ date: string }> }
) {
  const { token: authToken } = await auth0.getAccessToken()
  const { date: dateID } = await params
  const fullBackendURL = `${BACKEND_URL}/calendar/${encodeURIComponent(dateID)}`

  try {
    const backendRes = await fetch(
      fullBackendURL, 
      { 
        method: "DELETE",
        headers: { 'Authorization': `Bearer ${authToken}` } 
      }
    )

    return new Response(null, { status: backendRes.status })

  } catch (err) {
    console.error(`Error in DELETE with route: ${fullBackendURL}\n`, err)

    return new Response(
      JSON.stringify({ error: 'Bad gateway' }),
      {
        status: 502,
        headers: { 'Content-Type': 'application/json' }
      }
    )
  }
}
