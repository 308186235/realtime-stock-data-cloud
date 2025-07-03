// 禁用模拟数据的API函数
exports.handler = async (event, context) => {
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Content-Type': 'application/json'
  };

  if (event.httpMethod === 'OPTIONS') {
    return { statusCode: 200, headers, body: '' };
  }

  const errorResponse = {
    error: "REAL_DATA_REQUIRED",
    message: "❌ 系统禁止返回模拟数据",
    required_action: "请配置真实交易数据源",
    timestamp: new Date().toISOString()
  };

  return {
    statusCode: 400,
    headers,
    body: JSON.stringify(errorResponse, null, 2)
  };
};
