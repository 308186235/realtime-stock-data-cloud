/**
 * User Vuex Module
 * Manages user authentication, profile, and settings
 */

import { get, post } from '../../utils/request';

// Initial state
const state = {
  token: null,
  userInfo: null,
  isLoggedIn: false,
  accountBalance: 0,
  tradingPermissions: {
    canTrade: false,
    restrictions: []
  },
  settings: {
    theme: 'light',
    notification: true,
    language: 'en'
  },
  loading: false,
  error: null
};

// Getters
const getters = {
  isLoggedIn: state => state.isLoggedIn,
  username: state => state.userInfo ? state.userInfo.username : '',
  canTrade: state => state.tradingPermissions.canTrade,
  accountBalance: state => state.accountBalance,
  userSettings: state => state.settings
};

// Mutations
const mutations = {
  SET_TOKEN(state, token) {
    state.token = token;
    state.isLoggedIn = !!token;
    
    // Save token to storage
    if (token) {
      uni.setStorageSync('token', token);
    } else {
      uni.removeStorageSync('token');
    }
  },
  SET_USER_INFO(state, userInfo) {
    state.userInfo = userInfo;
  },
  SET_ACCOUNT_BALANCE(state, balance) {
    state.accountBalance = balance;
  },
  SET_TRADING_PERMISSIONS(state, permissions) {
    state.tradingPermissions = permissions;
  },
  SET_USER_SETTINGS(state, settings) {
    state.settings = {
      ...state.settings,
      ...settings
    };
  },
  SET_LOADING(state, status) {
    state.loading = status;
  },
  SET_ERROR(state, error) {
    state.error = error;
  },
  CLEAR_USER_DATA(state) {
    state.token = null;
    state.userInfo = null;
    state.isLoggedIn = false;
    state.accountBalance = 0;
    state.tradingPermissions = {
      canTrade: false,
      restrictions: []
    };
    
    // Clear token from storage
    uni.removeStorageSync('token');
  }
};

// Actions
const actions = {
  /**
   * Login user
   */
  async login({ commit, dispatch }, { username, password }) {
    try {
      commit('SET_LOADING', true);
      commit('SET_ERROR', null);
      
      const response = await post('/api/user/login', { username, password });
      
      if (response && response.code === 200 && response.data) {
        // Set token
        commit('SET_TOKEN', response.data.token);
        
        // Load user info
        await dispatch('loadUserInfo');
        
        // Load account balance
        await dispatch('loadAccountBalance');
        
        // Show success message
        uni.showToast({
          title: 'Login successful',
          icon: 'success'
        });
        
        return true;
      }
      
      return false;
    } catch (error) {
      console.error('Login failed:', error);
      commit('SET_ERROR', error.message || 'Login failed');
      
      uni.showToast({
        title: error.message || 'Login failed',
        icon: 'none'
      });
      
      return false;
    } finally {
      commit('SET_LOADING', false);
    }
  },
  
  /**
   * Logout user
   */
  async logout({ commit }) {
    try {
      // Try to logout on server
      try {
        await post('/api/user/logout');
      } catch (error) {
        console.error('Logout API call failed:', error);
      }
      
      // Clear user data regardless of server response
      commit('CLEAR_USER_DATA');
      
      // Show success message
      uni.showToast({
        title: 'Logged out successfully',
        icon: 'success'
      });
      
      // Redirect to login page
      setTimeout(() => {
        uni.reLaunch({
          url: '/pages/login/index'
        });
      }, 1000);
      
      return true;
    } catch (error) {
      console.error('Logout failed:', error);
      return false;
    }
  },
  
  /**
   * Load user information
   */
  async loadUserInfo({ commit, state }) {
    if (!state.token) {
      const storedToken = uni.getStorageSync('token');
      if (storedToken) {
        commit('SET_TOKEN', storedToken);
      } else {
        return false;
      }
    }
    
    try {
      commit('SET_LOADING', true);
      
      const response = await get('/api/user/profile');
      
      if (response && response.code === 200 && response.data) {
        commit('SET_USER_INFO', response.data);
        
        // Set trading permissions
        if (response.data.tradingPermissions) {
          commit('SET_TRADING_PERMISSIONS', response.data.tradingPermissions);
        }
        
        return true;
      }
      
      return false;
    } catch (error) {
      console.error('Failed to load user info:', error);
      
      // If unauthorized, clear user data
      if (error.category === 'unauthorized') {
        commit('CLEAR_USER_DATA');
      }
      
      return false;
    } finally {
      commit('SET_LOADING', false);
    }
  },
  
  /**
   * Load account balance
   */
  async loadAccountBalance({ commit, state }) {
    if (!state.isLoggedIn) return false;
    
    try {
      const response = await get('/api/account/balance');
      
      if (response && response.code === 200 && response.data) {
        commit('SET_ACCOUNT_BALANCE', response.data.balance || 0);
        return true;
      }
      
      return false;
    } catch (error) {
      console.error('Failed to load account balance:', error);
      return false;
    }
  },
  
  /**
   * Update user settings
   */
  async updateSettings({ commit, state }, settings) {
    commit('SET_USER_SETTINGS', settings);
    
    // Save settings to storage
    uni.setStorageSync('user_settings', JSON.stringify(state.settings));
    
    // If logged in, sync with server
    if (state.isLoggedIn) {
      try {
        await post('/api/user/settings', { settings: state.settings });
      } catch (error) {
        console.error('Failed to sync settings with server:', error);
      }
    }
  },
  
  /**
   * Load saved settings from storage
   */
  loadSettings({ commit }) {
    try {
      const settings = uni.getStorageSync('user_settings');
      if (settings) {
        commit('SET_USER_SETTINGS', JSON.parse(settings));
      }
    } catch (error) {
      console.error('Failed to load settings from storage:', error);
    }
  }
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}; 
 
