import axios from 'axios';

// 配置API基础URL
const API_BASE_URL = process.env.VUE_APP_API_BASE_URL || 'http://localhost:8000';
const AGENT_API_URL = `${API_BASE_URL}/api/agent`;

// 创建axios实例
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// 请求拦截器
api.interceptors.request.use(
  config => {
    // 添加认证token
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      // 未授权,跳转到登录页
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Agent服务接口
export function useAgentService() {
  // 启动Agent
  const startAgent = async () => {
    try {
      const response = await axios.post(`${AGENT_API_URL}/start`);
      return response.data;
    } catch (error) {
      console.error('启动Agent失败:', error);
      throw error;
    }
  };

  // 停止Agent
  const stopAgent = async () => {
    try {
      const response = await axios.post(`${AGENT_API_URL}/stop`);
      return response.data;
    } catch (error) {
      console.error('停止Agent失败:', error);
      throw error;
    }
  };

  // 获取Agent状态
  const getAgentStatus = async () => {
    try {
      const response = await axios.get(`${AGENT_API_URL}/status`);
      return response.data.data || {};
    } catch (error) {
      console.error('获取Agent状态失败:', error);
      throw error;
    }
  };

  // 请求Agent进行决策
  const requestDecision = async (context = {}) => {
    try {
      const response = await axios.post(`${AGENT_API_URL}/decision`, { context });
      return response.data;
    } catch (error) {
      console.error('请求决策失败:', error);
      throw error;
    }
  };

  // 执行交易动作
  const executeAction = async (actionData = {}) => {
    try {
      const response = await axios.post(`${AGENT_API_URL}/execute`, { action_data: actionData });
      return response.data;
    } catch (error) {
      console.error('执行交易动作失败:', error);
      throw error;
    }
  };

  // 提供学习反馈
  const provideFeedback = async (feedback = {}) => {
    try {
      const response = await axios.post(`${AGENT_API_URL}/learn`, { feedback });
      return response.data;
    } catch (error) {
      console.error('提供学习反馈失败:', error);
      throw error;
    }
  };

  // 获取交易执行器状态
  const getExecutorStatus = async () => {
    try {
      const response = await axios.get(`${AGENT_API_URL}/executor/status`);
      return response.data.data || {};
    } catch (error) {
      console.error('获取交易执行器状态失败:', error);
      throw error;
    }
  };

  // 获取当前持仓
  const getPositions = async () => {
    try {
      const response = await axios.get(`${AGENT_API_URL}/executor/positions`);
      return response.data.positions || [];
    } catch (error) {
      console.error('获取持仓信息失败:', error);
      throw error;
    }
  };

  // 获取订单历史
  const getOrderHistory = async (limit = 50) => {
    try {
      const response = await axios.get(`${AGENT_API_URL}/executor/orders?limit=${limit}`);
      return response.data.orders || [];
    } catch (error) {
      console.error('获取订单历史失败:', error);
      throw error;
    }
  };

  // 设置自动交易模式
  const setAutoTradeMode = async (enabled = false) => {
    try {
      const response = await axios.post(`${AGENT_API_URL}/executor/mode`, {
        auto_trade: enabled
      });
      return response.data;
    } catch (error) {
      console.error('设置自动交易模式失败:', error);
      throw error;
    }
  };

  // 手动下单
  const placeManualOrder = async (orderData = {}) => {
    try {
      const response = await axios.post(`${AGENT_API_URL}/executor/place-order`, orderData);
      return response.data;
    } catch (error) {
      console.error('手动下单失败:', error);
      throw error;
    }
  };

  // 取消订单
  const cancelOrder = async (orderId) => {
    try {
      const response = await axios.post(`${AGENT_API_URL}/executor/cancel-order`, {
        order_id: orderId
      });
      return response.data;
    } catch (error) {
      console.error('取消订单失败:', error);
      throw error;
    }
  };

  // 获取Agent性能统计
  const getPerformanceStats = async (timeRange = '1d') => {
    try {
      const response = await axios.get(`${AGENT_API_URL}/performance?range=${timeRange}`);
      return response.data.stats || {};
    } catch (error) {
      console.error('获取性能统计失败:', error);
      throw error;
    }
  };

  return {
    startAgent,
    stopAgent,
    getAgentStatus,
    requestDecision,
    executeAction,
    provideFeedback,
    getExecutorStatus,
    getPositions,
    getOrderHistory,
    setAutoTradeMode,
    placeManualOrder,
    cancelOrder,
    getPerformanceStats
  };
}

// Agent交易服务
export function useAiTradingService() {
  // 获取Agent交易建议
  const getTradingRecommendations = async (symbol = '', timeframe = '1d') => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/ai/recommendations`, {
        params: { symbol, timeframe }
      });
      return response.data.recommendations || [];
    } catch (error) {
      console.error('获取交易建议失败:', error);
      throw error;
    }
  };

  // 分析股票
  const analyzeStock = async (symbol = '', data = {}) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/ai/analyze`, {
        symbol,
        ...data
      });
      return response.data.analysis || {};
    } catch (error) {
      console.error('分析股票失败:', error);
      throw error;
    }
  };

  // 获取市场情绪
  const getMarketSentiment = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/ai/market-sentiment`);
      return response.data.sentiment || {};
    } catch (error) {
      console.error('获取市场情绪失败:', error);
      throw error;
    }
  };

  // 获取风险评估
  const getRiskAssessment = async (portfolio = []) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/ai/risk-assessment`, {
        portfolio
      });
      return response.data.assessment || {};
    } catch (error) {
      console.error('获取风险评估失败:', error);
      throw error;
    }
  };

  return {
    getTradingRecommendations,
    analyzeStock,
    getMarketSentiment,
    getRiskAssessment
  };
}

export default {
  useAgentService,
  useAiTradingService
}; 
