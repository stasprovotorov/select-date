// Function to obtain an access token from the Auth0 API as a JWT.

type Auth0JwtResponse = {
  access_token: string
  expires_in: number
  token_type: string
}

export async function getJwt(): Promise<string> {
  const domain = process.env.AUTH0_DOMAIN || ''
  const clientId = process.env.AUTH0_CLIENT_ID || ''
  const clientSecret = process.env.AUTH0_CLIENT_SECRET || ''
  const audience = process.env.AUTH0_AUDIENCE || ''

  if (!domain || !clientId || !clientSecret || !audience) {
    throw new Error('Missing Auth0 configuration')
  }

  const url = `${domain}/oauth/token`
  const payload = {
    client_id: clientId,
    client_secret: clientSecret,
    audience,
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
