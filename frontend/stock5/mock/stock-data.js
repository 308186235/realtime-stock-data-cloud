/**
 * Mock Stock Data
 * Provides mock responses for stock-related API endpoints
 */

// Sample stock list
const SAMPLE_STOCKS = [
  { code: '000001', name: 'Ping An Bank', industry: 'Banking' },
  { code: '600519', name: 'Kweichow Moutai', industry: 'Consumer Goods' },
  { code: '601398', name: 'ICBC', industry: 'Banking' },
  { code: '600276', name: 'Hengrui Medicine', industry: 'Pharmaceuticals' },
  { code: '601318', name: 'Ping An Insurance', industry: 'Insurance' },
  { code: '000858', name: 'Wuliangye', industry: 'Consumer Goods' },
  { code: '600036', name: 'China Merchants Bank', industry: 'Banking' },
  { code: '002594', name: 'BYD', industry: 'Automotive' },
  { code: '601988', name: 'Bank of China', industry: 'Banking' },
  { code: '600030', name: 'CITIC Securities', industry: 'Securities' }
];

// Generate a random price within a range
const getRandomPrice = (base, variance = 0.1) => {
  const min = base * (1 - variance);
  const max = base * (1 + variance);
  return parseFloat((Math.random() * (max - min) + min).toFixed(2));
};

// Generate a random stock quote
const generateStockQuote = (stock, currentPrice = null) => {
  const basePrice = currentPrice || (parseFloat(stock.code.slice(-4)) % 30 + 20); // Generate a stable price based on stock code
  const open = getRandomPrice(basePrice, 0.03);
  const close = getRandomPrice(basePrice, 0.05);
  const high = Math.max(open, close) * (1 + Math.random() * 0.03);
  const low = Math.min(open, close) * (1 - Math.random() * 0.03);
  const volume = Math.floor(Math.random() * 10000000) + 1000000;
  
  return {
    code: stock.code,
    name: stock.name,
    currentPrice: close,
    open: parseFloat(open.toFixed(2)),
    high: parseFloat(high.toFixed(2)),
    low: parseFloat(low.toFixed(2)),
    close: parseFloat(close.toFixed(2)),
    volume: volume,
    amount: parseFloat((volume * close).toFixed(2)),
    change: parseFloat((close - open).toFixed(2)),
    changePercent: parseFloat(((close - open) / open * 100).toFixed(2)),
    turnoverRate: parseFloat((volume / 10000000 * 100).toFixed(2)),
    pe: parseFloat((Math.random() * 30 + 10).toFixed(2)),
    pb: parseFloat((Math.random() * 5 + 1).toFixed(2)),
    marketCap: parseFloat((close * 10000000).toFixed(2)),
    timestamp: new Date().getTime()
  };
};

// Generate historical data points
const generateHistoricalData = (stock, days = 30) => {
  const data = [];
  const basePrice = parseFloat(stock.code.slice(-4)) % 30 + 20;
  let currentPrice = basePrice;
  
  const now = new Date();
  
  for (let i = days; i >= 0; i--) {
    const date = new Date(now);
    date.setDate(date.getDate() - i);
    
    // Skip weekends
    if (date.getDay() === 0 || date.getDay() === 6) {
      continue;
    }
    
    // Add some trend and volatility
    const trend = Math.sin(i / 10) * 0.01;
    const volatility = Math.random() * 0.04 - 0.02;
    
    currentPrice = currentPrice * (1 + trend + volatility);
    currentPrice = parseFloat(currentPrice.toFixed(2));
    
    const dayQuote = generateStockQuote({...stock, currentPrice});
    dayQuote.date = date.toISOString().split('T')[0];
    
    data.push(dayQuote);
  }
  
  return data;
};

// Find a stock by code
const findStockByCode = (code) => {
  return SAMPLE_STOCKS.find(stock => stock.code === code) || null;
};

// Mock API handlers
export default {
  // Get real-time stock quote
  getStockQuote: (params) => {
    const { code } = params;
    const stock = findStockByCode(code);
    
    if (!stock) {
      return {
        code: 404,
        message: 'Stock not found',
        data: null
      };
    }
    
    return {
      code: 200,
      message: 'success',
      data: generateStockQuote(stock)
    };
  },
  
  // Get historical stock data
  getStockHistory: (params) => {
    const { code, days = 30 } = params;
    const stock = findStockByCode(code);
    
    if (!stock) {
      return {
        code: 404,
        message: 'Stock not found',
        data: null
      };
    }
    
    return {
      code: 200,
      message: 'success',
      data: {
        stock: stock,
        history: generateHistoricalData(stock, days)
      }
    };
  },
  
  // Search for stocks
  searchStocks: (params) => {
    const { keyword = '', limit = 10 } = params;
    
    if (!keyword) {
      return {
        code: 200,
        message: 'success',
        data: SAMPLE_STOCKS.slice(0, limit)
      };
    }
    
    const results = SAMPLE_STOCKS.filter(stock => 
      stock.code.includes(keyword) || 
      stock.name.toLowerCase().includes(keyword.toLowerCase())
    ).slice(0, limit);
    
    return {
      code: 200,
      message: 'success',
      data: results
    };
  }
}; 
 
