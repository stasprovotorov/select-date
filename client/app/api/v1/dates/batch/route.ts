const SERVER_API_URL = process.env.SERVER_API_URL

if (!SERVER_API_URL) {
  throw new Error("Missing required environment variable: SERVER_API_URL.")
}

export async function POST(req: Request): Promise<Response> {
  const url = `${SERVER_API_URL}/dates/batch`

  const body = await req.json()
  const bodyStr = JSON.stringify(body)
  const bodyLen = String(Buffer.byteLength(bodyStr))

  const cookie = req.headers.get("Cookie")

  const headers = new Headers()
  headers.set("Content-Type", "application/json")
  headers.set('Content-Length', bodyLen)
  if (cookie) {
    headers.set("Cookie", cookie)
  }

  return await fetch(url, { 
    method: req.method, 
    headers, 
    body: bodyStr 
  })
}
