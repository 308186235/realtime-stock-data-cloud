/**
 * 云端到本地交易指令传输桥接系统
 * 云端Agent做出决策后,安全传输交易指令到本地电脑执行买卖操作
 */

/**
 * 云端到本地交易桥接器
 */
class CloudToLocalTradingBridge {
  constructor() {
    this.name = 'CloudToLocalTradingBridge';
    this.version = '1.0.0';
    this.localConnections = new Map();
    this.pendingOrders = new Map();
    this.executionHistory = [];
    
    // 安全配置
    this.securityConfig = {
      maxOrderValue: 100000,      // 最大单笔订单金额
      maxDailyOrders: 50,         // 每日最大订单数
      requireConfirmation: true,   // 是否需要确认
      encryptionEnabled: true     // 是否启用加密
    };
    
    console.log(`🌉 云端到本地交易桥接器初始化完成 v${this.version}`);
  }

  /**
   * 发送交易信号到本地
   */
  async sendTradingSignalToLocal(analysisResult) {
    try {
      console.log('📤 发送交易信号到本地电脑...');
      
      const { decision, analysis, timestamp } = analysisResult;
      
      // 1. 验证决策有效性
      const validationResult = this.validateTradingDecision(decision);
      if (!validationResult.valid) {
        console.log(`❌ 决策验证失败: ${validationResult.reason}`);
        return { success: false, error: validationResult.reason };
      }
      
      // 2. 生成交易指令
      const tradingOrder = this.generateTradingOrder(decision, analysis);
      
      // 3. 安全检查
      const securityCheck = this.performSecurityCheck(tradingOrder);
      if (!securityCheck.passed) {
        console.log(`🛡️ 安全检查失败: ${securityCheck.reason}`);
        return { success: false, error: securityCheck.reason };
      }
      
      // 4. 加密交易指令
      const encryptedOrder = this.encryptTradingOrder(tradingOrder);
      
      // 5. 发送到本地系统
      const transmissionResult = await this.transmitToLocalSystem(encryptedOrder);
      
      // 6. 记录传输历史
      this.recordTransmission(tradingOrder, transmissionResult);
      
      console.log(`✅ 交易信号发送${transmissionResult.success ? '成功' : '失败'}`);
      
      return transmissionResult;
      
    } catch (error) {
      console.error('❌ 发送交易信号失败:', error);
      return { success: false, error: error.message };
    }
  }

  /**
   * 验证交易决策
   */
  validateTradingDecision(decision) {
    try {
      // 检查必要字段
      const requiredFields = ['action', 'confidence', 'shouldTrade', 'tradeParams'];
      for (const field of requiredFields) {
        if (!(field in decision)) {
          return { valid: false, reason: `缺少必要字段: ${field}` };
        }
      }
      
      // 检查动作有效性
      if (!['BUY', 'SELL', 'HOLD'].includes(decision.action)) {
        return { valid: false, reason: `无效的交易动作: ${decision.action}` };
      }
      
      // 检查置信度
      if (decision.confidence < 0.6) {
        return { valid: false, reason: `置信度过低: ${decision.confidence}` };
      }
      
      // 检查是否应该交易
      if (!decision.shouldTrade) {
        return { valid: false, reason: '决策建议不交易' };
      }
      
      // 检查交易参数
      if (!decision.tradeParams || !decision.tradeParams.symbol) {
        return { valid: false, reason: '缺少交易参数' };
      }
      
      return { valid: true };
      
    } catch (error) {
      return { valid: false, reason: `验证异常: ${error.message}` };
    }
  }

  /**
   * 生成交易指令
   */
  generateTradingOrder(decision, analysis) {
    const orderId = this.generateOrderId();
    const timestamp = new Date().toISOString();
    
    const tradingOrder = {
      orderId,
      timestamp,
      source: 'cloud-intelligent-agent',
      
      // 基本交易信息
      action: decision.action,
      symbol: decision.tradeParams.symbol,
      quantity: decision.tradeParams.quantity || this.calculateOptimalQuantity(decision),
      price: decision.tradeParams.price || 'MARKET',
      orderType: decision.tradeParams.orderType || 'LIMIT',
      
      // 决策信息
      confidence: decision.confidence,
      finalScore: decision.finalScore,
      reasoning: decision.reasoning,
      
      // 风险控制
      stopLoss: decision.tradeParams.stopLoss,
      takeProfit: decision.tradeParams.takeProfit,
      maxLoss: decision.tradeParams.maxLoss,
      timeLimit: decision.tradeParams.timeLimit,
      
      // 分析数据
      marketAnalysis: {
        marketScore: analysis.marketAnalysis.marketScore,
        signal: analysis.marketAnalysis.signal,
        sentiment: analysis.marketAnalysis.marketSentiment
      },
      
      riskAssessment: {
        totalRiskScore: analysis.riskAssessment.totalRiskScore,
        riskLevel: analysis.riskAssessment.riskLevel,
        riskApproved: analysis.riskAssessment.riskApproved
      },
      
      // 执行优先级
      priority: this.calculateExecutionPriority(decision),
      
      // 安全标识
      securityHash: this.generateSecurityHash(orderId, decision),
      
      // 过期时间
      expiryTime: new Date(Date.now() + 30 * 60 * 1000).toISOString() // 30分钟后过期
    };
    
    return tradingOrder;
  }

  /**
   * 安全检查
   */
  performSecurityCheck(tradingOrder) {
    try {
      // 1. 检查订单金额
      const orderValue = tradingOrder.quantity * (tradingOrder.price === 'MARKET' ? 100 : tradingOrder.price);
      if (orderValue > this.securityConfig.maxOrderValue) {
        return { 
          passed: false, 
          reason: `订单金额超限: ${orderValue} > ${this.securityConfig.maxOrderValue}` 
        };
      }
      
      // 2. 检查每日订单数量
      const todayOrders = this.getTodayOrderCount();
      if (todayOrders >= this.securityConfig.maxDailyOrders) {
        return { 
          passed: false, 
          reason: `每日订单数量超限: ${todayOrders} >= ${this.securityConfig.maxDailyOrders}` 
        };
      }
      
      // 3. 检查订单频率
      const recentOrders = this.getRecentOrderCount(5 * 60 * 1000); // 5分钟内
      if (recentOrders > 5) {
        return { 
          passed: false, 
          reason: `订单频率过高: 5分钟内${recentOrders}笔订单` 
        };
      }
      
      // 4. 检查股票代码有效性
      if (!this.isValidStockSymbol(tradingOrder.symbol)) {
        return { 
          passed: false, 
          reason: `无效的股票代码: ${tradingOrder.symbol}` 
        };
      }
      
      // 5. 检查交易时间
      if (!this.isValidTradingTime()) {
        return { 
          passed: false, 
          reason: '非交易时间' 
        };
      }
      
      return { passed: true };
      
    } catch (error) {
      return { passed: false, reason: `安全检查异常: ${error.message}` };
    }
  }

  /**
   * 加密交易指令
   */
  encryptTradingOrder(tradingOrder) {
    if (!this.securityConfig.encryptionEnabled) {
      return tradingOrder;
    }
    
    try {
      // 简化的加密实现(实际应使用更强的加密算法)
      const orderString = JSON.stringify(tradingOrder);
      const encrypted = btoa(orderString); // Base64编码作为简化加密
      
      return {
        encrypted: true,
        data: encrypted,
        timestamp: new Date().toISOString(),
        checksum: this.calculateChecksum(orderString)
      };
      
    } catch (error) {
      console.error('❌ 加密失败:', error);
      return tradingOrder; // 加密失败时返回原始数据
    }
  }

  /**
   * 传输到本地系统
   */
  async transmitToLocalSystem(encryptedOrder) {
    try {
      console.log('🚀 传输交易指令到本地系统...');
      
      // 1. 选择最佳传输方式
      const transmissionMethod = this.selectTransmissionMethod();
      
      // 2. 根据传输方式发送
      let result;
      switch (transmissionMethod) {
        case 'websocket':
          result = await this.transmitViaWebSocket(encryptedOrder);
          break;
        case 'http':
          result = await this.transmitViaHTTP(encryptedOrder);
          break;
        case 'webhook':
          result = await this.transmitViaWebhook(encryptedOrder);
          break;
        default:
          throw new Error(`不支持的传输方式: ${transmissionMethod}`);
      }
      
      return result;
      
    } catch (error) {
      console.error('❌ 传输失败:', error);
      return { success: false, error: error.message };
    }
  }

  /**
   * 通过WebSocket传输
   */
  async transmitViaWebSocket(encryptedOrder) {
    try {
      // 获取本地连接
      const localConnection = this.getLocalConnection();
      if (!localConnection || localConnection.readyState !== WebSocket.OPEN) {
        throw new Error('本地连接不可用');
      }
      
      // 发送数据
      const message = {
        type: 'TRADING_ORDER',
        data: encryptedOrder,
        timestamp: new Date().toISOString()
      };
      
      localConnection.send(JSON.stringify(message));
      
      // 等待确认
      const confirmation = await this.waitForConfirmation(encryptedOrder.orderId || 'unknown');
      
      return {
        success: true,
        method: 'websocket',
        confirmation,
        timestamp: new Date().toISOString()
      };
      
    } catch (error) {
      return { success: false, method: 'websocket', error: error.message };
    }
  }

  /**
   * 通过HTTP传输
   */
  async transmitViaHTTP(encryptedOrder) {
    try {
      const localEndpoint = this.getLocalEndpoint();
      
      const response = await fetch(localEndpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Source': 'cloud-agent',
          'X-Timestamp': new Date().toISOString()
        },
        body: JSON.stringify({
          type: 'TRADING_ORDER',
          data: encryptedOrder
        })
      });
      
      const result = await response.json();
      
      return {
        success: response.ok,
        method: 'http',
        result,
        timestamp: new Date().toISOString()
      };
      
    } catch (error) {
      return { success: false, method: 'http', error: error.message };
    }
  }

  /**
   * 通过Webhook传输
   */
  async transmitViaWebhook(encryptedOrder) {
    try {
      const webhookUrl = this.getWebhookUrl();
      
      const response = await fetch(webhookUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Webhook-Source': 'cloud-intelligent-agent'
        },
        body: JSON.stringify({
          event: 'trading_order',
          data: encryptedOrder,
          timestamp: new Date().toISOString()
        })
      });
      
      return {
        success: response.ok,
        method: 'webhook',
        status: response.status,
        timestamp: new Date().toISOString()
      };
      
    } catch (error) {
      return { success: false, method: 'webhook', error: error.message };
    }
  }

  /**
   * 记录传输历史
   */
  recordTransmission(tradingOrder, transmissionResult) {
    const record = {
      orderId: tradingOrder.orderId,
      symbol: tradingOrder.symbol,
      action: tradingOrder.action,
      quantity: tradingOrder.quantity,
      confidence: tradingOrder.confidence,
      transmissionResult,
      timestamp: new Date().toISOString()
    };
    
    this.executionHistory.push(record);
    
    // 保持历史记录在合理范围内
    if (this.executionHistory.length > 1000) {
      this.executionHistory = this.executionHistory.slice(-500);
    }
  }

  /**
   * 获取传输统计
   */
  getTransmissionStats() {
    const total = this.executionHistory.length;
    const successful = this.executionHistory.filter(r => r.transmissionResult.success).length;
    const failed = total - successful;
    
    return {
      total,
      successful,
      failed,
      successRate: total > 0 ? (successful / total * 100).toFixed(2) : 0,
      recentTransmissions: this.executionHistory.slice(-10)
    };
  }

  // 辅助方法
  generateOrderId() {
    return `ORDER_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  calculateOptimalQuantity(decision) {
    // 基于置信度和风险评估计算最优数量
    const baseQuantity = 1000;
    const confidenceMultiplier = decision.confidence;
    return Math.floor(baseQuantity * confidenceMultiplier);
  }

  calculateExecutionPriority(decision) {
    if (decision.confidence > 0.8) return 'HIGH';
    if (decision.confidence > 0.6) return 'MEDIUM';
    return 'LOW';
  }

  generateSecurityHash(orderId, decision) {
    const data = `${orderId}_${decision.action}_${decision.confidence}_${Date.now()}`;
    return btoa(data).substr(0, 16);
  }

  calculateChecksum(data) {
    let hash = 0;
    for (let i = 0; i < data.length; i++) {
      const char = data.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32-bit integer
    }
    return hash.toString(16);
  }

  getTodayOrderCount() {
    const today = new Date().toDateString();
    return this.executionHistory.filter(r => 
      new Date(r.timestamp).toDateString() === today
    ).length;
  }

  getRecentOrderCount(timeWindow) {
    const cutoff = Date.now() - timeWindow;
    return this.executionHistory.filter(r => 
      new Date(r.timestamp).getTime() > cutoff
    ).length;
  }

  isValidStockSymbol(symbol) {
    // 简化的股票代码验证
    return /^[0-9]{6}$/.test(symbol);
  }

  isValidTradingTime() {
    const now = new Date();
    const hour = now.getHours();
    const minute = now.getMinutes();
    const day = now.getDay();
    
    // 工作日检查
    if (day === 0 || day === 6) return false;
    
    // 交易时间检查
    const currentTime = hour * 60 + minute;
    const morningStart = 9 * 60 + 30;
    const morningEnd = 11 * 60 + 30;
    const afternoonStart = 13 * 60;
    const afternoonEnd = 15 * 60;
    
    return (currentTime >= morningStart && currentTime <= morningEnd) ||
           (currentTime >= afternoonStart && currentTime <= afternoonEnd);
  }

  selectTransmissionMethod() {
    // 优先选择WebSocket,其次HTTP,最后Webhook
    if (this.hasActiveLocalConnection()) return 'websocket';
    if (this.hasLocalEndpoint()) return 'http';
    return 'webhook';
  }

  hasActiveLocalConnection() {
    const connection = this.localConnections.get('primary');
    return connection && connection.readyState === WebSocket.OPEN;
  }

  hasLocalEndpoint() {
    return !!this.getLocalEndpoint();
  }

  getLocalConnection() {
    return this.localConnections.get('primary');
  }

  getLocalEndpoint() {
    // 这里应该从配置中获取本地端点
    return 'http://localhost:8080/api/trading-orders';
  }

  getWebhookUrl() {
    // 这里应该从配置中获取Webhook URL
    return 'http://localhost:8080/webhook/trading-orders';
  }

  async waitForConfirmation(orderId, timeout = 5000) {
    return new Promise((resolve) => {
      const timer = setTimeout(() => {
        resolve({ confirmed: false, reason: 'timeout' });
      }, timeout);
      
      // 模拟确认逻辑
      setTimeout(() => {
        clearTimeout(timer);
        resolve({ confirmed: true, orderId });
      }, 1000);
    });
  }
}

// 导出桥接器
const tradingBridge = new CloudToLocalTradingBridge();

export { tradingBridge, CloudToLocalTradingBridge };
