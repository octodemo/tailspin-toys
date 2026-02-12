import type { APIRoute } from 'astro';

const API_SERVER_URL = process.env.API_SERVER_URL || 'http://localhost:5100';

// Catch-all proxy for /api/* requests to the Flask backend.
// Streams request and response bodies to avoid buffering.
export const ALL: APIRoute = async ({ params, request }) => {
  const url = new URL(request.url);
  const targetUrl = `${API_SERVER_URL}/api/${params.path}${url.search}`;

  try {
    const response = await fetch(targetUrl, {
      method: request.method,
      headers: request.headers,
      body: request.method !== 'GET' && request.method !== 'HEAD'
        ? request.body
        : undefined,
    });

    return new Response(response.body, {
      status: response.status,
      statusText: response.statusText,
      headers: response.headers,
    });
  } catch (error) {
    console.error('Error forwarding request to API:', error);
    return new Response(JSON.stringify({ error: 'Failed to reach API server' }), {
      status: 502,
      headers: { 'Content-Type': 'application/json' },
    });
  }
};
