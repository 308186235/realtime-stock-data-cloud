// Vercel Edge Function - 健康检查
export default function handler(req, res) {
  res.status(200).json({
    status: "healthy",
    server: "vercel-edge",
    timestamp: new Date().toISOString(),
    message: "Trading System API is running on Vercel"
  });
}
