import { NextResponse } from 'next/server';
import { auth0 } from '../../../lib/auth0';

const BACKEND_URL = process.env.FASTAPI_URL!;

export async function POST(request: Request) {
  try {
    const data = await request.json();
    const { token: accessToken } = await auth0.getAccessToken();

    const backendRes = await fetch(BACKEND_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${accessToken}`
      },
      body: JSON.stringify(data)
    });

    const bodyText = await backendRes.text();
    let backendBody: any = bodyText;

    try {
      backendBody = JSON.parse(bodyText);
    } catch {
      // keep raw text if not JSON
    }

    return NextResponse.json(
      { backendBody },
      { status: backendRes.status }
    );
  } catch (err) {
    console.error('Error in POST /api/calendar:', err);
    return NextResponse.json({ error: 'Bad gateway', message: String(err) }, { status: 502 });
  }
}