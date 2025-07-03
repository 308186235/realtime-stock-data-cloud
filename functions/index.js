// Cloudflare Pages Functions Entry Point
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
    message: "🚀 Cloudflare Pages Functions 已激活！",
    available_endpoints: [
      "/api/health",
      "/api/test",
      "/api/account-balance",
      "/api/account-positions",
      "/api/agent-analysis",
      "/api/real-stock-api",
      "/api/quotes"
    ],
    timestamp: new Date().toISOString(),
    platform: "Cloudflare Pages"
  }), {
    headers: corsHeaders
  });
}
