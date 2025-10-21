import { NextResponse } from 'next/server';
import { auth0 } from '../../../lib/auth0';

export async function POST(request: Request) {
  const data = await request.json();
  const { token: accessToken } = await auth0.getAccessToken();

  const backendRes = await fetch("http://127.0.0.1:8000/calendar", {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': accessToken
    },
    body: JSON.stringify(data),
  });

  // Here will be code to send POST request to Fast API when it will be ready
  // Now it's just a print in conlose
  console.log(accessToken);
  console.log(data);
  return NextResponse.json({ received: data });
}
