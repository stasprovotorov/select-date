const SERVER_API_URL = process.env.SERVER_URL

export async function POST(req: Request): Promise<Response> {
  const url = `${SERVER_API_URL}/auth/logout`
  const cookie = req.headers.get("Cookie")
  const headers = new Headers()
  
  if (cookie) {
    headers.set("Cookie", cookie)
  }

  return await fetch(url, { 
    method: req.method,
    headers
  })
}
