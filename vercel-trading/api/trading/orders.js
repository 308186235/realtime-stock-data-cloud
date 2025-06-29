// Vercel Edge Function - 交易订单
export default function handler(req, res) {
  // 设置CORS头
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  if (req.method === 'GET') {
    // 获取订单列表
    const ordersData = {
      orders: [
        {
          order_id: "VCL20250629001",
          symbol: "000001",
          name: "平安银行",
          type: "buy",
          quantity: 1000,
          price: 12.50,
          status: "filled",
          time: "2025-06-29 09:30:15",
          commission: 5.00
        },
        {
          order_id: "VCL20250629002", 
          symbol: "600000",
          name: "浦发银行",
          type: "buy",
          quantity: 2000,
          price: 8.80,
          status: "filled",
          time: "2025-06-29 10:15:30",
          commission: 8.80
        },
        {
          order_id: "VCL20250629003",
          symbol: "000002",
          name: "万科A",
          type: "buy", 
          quantity: 1500,
          price: 15.20,
          status: "pending",
          time: "2025-06-29 14:25:00",
          commission: 0.00
        }
      ],
      total_orders: 3,
      pending_orders: 1,
      filled_orders: 2,
      server: "vercel-edge",
      timestamp: new Date().toISOString()
    };

    res.status(200).json(ordersData);
  } 
  else if (req.method === 'POST') {
    // 提交新订单
    const orderData = req.body || {};
    const newOrderId = `VCL${new Date().toISOString().replace(/[-:T.]/g, '').slice(0, 14)}`;
    
    const response = {
      status: "success",
      message: "订单已提交到Vercel处理",
      order_id: newOrderId,
      order_data: {
        ...orderData,
        status: "pending",
        submit_time: new Date().toISOString(),
        commission: (orderData.quantity * orderData.price * 0.0003).toFixed(2)
      },
      server: "vercel-edge",
      timestamp: new Date().toISOString()
    };

    res.status(200).json(response);
  }
}
