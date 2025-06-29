/**
 * System Vuex Module
 * Manages system-wide state, configuration and app status
 */

import env from '../../env';
import { get } from '../../utils/request';

// Initial state
const state = {
  appReady: false,
  systemInfo: null,
  marketStatus: {
    isOpen: false,
    nextOpenTime: null,
    nextCloseTime: null
  },
  networkStatus: {
    isConnected: true,
    type: 'unknown'
  },
  serverTime: null,
  timeOffset: 0,
  environment: env.current.name,
  serverVersion: null,
  notifications: []
};

// Getters
const getters = {
  isAppReady: state => state.appReady,
  isMarketOpen: state => state.marketStatus.isOpen,
  isNetworkConnected: state => state.networkStatus.isConnected,
  networkType: state => state.networkStatus.type,
  currentEnvironment: state => state.environment,
  systemTime: state => {
    const now = new Date();
    // Apply server time offset if available
    if (state.timeOffset) {
      now.setTime(now.getTime() + state.timeOffset);
    }
    return now;
  },
  // Format: HH:MM:SS
  formattedSystemTime: (state, getters) => {
    const time = getters.systemTime;
    return `${String(time.getHours()).padStart(2, '0')}:${String(time.getMinutes()).padStart(2, '0')}:${String(time.getSeconds()).padStart(2, '0')}`;
  },
  hasActiveNotifications: state => state.notifications.length > 0
};

// Mutations
const mutations = {
  SET_APP_READY(state, status) {
    state.appReady = status;
  },
  SET_SYSTEM_INFO(state, info) {
    state.systemInfo = info;
  },
  SET_MARKET_STATUS(state, status) {
    state.marketStatus = status;
  },
  SET_NETWORK_STATUS(state, status) {
    state.networkStatus = status;
  },
  SET_SERVER_TIME(state, time) {
    state.serverTime = time;
    
    // Calculate offset between local time and server time
    const localTime = new Date().getTime();
    const serverTime = new Date(time).getTime();
    state.timeOffset = serverTime - localTime;
  },
  SET_SERVER_VERSION(state, version) {
    state.serverVersion = version;
  },
  ADD_NOTIFICATION(state, notification) {
    // Add notification with unique ID
    const id = notification.id || Date.now().toString();
    state.notifications.push({
      ...notification,
      id,
      timestamp: new Date().toISOString()
    });
  },
  REMOVE_NOTIFICATION(state, id) {
    state.notifications = state.notifications.filter(n => n.id !== id);
  },
  CLEAR_NOTIFICATIONS(state) {
    state.notifications = [];
  }
};

// Actions
const actions = {
  /**
   * Initialize system module
   */
  async init({ commit, dispatch }) {
    // Get system info
    const systemInfo = uni.getSystemInfoSync();
    commit('SET_SYSTEM_INFO', systemInfo);
    
    // Set up network status monitoring
    dispatch('monitorNetworkStatus');
    
    // Load server time and version info
    await dispatch('loadServerInfo');
    
    // Load market status
    await dispatch('loadMarketStatus');
    
    // Set up market status monitoring
    dispatch('startMarketStatusMonitor');
    
    // App is ready
    commit('SET_APP_READY', true);
  },
  
  /**
   * Monitor network status changes
   */
  monitorNetworkStatus({ commit }) {
    // Set initial network status
    uni.getNetworkType({
      success: (res) => {
        commit('SET_NETWORK_STATUS', {
          isConnected: res.networkType !== 'none',
          type: res.networkType
        });
      }
    });
    
    // Listen for network status changes
    uni.onNetworkStatusChange((res) => {
      commit('SET_NETWORK_STATUS', {
        isConnected: res.isConnected,
        type: res.networkType
      });
      
      // Show toast when network status changes
      if (res.isConnected) {
        uni.showToast({
          title: 'Network connection restored',
          icon: 'success'
        });
      } else {
        uni.showToast({
          title: 'Network connection lost',
          icon: 'none'
        });
      }
    });
  },
  
  /**
   * Load server information
   */
  async loadServerInfo({ commit }) {
    try {
      const response = await get('/api/system/info');
      
      if (response && response.code === 200 && response.data) {
        if (response.data.serverTime) {
          commit('SET_SERVER_TIME', response.data.serverTime);
        }
        
        if (response.data.version) {
          commit('SET_SERVER_VERSION', response.data.version);
        }
      }
    } catch (error) {
      console.error('Failed to load server info:', error);
    }
  },
  
  /**
   * Load market status
   */
  async loadMarketStatus({ commit }) {
    try {
      const response = await get('/api/market/status');
      
      if (response && response.code === 200 && response.data) {
        commit('SET_MARKET_STATUS', {
          isOpen: response.data.isOpen || false,
          nextOpenTime: response.data.nextOpenTime,
          nextCloseTime: response.data.nextCloseTime
        });
        
        return response.data;
      }
    } catch (error) {
      console.error('Failed to load market status:', error);
      
      // Set default status
      commit('SET_MARKET_STATUS', {
        isOpen: false,
        nextOpenTime: null,
        nextCloseTime: null
      });
    }
  },
  
  /**
   * Start market status monitor
   */
  startMarketStatusMonitor({ dispatch }) {
    // Check market status every 5 minutes
    setInterval(() => {
      dispatch('loadMarketStatus');
    }, 5 * 60 * 1000);
  },
  
  /**
   * Add notification
   */
  addNotification({ commit }, notification) {
    commit('ADD_NOTIFICATION', notification);
    
    // Auto-remove after timeout if specified
    if (notification.timeout) {
      setTimeout(() => {
        commit('REMOVE_NOTIFICATION', notification.id || Date.now().toString());
      }, notification.timeout);
    }
  },
  
  /**
   * Remove notification
   */
  removeNotification({ commit }, id) {
    commit('REMOVE_NOTIFICATION', id);
  },
  
  /**
   * Clear all notifications
   */
  clearNotifications({ commit }) {
    commit('CLEAR_NOTIFICATIONS');
  }
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}; 
 
