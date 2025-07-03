/**
 * 交易服务 - 与后端交易API通信
 */
import { baseUrl } from './config.js';

const API_PREFIX = `${baseUrl}/api/trading`;
const THS_API_PREFIX = `${baseUrl}/api/ths`;

class TradingService {
  
  /**
   * 获取支持的券商列表
   */
  async getSupportedBrokers() {
    try {
      const response = await uni.request({
        url: `${API_PREFIX}/brokers`,
        method: 'GET'
      });
      
      if (response.statusCode === 200) {
        return response.data;
      } else {
        throw new Error(`获取券商列表失败: ${response.statusCode}`);
      }
    } catch (error) {
      console.error('获取券商列表异常:', error);
      throw error;
    }
  }
  
  /**
   * 连接到交易服务
   * @param {Object} params - 连接参数
   * @param {string} [params.broker_type] - 券商类型
   * @param {string} [params.account_id] - 账号
   * @param {string} [params.account_pwd] - 密码
   * @param {string} [params.server_ip] - 服务器IP
   * @param {number} [params.server_port] - 服务器端口
   */
  async connect(params = {}) {
    try {
      const response = await uni.request({
        url: `${API_PREFIX}/connect`,
        method: 'POST',
        data: params
      });
      
      if (response.statusCode === 200) {
        return response.data;
      } else {
        throw new Error(`连接交易服务失败: ${response.statusCode}`);
      }
    } catch (error) {
      console.error('连接交易服务异常:', error);
      throw error;
    }
  }
  
  /**
   * 断开交易服务连接
   */
  async disconnect() {
    try {
      const response = await uni.request({
        url: `${API_PREFIX}/disconnect`,
        method: 'POST'
      });
      
      if (response.statusCode === 200) {
        return response.data;
      } else {
        throw new Error(`断开交易服务连接失败: ${response.statusCode}`);
      }
    } catch (error) {
      console.error('断开交易服务连接异常:', error);
      throw error;
    }
  }
  
  /**
   * 获取账户信息
   */
  async getAccountInfo() {
    try {
      const response = await uni.request({
        url: `${API_PREFIX}/account`,
        method: 'GET'
      });
      
      if (response.statusCode === 200) {
        return response.data;
      } else {
        throw new Error(`获取账户信息失败: ${response.statusCode}`);
      }
    } catch (error) {
      console.error('获取账户信息异常:', error);
      throw error;
    }
  }
  
  /**
   * 获取持仓信息
   */
  async getPositions() {
    try {
      // 开发环境下拒绝模拟数据
      if (process.env.NODE_ENV === 'development') {
        console.log('[开发模式] 拒绝返回模拟数据');

        // ❌ 拒绝返回模拟持仓数据
        throw new Error('❌ 拒绝返回模拟数据！系统要求使用真实数据源');
        const mockPositions = [
          {
            symbol: '600519',
            name: '贵州茅台',
            volume: 10,
            available_volume: 10,
            cost_price: 1680.25,
            current_price: 1760.88,
            price_change_pct: 2.15,
            market_value: 17608.80,
            profit_loss: 806.30,
            profit_loss_ratio: 0.048,
            position_date: '2023-06-15'
          },
          {
            symbol: '000001',
            name: '平安银行',
            volume: 1000,
            available_volume: 1000,
            cost_price: 16.05,
            current_price: 15.23,
            price_change_pct: -1.36,
            market_value: 15230.00,
            profit_loss: -820.00,
            profit_loss_ratio: -0.0511,
            position_date: '2023-05-22'
          },
          {
            symbol: '601318',
            name: '中国平安',
            volume: 200,
            available_volume: 200,
            cost_price: 45.30,
            current_price: 48.75,
            price_change_pct: 0.56,
            market_value: 9750.00,
            profit_loss: 690.00,
            profit_loss_ratio: 0.0761,
            position_date: '2023-07-03'
          },
          {
            symbol: '300750',
            name: '宁德时代',
            volume: 50,
            available_volume: 50,
            cost_price: 200.40,
            current_price: 226.60,
            price_change_pct: 4.25,
            market_value: 11330.00,
            profit_loss: 1310.00,
            profit_loss_ratio: 0.1307,
            position_date: '2023-04-18'
          },
          {
            symbol: '600050',
            name: '中国联通',
            volume: 5000,
            available_volume: 5000,
            cost_price: 5.12,
            current_price: 4.68,
            price_change_pct: -0.21,
            market_value: 23400.00,
            profit_loss: -2200.00,
            profit_loss_ratio: -0.0859,
            position_date: '2023-01-30'
          }
        ];
        
        return Promise.resolve({
          success: true,
          data: mockPositions
        });
      }
      
      const response = await uni.request({
        url: `${API_PREFIX}/positions`,
        method: 'GET'
      });
      
      if (response.statusCode === 200) {
        return response.data;
      } else {
        throw new Error(`获取持仓信息失败: ${response.statusCode}`);
      }
    } catch (error) {
      console.error('获取持仓信息异常:', error);
      throw error;
    }
  }
  
  /**
   * 下单
   * @param {Object} order - 订单参数
   * @param {string} order.symbol - 证券代码
   * @param {number} order.price - 委托价格
   * @param {number} order.volume - 委托数量
   * @param {string} order.direction - 交易方向 'BUY'或'SELL'
   * @param {string} [order.order_type] - 订单类型 'LIMIT'或'MARKET'
   */
  async placeOrder(order) {
    try {
      const response = await uni.request({
        url: `${API_PREFIX}/orders`,
        method: 'POST',
        data: order
      });
      
      if (response.statusCode === 200) {
        return response.data;
      } else {
        throw new Error(`下单失败: ${response.statusCode}`);
      }
    } catch (error) {
      console.error('下单异常:', error);
      throw error;
    }
  }
  
  /**
   * 撤单
   * @param {string} orderId - 委托编号
   */
  async cancelOrder(orderId) {
    try {
      const response = await uni.request({
        url: `${API_PREFIX}/orders/${orderId}`,
        method: 'DELETE'
      });
      
      if (response.statusCode === 200) {
        return response.data;
      } else {
        throw new Error(`撤单失败: ${response.statusCode}`);
      }
    } catch (error) {
      console.error('撤单异常:', error);
      throw error;
    }
  }
  
  /**
   * 获取委托列表
   * @param {Object} params - 查询参数
   * @param {string} [params.status] - 委托状态
   * @param {string} [params.start_date] - 开始日期,格式'YYYY-MM-DD'
   * @param {string} [params.end_date] - 结束日期,格式'YYYY-MM-DD'
   */
  async getOrders(params = {}) {
    try {
      // 构建查询参数
      const queryParams = Object.entries(params)
        .filter(([_, value]) => value !== undefined && value !== null)
        .map(([key, value]) => `${key}=${encodeURIComponent(value)}`)
        .join('&');
      
      const url = `${API_PREFIX}/orders${queryParams ? '?' + queryParams : ''}`;
      
      const response = await uni.request({
        url,
        method: 'GET'
      });
      
      if (response.statusCode === 200) {
        return response.data;
      } else {
        throw new Error(`获取委托列表失败: ${response.statusCode}`);
      }
    } catch (error) {
      console.error('获取委托列表异常:', error);
      throw error;
    }
  }
  
  /**
   * 获取成交列表
   * @param {Object} params - 查询参数
   * @param {string} [params.start_date] - 开始日期,格式'YYYY-MM-DD'
   * @param {string} [params.end_date] - 结束日期,格式'YYYY-MM-DD'
   */
  async getTrades(params = {}) {
    try {
      // 开发环境下拒绝模拟数据
      if (process.env.NODE_ENV === 'development') {
        console.log('[开发模式] 拒绝返回模拟数据');

        // ❌ 拒绝返回模拟交易数据
        throw new Error('❌ 拒绝返回模拟数据！系统要求使用真实数据源');
        const mockTrades = [
          {
            id: 'trade001',
            symbol: '600519',
            name: '贵州茅台',
            direction: 'BUY',
            volume: 5,
            price: 1670.50,
            amount: 8352.50,
            trade_time: '2023-05-20T10:15:30',
            commission: 8.35,
            status: 'COMPLETED'
          },
          {
            id: 'trade002',
            symbol: '600519',
            name: '贵州茅台',
            direction: 'BUY',
            volume: 5,
            price: 1680.25,
            amount: 8401.25,
            trade_time: '2023-06-15T14:23:45',
            commission: 8.40,
            status: 'COMPLETED'
          },
          {
            id: 'trade003',
            symbol: '600519',
            name: '贵州茅台',
            direction: 'SELL',
            volume: 2,
            price: 1725.80,
            amount: 3451.60,
            trade_time: '2023-07-10T09:45:12',
            commission: 3.45,
            status: 'COMPLETED'
          },
          {
            id: 'trade004',
            symbol: '000001',
            name: '平安银行',
            direction: 'BUY',
            volume: 1000,
            price: 16.05,
            amount: 16050.00,
            trade_time: '2023-05-22T11:32:40',
            commission: 16.05,
            status: 'COMPLETED'
          },
          {
            id: 'trade005',
            symbol: '601318',
            name: '中国平安',
            direction: 'BUY',
            volume: 200,
            price: 45.30,
            amount: 9060.00,
            trade_time: '2023-07-03T13:54:28',
            commission: 9.06,
            status: 'COMPLETED'
          },
          {
            id: 'trade006',
            symbol: '300750',
            name: '宁德时代',
            direction: 'BUY',
            volume: 50,
            price: 200.40,
            amount: 10020.00,
            trade_time: '2023-04-18T10:05:33',
            commission: 10.02,
            status: 'COMPLETED'
          },
          {
            id: 'trade007',
            symbol: '300750',
            name: '宁德时代',
            direction: 'SELL',
            volume: 10,
            price: 220.50,
            amount: 2205.00,
            trade_time: '2023-06-25T14:12:18',
            commission: 2.21,
            status: 'COMPLETED'
          },
          {
            id: 'trade008',
            symbol: '600050',
            name: '中国联通',
            direction: 'BUY',
            volume: 5000,
            price: 5.12,
            amount: 25600.00,
            trade_time: '2023-01-30T09:38:22',
            commission: 25.60,
            status: 'COMPLETED'
          }
        ];
        
        // 过滤交易记录以匹配请求的日期范围
        let filteredTrades = [...mockTrades];
        
        if (params.start_date) {
          const startDate = new Date(params.start_date);
          filteredTrades = filteredTrades.filter(trade => {
            const tradeDate = new Date(trade.trade_time);
            return tradeDate >= startDate;
          });
        }
        
        if (params.end_date) {
          const endDate = new Date(params.end_date);
          endDate.setHours(23, 59, 59, 999); // 设置为当天结束时间
          filteredTrades = filteredTrades.filter(trade => {
            const tradeDate = new Date(trade.trade_time);
            return tradeDate <= endDate;
          });
        }
        
        return Promise.resolve({
          success: true,
          data: filteredTrades
        });
      }
      
      // 构建查询参数
      const queryParams = Object.entries(params)
        .filter(([_, value]) => value !== undefined && value !== null)
        .map(([key, value]) => `${key}=${encodeURIComponent(value)}`)
        .join('&');
      
      const url = `${API_PREFIX}/trades${queryParams ? '?' + queryParams : ''}`;
      
      const response = await uni.request({
        url,
        method: 'GET'
      });
      
      if (response.statusCode === 200) {
        return response.data;
      } else {
        throw new Error(`获取成交列表失败: ${response.statusCode}`);
      }
    } catch (error) {
      console.error('获取成交列表异常:', error);
      throw error;
    }
  }
  
  /**
   * 获取实时行情
   * @param {Array<string>} symbols - 证券代码列表
   */
  async getQuotes(symbols) {
    try {
      if (!symbols || !symbols.length) {
        throw new Error('请提供有效的证券代码');
      }
      
      const symbolsStr = symbols.join(',');
      const url = `${API_PREFIX}/quotes?symbols=${encodeURIComponent(symbolsStr)}`;
      
      const response = await uni.request({
        url,
        method: 'GET'
      });
      
      if (response.statusCode === 200) {
        return response.data;
      } else {
        throw new Error(`获取行情数据失败: ${response.statusCode}`);
      }
    } catch (error) {
      console.error('获取行情数据异常:', error);
      throw error;
    }
  }
  
  /**
   * 获取东吴秀才账户余额(从同花顺API)
   * @returns {Promise<Object>} 账户余额信息
   */
  async getDongwuXiucaiBalance() {
    try {
      // 开发环境下拒绝模拟数据
      if (process.env.NODE_ENV === 'development') {
        console.log('[开发模式] 拒绝返回模拟数据');

        // ❌ 拒绝返回模拟东吴秀才账户数据
        throw new Error('❌ 拒绝返回模拟数据！系统要求使用真实数据源');
        return Promise.resolve({
          success: true,
          data: {
            balance: 120000.00,
            available: 80000.00,
            market_value: 40000.00,
            total_assets: 120000.00,
            frozen: 0.00,
            account_type: '东吴秀才'
          }
        });
      }
      
      // 登录同花顺并获取账户信息
      const loginResponse = await uni.request({
        url: `${THS_API_PREFIX}/login`,
        method: 'POST',
        data: {
          account: '东吴秀才账号', // 实际应用中应从配置或安全存储获取
          password: '密码',       // 实际应用中应从配置或安全存储获取
          broker_type: 'dongwu_xiucai'
        }
      });
      
      if (loginResponse.statusCode !== 200 || !loginResponse.data.success) {
        throw new Error(`登录同花顺失败: ${loginResponse.data?.message || loginResponse.statusCode}`);
      }
      
      const sessionId = loginResponse.data.session_id;
      
      // 获取账户信息
      const accountResponse = await uni.request({
        url: `${THS_API_PREFIX}/account_info`,
        method: 'GET',
        data: { session_id: sessionId }
      });
      
      if (accountResponse.statusCode !== 200 || !accountResponse.data.success) {
        throw new Error(`获取账户信息失败: ${accountResponse.data?.message || accountResponse.statusCode}`);
      }
      
      // 登出
      await uni.request({
        url: `${THS_API_PREFIX}/logout`,
        method: 'POST',
        data: { session_id: sessionId }
      });
      
      // 为账户信息添加账户类型标识
      const accountInfo = accountResponse.data.data;
      accountInfo.account_type = '东吴秀才';
      
      return {
        success: true,
        data: accountInfo
      };
    } catch (error) {
      console.error('获取东吴秀才账户信息异常:', error);
      return {
        success: false,
        message: error.message || '获取东吴秀才账户信息失败'
      };
    }
  }
  
  /**
   * 获取账户余额历史变化记录
   * @param {Object} params - 查询参数
   * @param {string} [params.start_date] - 开始日期,格式'YYYY-MM-DD'
   * @param {string} [params.end_date] - 结束日期,格式'YYYY-MM-DD'
   * @returns {Promise<Object>} 余额历史记录
   */
  async getBalanceHistory(params = {}) {
    try {
      // 开发环境下拒绝模拟数据
      if (process.env.NODE_ENV === 'development') {
        console.log('[开发模式] 拒绝返回模拟数据');

        // ❌ 拒绝生成模拟余额变化数据
        throw new Error('❌ 拒绝返回模拟数据！系统要求使用真实数据源');
        const endDate = params.end_date ? new Date(params.end_date) : new Date();
        const startDate = params.start_date ? new Date(params.start_date) : new Date(endDate);
        startDate.setMonth(startDate.getMonth() - 1);
        
        const mockData = [];
        
        // 模拟每天有1-3条余额变化记录
        let currentDate = new Date(startDate);
        while (currentDate <= endDate) {
          const recordsCount = Math.floor(Math.random() * 3) + 1;
          
          for (let i = 0; i < recordsCount; i++) {
            const recordTime = new Date(currentDate);
            recordTime.setHours(9 + Math.floor(Math.random() * 6)); // 9:00 - 15:00
            recordTime.setMinutes(Math.floor(Math.random() * 60));
            
            // 随机生成买入或卖出交易
            const isBuy = Math.random() > 0.5;
            const stockCodes = ['600519', '000858', '601318', '600036', '000001'];
            const stockNames = ['贵州茅台', '五粮液', '中国平安', '招商银行', '平安银行'];
            const stockIndex = Math.floor(Math.random() * stockCodes.length);
            
            const price = 50 + Math.random() * 150; // 模拟股价
            const volume = Math.floor(Math.random() * 500) + 100; // 模拟成交量
            const tradeAmount = price * volume;
            
            // 模拟费用为交易额的0.15%左右
            const feeRate = 0.0015 + (Math.random() * 0.0005);
            const fees = tradeAmount * feeRate;
            
            // 买入时余额减少(交易额+费用),卖出时余额增加(交易额-费用)
            const balanceChange = isBuy ? -(tradeAmount + fees) : (tradeAmount - fees);
            
            mockData.push({
              id: `record_${mockData.length + 1}`,
              time: recordTime.getTime(),
              balance: balanceChange,
              tradeId: `trade_${new Date().getTime()}_${i}`,
              type: isBuy ? 'BUY' : 'SELL',
              symbol: stockCodes[stockIndex],
              name: stockNames[stockIndex],
              price: price.toFixed(2),
              volume: volume,
              description: `${isBuy ? '买入' : '卖出'} ${stockNames[stockIndex]}(${stockCodes[stockIndex]}) ${volume}股`,
              fees: {
                total: fees,
                stampDuty: isBuy ? 0 : tradeAmount * 0.001,
                commission: isBuy ? fees * 0.85 : (fees - tradeAmount * 0.001) * 0.9,
                transferFee: isBuy ? fees * 0.15 : (fees - tradeAmount * 0.001) * 0.1
              }
            });
          }
          
          // 下一天
          currentDate.setDate(currentDate.getDate() + 1);
        }
        
        return Promise.resolve({
          success: true,
          data: mockData
        });
      }
      
      // 构建查询参数
      const queryParams = Object.entries(params)
        .filter(([_, value]) => value !== undefined && value !== null)
        .map(([key, value]) => `${key}=${encodeURIComponent(value)}`)
        .join('&');
      
      const url = `${API_PREFIX}/balance/history${queryParams ? '?' + queryParams : ''}`;
      
      const response = await uni.request({
        url,
        method: 'GET'
      });
      
      if (response.statusCode === 200) {
        return response.data;
      } else {
        throw new Error(`获取余额历史记录失败: ${response.statusCode}`);
      }
    } catch (error) {
      console.error('获取余额历史记录异常:', error);
      // 发生异常时,返回一个空的成功结果,避免界面出错
      return {
        success: true,
        data: []
      };
    }
  }
}

export default new TradingService(); 
