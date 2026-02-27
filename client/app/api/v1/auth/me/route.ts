const SERVER_BASE_URL = process.env.NEXT_PUBLIC_SERVER_BASE_URL ?? "http://localhost:8000"
const SERVER_API_URL = `${SERVER_BASE_URL}${process.env.NEXT_PUBLIC_SERVER_API_URL}`

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
