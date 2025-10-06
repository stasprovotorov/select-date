import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  const data = await request.json();
  // Here will be code to send POST request to Fast API when it will be ready
  // Now it's just a print in conlose
  console.log("Данные календаря:", data);
  return NextResponse.json({ received: data });
}
