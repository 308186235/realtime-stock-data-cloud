export async function onRequest(context) {
  const corsHeaders = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Content-Type': 'application/json'
  };

  // Handle CORS preflight
  if (context.request.method === 'OPTIONS') {
    return new Response('', { headers: corsHeaders });
  }

  return new Response(JSON.stringify({
    message: "✅ Cloudflare Pages Functions 工作正常！",
    timestamp: new Date().toISOString(),
    method: context.request.method,
    url: context.request.url,
    platform: "Cloudflare Pages"
  }), {
    headers: corsHeaders
  });
}
