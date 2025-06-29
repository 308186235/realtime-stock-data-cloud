/**
 * Trading Vuex Module
 * Manages trading operations, strategies, and trading session state
 */

import { get, post } from '../../utils/request';

// Initial state
const state = {
  isTradingDay: false,
  currentStrategy: null,
  tradingPreferences: {
    defaultQuantity: 100,
    autoEvaluate: false,
    riskTolerance: 'medium' // 'low', 'medium', 'high'
  },
  activeTrades: [],
  tradingHistory: [],
  dailyStats: {
    trades: 0,
    successful: 0,
    profit: 0
  },
  currentOpportunity: null,
  evaluationLoading: false,
  evaluationError: null
};

// Getters
const getters = {
  isTradingActive: state => state.isTradingDay,
  currentProfit: state => state.dailyStats.profit,
  successRate: state => {
    if (state.dailyStats.trades === 0) return 0;
    return (state.dailyStats.successful / state.dailyStats.trades) * 100;
  },
  hasActiveOpportunity: state => state.currentOpportunity && state.currentOpportunity.has_opportunity,
  recommendedAction: state => {
    if (!state.currentOpportunity || !state.currentOpportunity.has_opportunity) return null;
    return state.currentOpportunity.mode === 'positive' ? 'buy' : 'sell';
  },
  activeTrades: state => state.activeTrades
};

// Mutations
const mutations = {
  SET_TRADING_DAY(state, status) {
    state.isTradingDay = status;
  },
  SET_CURRENT_STRATEGY(state, strategy) {
    state.currentStrategy = strategy;
  },
  SET_TRADING_PREFERENCES(state, preferences) {
    state.tradingPreferences = {
      ...state.tradingPreferences,
      ...preferences
    };
  },
  SET_DAILY_STATS(state, stats) {
    state.dailyStats = stats;
  },
  SET_CURRENT_OPPORTUNITY(state, opportunity) {
    state.currentOpportunity = opportunity;
  },
  SET_EVALUATION_LOADING(state, status) {
    state.evaluationLoading = status;
  },
  SET_EVALUATION_ERROR(state, error) {
    state.evaluationError = error;
  },
  ADD_ACTIVE_TRADE(state, trade) {
    state.activeTrades.push(trade);
  },
  UPDATE_ACTIVE_TRADE(state, { tradeId, updates }) {
    const index = state.activeTrades.findIndex(trade => trade.id === tradeId);
    if (index !== -1) {
      state.activeTrades[index] = {
        ...state.activeTrades[index],
        ...updates
      };
    }
  },
  REMOVE_ACTIVE_TRADE(state, tradeId) {
    state.activeTrades = state.activeTrades.filter(trade => trade.id !== tradeId);
  },
  ADD_TRADING_HISTORY(state, trade) {
    state.tradingHistory.unshift(trade);
  },
  CLEAR_TRADING_DATA(state) {
    state.activeTrades = [];
    state.currentOpportunity = null;
  }
};

// Actions
const actions = {
  /**
   * Load current trading status
   */
  async loadTradingStatus({ commit }) {
    try {
      const response = await get('/api/t-trading/summary');
      if (response && response.data) {
        // Update trading day status
        commit('SET_TRADING_DAY', response.data.is_trading_day || false);
        
        // Update daily statistics
        commit('SET_DAILY_STATS', {
          trades: response.data.total_trades || 0,
          successful: Math.round(response.data.total_trades * response.data.success_rate) || 0,
          profit: response.data.total_profit || 0
        });
      }
    } catch (error) {
      console.error('Failed to load trading status:', error);
    }
  },
  
  /**
   * Start trading day
   */
  async startTradingDay({ commit }) {
    try {
      const response = await post('/api/t-trading/start-trading-day');
      
      if (response && response.code === 200) {
        commit('SET_TRADING_DAY', true);
        
        // Display success message
        uni.showToast({
          title: 'Trading day started successfully',
          icon: 'success'
        });
        
        return true;
      }
      return false;
    } catch (error) {
      console.error('Failed to start trading day:', error);
      uni.showToast({
        title: 'Failed to start trading day',
        icon: 'none'
      });
      return false;
    }
  },
  
  /**
   * End trading day
   */
  async endTradingDay({ commit }) {
    try {
      const response = await post('/api/t-trading/end-trading-day');
      
      if (response && response.code === 200) {
        commit('SET_TRADING_DAY', false);
        
        // Update daily statistics
        if (response.data && response.data.summary) {
          commit('SET_DAILY_STATS', {
            trades: response.data.summary.total_trades || 0,
            successful: response.data.summary.successful_trades || 0,
            profit: response.data.summary.total_profit || 0
          });
        }
        
        // Clear active trades and current opportunity
        commit('CLEAR_TRADING_DATA');
        
        // Display success message
        uni.showToast({
          title: 'Trading day ended successfully',
          icon: 'success'
        });
        
        return true;
      }
      return false;
    } catch (error) {
      console.error('Failed to end trading day:', error);
      uni.showToast({
        title: 'Failed to end trading day',
        icon: 'none'
      });
      return false;
    }
  },
  
  /**
   * Evaluate trading opportunity
   */
  async evaluateOpportunity({ commit, state }, stockData) {
    if (!stockData || !stockData.code) {
      uni.showToast({
        title: 'Invalid stock data',
        icon: 'none'
      });
      return null;
    }
    
    try {
      commit('SET_EVALUATION_LOADING', true);
      commit('SET_EVALUATION_ERROR', null);
      
      const data = {
        code: stockData.code,
        name: stockData.name,
        current_price: stockData.currentPrice,
        open_price: stockData.open,
        intraday_high: stockData.high,
        intraday_low: stockData.low,
        avg_volume: stockData.volume / 2, // Simplified calculation
        current_volume: stockData.volume,
        base_position: stockData.basePosition,
        base_cost: stockData.baseCost,
        risk_tolerance: state.tradingPreferences.riskTolerance
      };
      
      const response = await post('/api/t-trading/evaluate-opportunity', data);
      
      if (response && response.code === 200) {
        commit('SET_CURRENT_OPPORTUNITY', response.data);
        return response.data;
      }
      
      return null;
    } catch (error) {
      console.error('Failed to evaluate opportunity:', error);
      commit('SET_EVALUATION_ERROR', error.message || 'Failed to evaluate opportunity');
      uni.showToast({
        title: 'Failed to evaluate opportunity',
        icon: 'none'
      });
      return null;
    } finally {
      commit('SET_EVALUATION_LOADING', false);
    }
  },
  
  /**
   * Execute trade action
   */
  async executeTrade({ commit, state }, { stockInfo, tradeType }) {
    if (!state.currentOpportunity || !state.currentOpportunity.has_opportunity) {
      uni.showToast({
        title: 'No valid trading opportunity',
        icon: 'none'
      });
      return false;
    }
    
    try {
      const data = {
        stock_code: stockInfo.code,
        stock_name: stockInfo.name,
        price: stockInfo.currentPrice,
        quantity: state.currentOpportunity.suggested_quantity,
        trade_type: tradeType,
        mode: state.currentOpportunity.mode
      };
      
      const response = await post('/api/t-trading/record-trade', data);
      
      if (response && response.code === 200) {
        // Add to active trades
        const newTrade = {
          id: response.data.trade_id || Date.now().toString(),
          stockCode: stockInfo.code,
          stockName: stockInfo.name,
          price: stockInfo.currentPrice,
          quantity: state.currentOpportunity.suggested_quantity,
          tradeType,
          mode: state.currentOpportunity.mode,
          status: 'active',
          timestamp: new Date().toISOString()
        };
        
        commit('ADD_ACTIVE_TRADE', newTrade);
        
        // Update stats
        await dispatch('loadTradingStatus');
        
        uni.showToast({
          title: `${tradeType === 'buy' ? 'Buy' : 'Sell'} order executed successfully`,
          icon: 'success'
        });
        
        return true;
      }
      
      return false;
    } catch (error) {
      console.error('Failed to execute trade:', error);
      uni.showToast({
        title: 'Failed to execute trade',
        icon: 'none'
      });
      return false;
    }
  },
  
  /**
   * Update trading preferences
   */
  updatePreferences({ commit }, preferences) {
    commit('SET_TRADING_PREFERENCES', preferences);
  },
  
  /**
   * Clear current opportunity
   */
  clearCurrentOpportunity({ commit }) {
    commit('SET_CURRENT_OPPORTUNITY', null);
  }
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}; 
 
