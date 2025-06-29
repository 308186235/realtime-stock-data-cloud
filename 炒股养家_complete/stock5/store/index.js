import Vue from 'vue';
import Vuex from 'vuex';
import createPersistedState from 'vuex-persistedstate';

// Import modules
import trading from './modules/trading';
import stocks from './modules/stocks';
import user from './modules/user';
import system from './modules/system';

Vue.use(Vuex);

// Root state
const state = {
  appVersion: '1.0.0',
  lastUpdated: null
};

// Root mutations
const mutations = {
  UPDATE_LAST_UPDATED(state) {
    state.lastUpdated = new Date().toISOString();
  }
};

// Root actions
const actions = {
  init({ commit, dispatch }) {
    // Initialize app
    commit('UPDATE_LAST_UPDATED');
    
    // Initialize modules
    dispatch('system/init');
    dispatch('user/loadUserInfo');
    dispatch('stocks/loadWatchlist');
    dispatch('trading/loadTradingStatus');
  }
};

// Create store
const store = new Vuex.Store({
  state,
  mutations,
  actions,
  modules: {
    trading,
    stocks,
    user,
    system
  },
  // Enable strict mode in development for better debugging
  strict: process.env.NODE_ENV !== 'production',
  // Persist state to localStorage (with customization)
  plugins: [
    createPersistedState({
      key: 'stock5-store',
      paths: [
        'user.token',
        'user.userInfo',
        'stocks.watchlist',
        'trading.tradingPreferences'
      ]
    })
  ]
});

export default store; 
 
