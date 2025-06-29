import request from '@/utils/request';

/**
 * External Strategy Research Service
 * Provides methods to interact with the external strategy research API
 */
const externalStrategyService = {
  /**
   * Search for and analyze external trading strategies
   * @param {string} query - Search query
   * @param {string} language - Language ('en' or 'cn')
   * @param {number} maxResults - Maximum number of results
   * @returns {Promise} - Promise with research results
   */
  async researchStrategies(query, language = 'en', maxResults = 5) {
    return request({
      url: '/api/ai/research/strategies',
      method: 'post',
      data: { query, language, max_results: maxResults }
    });
  },

  /**
   * Get strategies from top performing traders
   * @param {string} market - Target market ('global', 'us', 'china', etc.)
   * @param {number} traderCount - Number of top traders to analyze
   * @returns {Promise} - Promise with top trader strategies
   */
  async getTopTraderStrategies(market = 'global', traderCount = 5) {
    return request({
      url: '/api/ai/research/top-traders',
      method: 'get',
      params: { market, trader_count: traderCount }
    });
  },

  /**
   * Get the status of external strategy learning
   * @returns {Promise} - Promise with learning status
   */
  async getLearningStatus() {
    return request({
      url: '/api/ai/research/status',
      method: 'get'
    });
  },

  /**
   * Schedule automatic research of external strategies
   * @param {boolean} enabled - Whether to enable automatic research
   * @param {number} intervalHours - Interval between research runs in hours
   * @returns {Promise} - Promise with schedule status
   */
  async scheduleResearch(enabled = true, intervalHours = 24) {
    return request({
      url: '/api/ai/research/schedule',
      method: 'post',
      data: { enabled, interval_hours: intervalHours }
    });
  }
};

export default externalStrategyService; 
