/**
 * Mock Data System
 * Provides structured mock data handlers for API endpoints
 */

import stockData from './stock-data';
import tradeData from './trade-data';
import aiRecommendations from './ai-recommendations';

/**
 * Mock data handlers organized by endpoint and HTTP method
 * Each handler is a function that receives the request data and returns a mock response
 */
export default {
  // Stock Data API
  '/api/stock/quote': {
    GET: stockData.getStockQuote,
    POST: null
  },
  
  '/api/stock/history': {
    GET: stockData.getStockHistory,
    POST: null
  },
  
  '/api/stock/search': {
    GET: stockData.searchStocks,
    POST: null
  },
  
  // T Trading API
  '/api/t-trading/evaluate-opportunity': {
    POST: tradeData.evaluateOpportunity,
    GET: null
  },
  
  '/api/t-trading/record-trade': {
    POST: tradeData.recordTrade,
    GET: null
  },
  
  '/api/t-trading/ai-recommendation': {
    POST: aiRecommendations.getRecommendation,
    GET: null
  },
  
  '/api/t-trading/train-ai-model': {
    POST: aiRecommendations.trainModel,
    GET: null
  },
  
  '/api/t-trading/trade-history': {
    GET: tradeData.getTradeHistory,
    POST: null
  },
  
  // More endpoints can be added as needed...
}; 
 
