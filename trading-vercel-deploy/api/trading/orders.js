// 交易订单API
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
      summary: {
        total_orders: 8,
        pending_orders: 1,
        filled_orders: 6,
        cancelled_orders: 1,
        today_orders: 3
      },
      orders: [
        {
          order_id: "VCL20250629001",
          symbol: "000001",
          name: "平安银行",
          direction: "buy",
          order_type: "limit",
          quantity: 1000,
          price: 13.85,
          filled_quantity: 1000,
          filled_price: 13.82,
          status: "filled",
          submit_time: "2025-06-29 09:30:15",
          filled_time: "2025-06-29 09:30:18",
          commission: 4.15,
          amount: 13820.00
        },
        {
          order_id: "VCL20250629002",
          symbol: "600000",
          name: "浦发银行",
          direction: "buy",
          order_type: "limit",
          quantity: 2000,
          price: 9.45,
          filled_quantity: 2000,
          filled_price: 9.43,
          status: "filled",
          submit_time: "2025-06-29 10:15:30",
          filled_time: "2025-06-29 10:15:35",
          commission: 5.66,
          amount: 18860.00
        },
        {
          order_id: "VCL20250629003",
          symbol: "000002",
          name: "万科A",
          direction: "buy",
          order_type: "limit",
          quantity: 1500,
          price: 13.60,
          filled_quantity: 0,
          filled_price: 0.00,
          status: "pending",
          submit_time: "2025-06-29 14:25:00",
          filled_time: null,
          commission: 0.00,
          amount: 20400.00
        },
        {
          order_id: "VCL20250629004",
          symbol: "600519",
          name: "贵州茅台",
          direction: "sell",
          order_type: "market",
          quantity: 10,
          price: 0.00,
          filled_quantity: 10,
          filled_price: 1728.50,
          status: "filled",
          submit_time: "2025-06-29 11:20:10",
          filled_time: "2025-06-29 11:20:12",
          commission: 5.19,
          amount: 17285.00
        }
      ],
      server: "vercel-edge",
      timestamp: new Date().toISOString()
    };

    res.status(200).json(ordersData);
  } 
  else if (req.method === 'POST') {
    // 提交新订单
    const orderData = req.body || {};
    const newOrderId = `VCL${new Date().toISOString().replace(/[-:T.]/g, '').slice(0, 14)}`;
    
    // 计算手续费（万分之三）
    const amount = (orderData.quantity || 0) * (orderData.price || 0);
    const commission = Math.max(amount * 0.0003, 5.00); // 最低5元

    const response = {
      status: "success",
      message: "订单已成功提交到Vercel交易系统",
      order_info: {
        order_id: newOrderId,
        symbol: orderData.symbol || "",
        name: orderData.name || "",
        direction: orderData.direction || "buy",
        order_type: orderData.order_type || "limit",
        quantity: orderData.quantity || 0,
        price: orderData.price || 0.00,
        amount: amount,
        commission: commission.toFixed(2),
        status: "pending",
        submit_time: new Date().toISOString(),
        estimated_fill_time: new Date(Date.now() + 30000).toISOString() // 预计30秒后成交
      },
      server: "vercel-edge",
      timestamp: new Date().toISOString()
    };

    res.status(200).json(response);
  }
}
