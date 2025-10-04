import { auth0 } from '../../../lib/auth0';


export async function GET(request: Request) {
  try {
    const { token: accessToken } = await auth0.getAccessToken();

    console.log(accessToken);

    return new Response(JSON.stringify({ accessToken }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' }
    });
  } catch (error: any) {
    return new Response(JSON.stringify({ error: error.message }), {
      status: error.status || 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}