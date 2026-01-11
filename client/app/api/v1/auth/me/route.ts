const SERVER_API_URL = process.env.SERVER_API_URL

if (!SERVER_API_URL) {
  throw new Error("Missing required environment variable: SERVER_API_URL.")
}

export async function GET(req: Request): Promise<Response> {
  const url = `${SERVER_API_URL}/auth/me`
  const cookie = req.headers.get("Cookie")
  const headers = new Headers()

  if (cookie) {
    headers.set("Cookie", cookie)
  }

  return await fetch(url, {
    method: req.method,
    headers,
    credentials: "include"
  })
}
