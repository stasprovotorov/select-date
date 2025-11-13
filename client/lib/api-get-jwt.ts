// Function to obtain an access token from the Auth0 API as a JWT

const DOMAIN = process.env.AUTH0_DOMAIN || ''
const CLIENT_ID = process.env.AUTH0_CLIENT_ID || ''
const CLIENT_SECRET = process.env.AUTH0_CLIENT_SECRET || ''
const AUDIENCE = process.env.AUTH0_AUDIENCE || ''

type Auth0JwtResponse = {
  access_token: string
  expires_in: number
  token_type: string
}

export async function getJwt(): Promise<string> {
  if (!DOMAIN || !CLIENT_ID || !CLIENT_SECRET || !AUDIENCE) {
    throw new Error('Missing Auth0 configuration')
  }

  const url = `${DOMAIN}/oauth/token`
  const payload = {
    client_id: CLIENT_ID,
    client_secret: CLIENT_SECRET,
    audience: AUDIENCE,
    grant_type: 'client_credentials'
  }

  try {
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })

    if (!res.ok) {
      throw new Error(`Get Auth0 JWT error! Respose status: ${res.status}`)
    }

    let data: Auth0JwtResponse

    try {
      data = await res.json()
    } catch {
      throw new Error(`Invalid JSON from Auth0: ${res.text()}`)
    }

    if (!data.access_token) {
      throw new Error('Auth0 response missing access_token')
    }

    return data.access_token
  } catch (err: unknown) {
    throw err
  }
}
