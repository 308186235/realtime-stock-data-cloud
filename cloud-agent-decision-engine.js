/**
 * 云端Agent决策引擎
 * 基于实时市场数据做出智能交易决策
 */

class CloudAgentDecisionEngine {
    constructor() {
        this.config = {
            // 风险控制参数
            maxPositionSize: 0.1,      // 单只股票最大仓位10%
            maxDailyTrades: 20,        // 每日最大交易次数
            stopLossRatio: 0.05,       // 止损比例5%
            takeProfitRatio: 0.15,     // 止盈比例15%
            
            // 技术指标参数
            maShort: 5,                // 短期均线
            maLong: 20,                // 长期均线
            rsiPeriod: 14,             // RSI周期
            rsiOverbought: 70,         // RSI超买线
            rsiOversold: 30,           // RSI超卖线
            
            // 交易时间控制
            tradingStartTime: '09:30', // 交易开始时间
            tradingEndTime: '15:00',   // 交易结束时间
            
            // 资金管理
            totalCapital: 1000000,     // 总资金
            maxRiskPerTrade: 0.02,     // 单笔交易最大风险2%
        };
        
        this.positions = new Map();    // 当前持仓
        this.orders = new Map();       // 当前委托
        this.dailyTrades = 0;          // 今日交易次数
        this.lastDecisionTime = null;  // 上次决策时间
    }
    
    /**
     * 主决策函数
     * @param {Object} marketData - 市场数据
     * @param {Object} portfolioData - 投资组合数据
     * @returns {Array} 交易指令列表
     */
    async makeDecisions(marketData, portfolioData) {
        console.log('🤖 云端Agent开始决策分析...');
        
        try {
            // 1. 更新投资组合状态
            this.updatePortfolioStatus(portfolioData);
            
            // 2. 检查交易时间
            if (!this.isInTradingTime()) {
                console.log('⏰ 非交易时间,跳过决策');
                return [];
            }
            
            // 3. 检查日交易限制
            if (this.dailyTrades >= this.config.maxDailyTrades) {
                console.log('🛑 已达到日交易限制,停止交易');
                return [];
            }
            
            // 4. 分析市场数据
            const marketAnalysis = this.analyzeMarket(marketData);
            
            // 5. 生成交易信号
            const signals = this.generateTradingSignals(marketAnalysis);
            
            // 6. 风险控制检查
            const validSignals = this.riskControlCheck(signals);
            
            // 7. 生成交易指令
            const orders = this.generateOrders(validSignals);
            
            console.log(`📊 生成 ${orders.length} 个交易指令`);
            return orders;
            
        } catch (error) {
            console.error('❌ 决策引擎异常:', error);
            return [];
        }
    }
    
    /**
     * 分析市场数据
     */
    analyzeMarket(marketData) {
        const analysis = {};
        
        for (const [stockCode, data] of Object.entries(marketData)) {
            try {
                const stockAnalysis = {
                    stockCode: stockCode,
                    currentPrice: data.current_price,
                    volume: data.volume,
                    
                    // 技术指标
                    ma5: this.calculateMA(data.prices, this.config.maShort),
                    ma20: this.calculateMA(data.prices, this.config.maLong),
                    rsi: this.calculateRSI(data.prices, this.config.rsiPeriod),
                    
                    // 价格变化
                    priceChange: data.price_change,
                    priceChangePercent: data.price_change_percent,
                    
                    // 成交量分析
                    volumeRatio: this.calculateVolumeRatio(data),
                    
                    // 市场情绪
                    sentiment: this.analyzeSentiment(data),
                    
                    // 趋势判断
                    trend: this.analyzeTrend(data)
                };
                
                analysis[stockCode] = stockAnalysis;
                
            } catch (error) {
                console.error(`分析股票 ${stockCode} 失败:`, error);
            }
        }
        
        return analysis;
    }
    
    /**
     * 生成交易信号
     */
    generateTradingSignals(marketAnalysis) {
        const signals = [];
        
        for (const [stockCode, analysis] of Object.entries(marketAnalysis)) {
            try {
                const signal = this.analyzeStock(analysis);
                if (signal.action !== 'hold') {
                    signals.push(signal);
                }
            } catch (error) {
                console.error(`生成信号失败 ${stockCode}:`, error);
            }
        }
        
        // 按信号强度排序
        signals.sort((a, b) => b.strength - a.strength);
        
        return signals;
    }
    
    /**
     * 分析单只股票
     */
    analyzeStock(analysis) {
        const { stockCode, currentPrice, ma5, ma20, rsi, trend, sentiment, volumeRatio } = analysis;
        
        let action = 'hold';
        let strength = 0;
        let reason = [];
        
        // 均线策略
        if (ma5 > ma20 && currentPrice > ma5) {
            action = 'buy';
            strength += 30;
            reason.push('均线多头排列');
        } else if (ma5 < ma20 && currentPrice < ma5) {
            action = 'sell';
            strength += 30;
            reason.push('均线空头排列');
        }
        
        // RSI策略
        if (rsi < this.config.rsiOversold) {
            if (action === 'buy') strength += 20;
            else if (action === 'hold') {
                action = 'buy';
                strength += 15;
            }
            reason.push('RSI超卖');
        } else if (rsi > this.config.rsiOverbought) {
            if (action === 'sell') strength += 20;
            else if (action === 'hold') {
                action = 'sell';
                strength += 15;
            }
            reason.push('RSI超买');
        }
        
        // 趋势确认
        if (trend === 'uptrend' && action === 'buy') {
            strength += 15;
            reason.push('上升趋势确认');
        } else if (trend === 'downtrend' && action === 'sell') {
            strength += 15;
            reason.push('下降趋势确认');
        }
        
        // 成交量确认
        if (volumeRatio > 1.5) {
            strength += 10;
            reason.push('成交量放大');
        }
        
        // 市场情绪
        if (sentiment === 'positive' && action === 'buy') {
            strength += 10;
            reason.push('市场情绪积极');
        } else if (sentiment === 'negative' && action === 'sell') {
            strength += 10;
            reason.push('市场情绪消极');
        }
        
        return {
            stockCode,
            action,
            strength,
            reason: reason.join(', '),
            currentPrice,
            analysis
        };
    }
    
    /**
     * 风险控制检查
     */
    riskControlCheck(signals) {
        const validSignals = [];
        
        for (const signal of signals) {
            try {
                // 检查持仓限制
                if (signal.action === 'buy') {
                    const currentPosition = this.positions.get(signal.stockCode) || 0;
                    const maxPosition = this.config.totalCapital * this.config.maxPositionSize;
                    
                    if (currentPosition >= maxPosition) {
                        console.log(`⚠️ ${signal.stockCode} 已达到最大仓位限制`);
                        continue;
                    }
                }
                
                // 检查资金风险
                const riskAmount = this.config.totalCapital * this.config.maxRiskPerTrade;
                const stopLossPrice = signal.currentPrice * (1 - this.config.stopLossRatio);
                const maxQuantity = Math.floor(riskAmount / (signal.currentPrice - stopLossPrice));
                
                if (maxQuantity <= 0) {
                    console.log(`⚠️ ${signal.stockCode} 风险过大,跳过交易`);
                    continue;
                }
                
                signal.maxQuantity = maxQuantity;
                validSignals.push(signal);
                
            } catch (error) {
                console.error(`风险检查失败 ${signal.stockCode}:`, error);
            }
        }
        
        return validSignals;
    }
    
    /**
     * 生成交易指令
     */
    generateOrders(signals) {
        const orders = [];
        
        for (const signal of signals) {
            try {
                const order = {
                    commandId: this.generateCommandId(),
                    stockCode: signal.stockCode,
                    action: signal.action,
                    orderType: 'limit',
                    price: this.calculateOrderPrice(signal),
                    quantity: this.calculateOrderQuantity(signal),
                    strategy: signal.reason,
                    riskLevel: this.calculateRiskLevel(signal),
                    stopLoss: this.calculateStopLoss(signal),
                    takeProfit: this.calculateTakeProfit(signal),
                    timestamp: new Date().toISOString(),
                    priority: signal.strength
                };
                
                orders.push(order);
                
            } catch (error) {
                console.error(`生成订单失败 ${signal.stockCode}:`, error);
            }
        }
        
        return orders;
    }
    
    /**
     * 计算移动平均线
     */
    calculateMA(prices, period) {
        if (!prices || prices.length < period) return null;
        
        const sum = prices.slice(-period).reduce((a, b) => a + b, 0);
        return sum / period;
    }
    
    /**
     * 计算RSI
     */
    calculateRSI(prices, period) {
        if (!prices || prices.length < period + 1) return 50;
        
        let gains = 0;
        let losses = 0;
        
        for (let i = prices.length - period; i < prices.length; i++) {
            const change = prices[i] - prices[i - 1];
            if (change > 0) {
                gains += change;
            } else {
                losses -= change;
            }
        }
        
        const avgGain = gains / period;
        const avgLoss = losses / period;
        
        if (avgLoss === 0) return 100;
        
        const rs = avgGain / avgLoss;
        return 100 - (100 / (1 + rs));
    }
    
    /**
     * 检查是否在交易时间内
     */
    isInTradingTime() {
        const now = new Date();
        const currentTime = now.toTimeString().slice(0, 5);
        
        return currentTime >= this.config.tradingStartTime && 
               currentTime <= this.config.tradingEndTime;
    }
    
    /**
     * 生成命令ID
     */
    generateCommandId() {
        const timestamp = Date.now();
        const random = Math.random().toString(36).substr(2, 6);
        return `CMD_${timestamp}_${random}`;
    }
    
    /**
     * 更新投资组合状态
     */
    updatePortfolioStatus(portfolioData) {
        if (portfolioData && portfolioData.positions) {
            this.positions.clear();
            portfolioData.positions.forEach(pos => {
                this.positions.set(pos.stockCode, pos.marketValue);
            });
        }
    }
    
    /**
     * 计算订单价格
     */
    calculateOrderPrice(signal) {
        // 买入时略高于当前价,卖出时略低于当前价
        const adjustment = signal.action === 'buy' ? 1.001 : 0.999;
        return Math.round(signal.currentPrice * adjustment * 100) / 100;
    }
    
    /**
     * 计算订单数量
     */
    calculateOrderQuantity(signal) {
        const baseQuantity = Math.min(signal.maxQuantity || 1000, 1000);
        
        // 根据信号强度调整数量
        const strengthMultiplier = Math.min(signal.strength / 50, 2);
        
        return Math.floor(baseQuantity * strengthMultiplier / 100) * 100; // 整百股
    }
    
    /**
     * 计算风险等级
     */
    calculateRiskLevel(signal) {
        if (signal.strength >= 70) return 'low';
        if (signal.strength >= 40) return 'medium';
        return 'high';
    }
    
    /**
     * 计算止损价
     */
    calculateStopLoss(signal) {
        if (signal.action === 'buy') {
            return signal.currentPrice * (1 - this.config.stopLossRatio);
        } else {
            return signal.currentPrice * (1 + this.config.stopLossRatio);
        }
    }
    
    /**
     * 计算止盈价
     */
    calculateTakeProfit(signal) {
        if (signal.action === 'buy') {
            return signal.currentPrice * (1 + this.config.takeProfitRatio);
        } else {
            return signal.currentPrice * (1 - this.config.takeProfitRatio);
        }
    }
    
    // 其他辅助方法...
    calculateVolumeRatio(data) { return 1.2; }
    analyzeSentiment(data) { return 'neutral'; }
    analyzeTrend(data) { return 'sideways'; }
}

// 导出决策引擎
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CloudAgentDecisionEngine;
} else if (typeof window !== 'undefined') {
    window.CloudAgentDecisionEngine = CloudAgentDecisionEngine;
}
