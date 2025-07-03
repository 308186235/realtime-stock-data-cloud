// API配置文件 - Cloudflare配置
// 统一的API基础URL配置

// API基础URL - 使用Cloudflare域名
const API_BASE_URL = 'http://localhost:9999';

// 茶股帮数据源配置
const CHAGUBANG_CONFIG = {
  enabled: true,
  baseUrl: API_BASE_URL,
  endpoints: {
    health: '/api/chagubang/health',
    stocks: '/api/chagubang/stocks',
    market: '/api/chagubang/market/overview',
    hot: '/api/chagubang/market/hot',
    search: '/api/chagubang/search',
    stats: '/api/chagubang/stats',
    tokenAdd: '/api/chagubang/token/add',
    tokenTest: '/api/chagubang/token/test'
  },
  cache: {
    enabled: true,
    ttl: 5000 // 5秒缓存
  }
};

// WebSocket URL
const WS_BASE_URL = 'wss://api.aigupiao.me/ws';

// API端点配置
const API_ENDPOINTS = {
  // 健康检查
  health: '/api/health',
  
  // 市场数据
  market: {
    stocks: '/api/market/stocks',
    quote: '/api/market/quote',
    status: '/api/market/status'
  },
  
  // 账户相关
  account: {
    balance: '/api/account/balance',
    positions: '/api/account/positions',
    orders: '/api/account/orders'
  },
  
  // Agent相关
  agent: {
    status: '/api/agent/status',
    analysis: '/api/agent/analysis',
    trading: '/api/agent/trading'
  },

  // 茶股帮实时数据
  chagubang: {
    health: '/api/chagubang/health',
    stocks: '/api/chagubang/stocks',
    stock: '/api/chagubang/stocks',
    market: '/api/chagubang/market/overview',
    hot: '/api/chagubang/market/hot',
    search: '/api/chagubang/search',
    stats: '/api/chagubang/stats',
    ws: '/api/chagubang/ws'
  },
  
  // 交易相关
  trading: {
    buy: '/api/trading/buy',
    sell: '/api/trading/sell',
    cancel: '/api/trading/cancel'
  }
};

// 请求配置
const REQUEST_CONFIG = {
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
};

// 导出配置
export {
  API_BASE_URL,
  WS_BASE_URL,
  API_ENDPOINTS,
  REQUEST_CONFIG
};

// 默认导出
export default {
  baseURL: API_BASE_URL,
  wsURL: WS_BASE_URL,
  endpoints: API_ENDPOINTS,
  config: REQUEST_CONFIG
};
