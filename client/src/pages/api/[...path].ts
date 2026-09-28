import type { APIRoute } from 'astro';

const API_SERVER_URL = process.env.API_SERVER_URL || 'http://localhost:5100';

const METHODS_WITHOUT_BODY = new Set(['GET', 'HEAD']);

// Catch-all proxy for /api/* requests to the Flask backend.
// Streams request and response bodies to avoid buffering.
export const ALL: APIRoute = async ({ params, request }) => {
  const url = new URL(request.url);
  const targetUrl = `${API_SERVER_URL}/api/${params.path}${url.search}`;
  const hasBody = !METHODS_WITHOUT_BODY.has(request.method);

  try {
    const response = await fetch(targetUrl, {
      method: request.method,
      headers: request.headers,
      body: hasBody ? request.body : undefined,
      // Streaming a request body through undici requires an explicit duplex mode.
      ...(hasBody ? { duplex: 'half' } : {}),
    } as RequestInit);

    const headers = new Headers(response.headers);

    // Headers collapses duplicate set-cookie values, so re-apply them
    // individually to keep the admin session cookie intact.
    const setCookies = response.headers.getSetCookie?.() ?? [];
    if (setCookies.length > 0) {
      headers.delete('set-cookie');
      for (const cookie of setCookies) {
        headers.append('set-cookie', cookie);
      }
    }

    return new Response(response.body, {
      status: response.status,
      statusText: response.statusText,
      headers,
    });
  } catch (error) {
    console.error('Error forwarding request to API:', error);
    return new Response(JSON.stringify({ error: 'Failed to reach API server' }), {
      status: 502,
      headers: { 'Content-Type': 'application/json' },
    });
  }
};
