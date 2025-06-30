/**
 * Supabase投资组合服务 - 与新的Supabase API通信
 */

// API配置
const API_BASE_URL = process.env.VUE_APP_API_URL || 'http://localhost:8000';
const SUPABASE_API_PREFIX = `${API_BASE_URL}/api/supabase`;

/**
 * HTTP请求工具函数
 */
async function apiRequest(url, options = {}) {
  try {
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('API请求失败:', error);
    throw error;
  }
}

/**
 * Supabase投资组合服务类
 */
export class SupabasePortfolioService {
  
  // ==================== 用户管理 ====================
  
  /**
   * 创建用户
   * @param {Object} userData - 用户数据
   * @returns {Promise} 创建结果
   */
  async createUser(userData) {
    return await apiRequest(`${SUPABASE_API_PREFIX}/users`, {
      method: 'POST',
      body: JSON.stringify(userData)
    });
  }

  /**
   * 获取用户信息
   * @param {string} userId - 用户ID
   * @returns {Promise} 用户信息
   */
  async getUser(userId) {
    return await apiRequest(`${SUPABASE_API_PREFIX}/users/${userId}`);
  }

  /**
   * 获取用户列表
   * @param {Object} filters - 过滤条件
   * @returns {Promise} 用户列表
   */
  async getUsers(filters = {}) {
    const params = new URLSearchParams(filters);
    return await apiRequest(`${SUPABASE_API_PREFIX}/users?${params}`);
  }

  // ==================== 股票管理 ====================

  /**
   * 创建股票信息
   * @param {Object} stockData - 股票数据
   * @returns {Promise} 创建结果
   */
  async createStock(stockData) {
    return await apiRequest(`${SUPABASE_API_PREFIX}/stocks`, {
      method: 'POST',
      body: JSON.stringify(stockData)
    });
  }

  /**
   * 获取股票信息
   * @param {string} stockCode - 股票代码
   * @returns {Promise} 股票信息
   */
  async getStock(stockCode) {
    return await apiRequest(`${SUPABASE_API_PREFIX}/stocks/${stockCode}`);
  }

  /**
   * 获取股票列表
   * @param {Object} filters - 过滤条件
   * @returns {Promise} 股票列表
   */
  async getStocks(filters = {}) {
    const params = new URLSearchParams(filters);
    return await apiRequest(`${SUPABASE_API_PREFIX}/stocks?${params}`);
  }

  // ==================== 投资组合管理 ====================

  /**
   * 创建投资组合
   * @param {Object} portfolioData - 投资组合数据
   * @returns {Promise} 创建结果
   */
  async createPortfolio(portfolioData) {
    return await apiRequest(`${SUPABASE_API_PREFIX}/portfolios`, {
      method: 'POST',
      body: JSON.stringify(portfolioData)
    });
  }

  /**
   * 获取投资组合列表
   * @param {string} userId - 用户ID
   * @returns {Promise} 投资组合列表
   */
  async getPortfolios(userId = null) {
    const params = userId ? new URLSearchParams({ user_id: userId }) : '';
    return await apiRequest(`${SUPABASE_API_PREFIX}/portfolios?${params}`);
  }

  /**
   * 获取投资组合详情
   * @param {string} portfolioId - 投资组合ID
   * @returns {Promise} 投资组合详情
   */
  async getPortfolio(portfolioId) {
    return await apiRequest(`${SUPABASE_API_PREFIX}/portfolios/${portfolioId}`);
  }

  /**
   * 更新投资组合
   * @param {string} portfolioId - 投资组合ID
   * @param {Object} updateData - 更新数据
   * @returns {Promise} 更新结果
   */
  async updatePortfolio(portfolioId, updateData) {
    return await apiRequest(`${SUPABASE_API_PREFIX}/portfolios/${portfolioId}`, {
      method: 'PUT',
      body: JSON.stringify(updateData)
    });
  }

  // ==================== 持仓管理 ====================

  /**
   * 创建持仓
   * @param {Object} holdingData - 持仓数据
   * @returns {Promise} 创建结果
   */
  async createHolding(holdingData) {
    return await apiRequest(`${SUPABASE_API_PREFIX}/holdings`, {
      method: 'POST',
      body: JSON.stringify(holdingData)
    });
  }

  /**
   * 获取持仓列表
   * @param {string} portfolioId - 投资组合ID
   * @returns {Promise} 持仓列表
   */
  async getHoldings(portfolioId = null) {
    const params = portfolioId ? new URLSearchParams({ portfolio_id: portfolioId }) : '';
    return await apiRequest(`${SUPABASE_API_PREFIX}/holdings?${params}`);
  }

  /**
   * 更新持仓
   * @param {string} holdingId - 持仓ID
   * @param {Object} updateData - 更新数据
   * @returns {Promise} 更新结果
   */
  async updateHolding(holdingId, updateData) {
    return await apiRequest(`${SUPABASE_API_PREFIX}/holdings/${holdingId}`, {
      method: 'PUT',
      body: JSON.stringify(updateData)
    });
  }

  // ==================== 交易记录管理 ====================

  /**
   * 创建交易记录
   * @param {Object} transactionData - 交易数据
   * @returns {Promise} 创建结果
   */
  async createTransaction(transactionData) {
    return await apiRequest(`${SUPABASE_API_PREFIX}/transactions`, {
      method: 'POST',
      body: JSON.stringify(transactionData)
    });
  }

  /**
   * 获取交易记录
   * @param {Object} filters - 过滤条件
   * @returns {Promise} 交易记录列表
   */
  async getTransactions(filters = {}) {
    const params = new URLSearchParams(filters);
    return await apiRequest(`${SUPABASE_API_PREFIX}/transactions?${params}`);
  }

  // ==================== 系统配置管理 ====================

  /**
   * 获取系统配置
   * @param {string} key - 配置键
   * @returns {Promise} 配置信息
   */
  async getSystemConfig(key = null) {
    const params = key ? new URLSearchParams({ key }) : '';
    return await apiRequest(`${SUPABASE_API_PREFIX}/config?${params}`);
  }

  /**
   * 更新系统配置
   * @param {string} key - 配置键
   * @param {any} value - 配置值
   * @param {string} description - 配置描述
   * @returns {Promise} 更新结果
   */
  async updateSystemConfig(key, value, description = null) {
    return await apiRequest(`${SUPABASE_API_PREFIX}/config/${key}`, {
      method: 'PUT',
      body: JSON.stringify({ value, description })
    });
  }

  // ==================== 数据管理 ====================

  /**
   * 清理测试数据
   * @param {Array} dataTypes - 数据类型列表
   * @returns {Promise} 清理结果
   */
  async cleanupTestData(dataTypes = null) {
    const params = dataTypes ? new URLSearchParams({ data_types: dataTypes.join(',') }) : '';
    return await apiRequest(`${SUPABASE_API_PREFIX}/cleanup?${params}`, {
      method: 'DELETE'
    });
  }

  // ==================== 便捷方法 ====================

  /**
   * 获取用户的完整投资组合信息（包含持仓和交易记录）
   * @param {string} userId - 用户ID
   * @returns {Promise} 完整投资组合信息
   */
  async getUserCompletePortfolios(userId) {
    try {
      // 获取用户投资组合列表
      const portfoliosResult = await this.getPortfolios(userId);
      const portfolios = portfoliosResult.data || [];

      // 为每个投资组合获取详细信息
      const completePortfolios = await Promise.all(
        portfolios.map(async (portfolio) => {
          try {
            // 获取投资组合详情（包含持仓）
            const detailResult = await this.getPortfolio(portfolio.id);
            const portfolioDetail = detailResult.data;

            // 获取交易记录
            const transactionsResult = await this.getTransactions({ portfolio_id: portfolio.id });
            portfolioDetail.transactions = transactionsResult.data || [];

            return portfolioDetail;
          } catch (error) {
            console.error(`获取投资组合 ${portfolio.id} 详情失败:`, error);
            return portfolio; // 返回基本信息
          }
        })
      );

      return {
        success: true,
        data: completePortfolios
      };
    } catch (error) {
      console.error('获取用户完整投资组合信息失败:', error);
      throw error;
    }
  }

  /**
   * 执行买入操作（创建持仓和交易记录）
   * @param {Object} tradeData - 交易数据
   * @returns {Promise} 交易结果
   */
  async executeBuyOrder(tradeData) {
    try {
      const { portfolioId, stockCode, shares, price, notes } = tradeData;

      // 创建持仓
      const holdingData = {
        portfolio_id: portfolioId,
        stock_code: stockCode,
        shares: shares,
        cost_price: price,
        current_price: price
      };

      const holdingResult = await this.createHolding(holdingData);

      // 创建交易记录
      const transactionData = {
        portfolio_id: portfolioId,
        stock_code: stockCode,
        transaction_type: 'buy',
        shares: shares,
        price: price,
        total_amount: shares * price,
        commission: shares * price * 0.0003, // 万三手续费
        notes: notes || `买入${stockCode}`
      };

      const transactionResult = await this.createTransaction(transactionData);

      return {
        success: true,
        data: {
          holding: holdingResult.data,
          transaction: transactionResult.data
        }
      };
    } catch (error) {
      console.error('执行买入操作失败:', error);
      throw error;
    }
  }

  /**
   * 计算投资组合表现
   * @param {Object} portfolio - 投资组合数据
   * @returns {Object} 表现指标
   */
  calculatePortfolioPerformance(portfolio) {
    const holdings = portfolio.holdings || [];
    
    let totalCost = 0;
    let totalMarketValue = 0;

    holdings.forEach(holding => {
      const shares = holding.shares || 0;
      const costPrice = holding.cost_price || 0;
      const currentPrice = holding.current_price || costPrice;

      totalCost += shares * costPrice;
      totalMarketValue += shares * currentPrice;
    });

    const profitLoss = totalMarketValue - totalCost;
    const profitLossRatio = totalCost > 0 ? (profitLoss / totalCost) * 100 : 0;

    return {
      totalCost,
      totalMarketValue,
      profitLoss,
      profitLossRatio,
      cash: portfolio.cash || 0,
      totalAssets: (portfolio.cash || 0) + totalMarketValue,
      holdingsCount: holdings.length
    };
  }
}

// 创建全局实例
export const supabasePortfolioService = new SupabasePortfolioService();

// 默认导出
export default supabasePortfolioService;
