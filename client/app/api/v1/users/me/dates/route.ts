const SERVER_API_URL = process.env.SERVER_URL

export async function GET(req: Request): Promise<Response> {
  const url = `${SERVER_API_URL}/users/me/dates`
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
