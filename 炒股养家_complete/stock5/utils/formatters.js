/**
 * Formatting Utilities
 * Provides functions for consistent data formatting
 */

/**
 * Format currency/money values
 * @param {Number} value - The value to format
 * @param {Number} decimals - Number of decimal places
 * @param {String} currency - Currency symbol
 * @returns {String} Formatted money value
 */
export const formatMoney = (value, decimals = 2, currency = '¥') => {
  if (typeof value !== 'number') {
    value = Number(value) || 0;
  }
  
  return `${currency}${value.toFixed(decimals).replace(/\B(?=(\d{3})+(?!\d))/g, ',')}`;
};

/**
 * Format large numbers with K, M, B suffixes
 * @param {Number} value - The value to format
 * @param {Number} decimals - Number of decimal places
 * @returns {String} Formatted number
 */
export const formatLargeNumber = (value, decimals = 1) => {
  if (typeof value !== 'number') {
    value = Number(value) || 0;
  }
  
  if (value >= 1000000000) {
    return `${(value / 1000000000).toFixed(decimals)}B`;
  } else if (value >= 1000000) {
    return `${(value / 1000000).toFixed(decimals)}M`;
  } else if (value >= 1000) {
    return `${(value / 1000).toFixed(decimals)}K`;
  }
  
  return value.toString();
};

/**
 * Format trading volume
 * @param {Number} volume - The volume to format
 * @returns {String} Formatted volume
 */
export const formatVolume = (volume) => {
  return formatLargeNumber(volume, 2);
};

/**
 * Format percentage
 * @param {Number} value - The value to format (0.1 = 10%)
 * @param {Number} decimals - Number of decimal places
 * @param {Boolean} includeSign - Whether to include + sign for positive values
 * @returns {String} Formatted percentage
 */
export const formatPercent = (value, decimals = 2, includeSign = false) => {
  if (typeof value !== 'number') {
    value = Number(value) || 0;
  }
  
  const sign = includeSign && value > 0 ? '+' : '';
  return `${sign}${(value * 100).toFixed(decimals)}%`;
};

/**
 * Format date to string
 * @param {Date|String} date - Date to format
 * @param {Boolean} includeTime - Whether to include time
 * @returns {String} Formatted date
 */
export const formatDate = (date, includeTime = false) => {
  if (!date) {
    return '';
  }
  
  const d = date instanceof Date ? date : new Date(date);
  
  if (isNaN(d.getTime())) {
    return '';
  }
  
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  
  if (!includeTime) {
    return `${year}-${month}-${day}`;
  }
  
  const hours = String(d.getHours()).padStart(2, '0');
  const minutes = String(d.getMinutes()).padStart(2, '0');
  const seconds = String(d.getSeconds()).padStart(2, '0');
  
  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
};

/**
 * Format time duration
 * @param {Number} seconds - Duration in seconds
 * @returns {String} Formatted duration
 */
export const formatDuration = (seconds) => {
  if (seconds < 60) {
    return `${Math.floor(seconds)}s`;
  } else if (seconds < 3600) {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes}m ${remainingSeconds}s`;
  } else {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${hours}h ${minutes}m`;
  }
};

/**
 * Parse and standardize stock code
 * @param {String} code - Raw stock code
 * @returns {String} Standardized stock code
 */
export const parseStockCode = (code) => {
  if (!code) return null;
  
  // Trim whitespace
  code = code.trim();
  
  // Remove any non-alphanumeric characters except dot
  code = code.replace(/[^a-zA-Z0-9.]/g, '');
  
  // Handle common formats
  
  // Format for Chinese stocks (e.g. "600000" -> "sh600000", "000001" -> "sz000001")
  if (/^\d{6}$/.test(code)) {
    // Shanghai Stock Exchange
    if (code.startsWith('6')) {
      return `sh${code}`;
    }
    // Shenzhen Stock Exchange
    else if (code.startsWith('0') || code.startsWith('3')) {
      return `sz${code}`;
    }
    // Others
    else {
      return code;
    }
  }
  
  // Already has market prefix
  if (/^(sh|sz|hk)\d+$/i.test(code)) {
    return code.toLowerCase();
  }
  
  // US stock
  if (/^[a-zA-Z]{1,5}(\.[a-zA-Z]{1,3})?$/.test(code)) {
    return code.toUpperCase();
  }
  
  // Hong Kong stock
  if (/^\d{5}$/.test(code)) {
    return `hk${code}`;
  }
  
  return code;
};

/**
 * Format stock code for display
 * @param {String} code - Standardized stock code
 * @returns {String} Formatted stock code
 */
export const formatStockCode = (code) => {
  if (!code) return '';
  
  // Remove market prefix for display
  if (code.startsWith('sh') || code.startsWith('sz')) {
    return code.substring(2);
  }
  
  if (code.startsWith('hk')) {
    return code.substring(2);
  }
  
  return code;
};

/**
 * Format file size
 * @param {Number} bytes - Size in bytes
 * @param {Number} decimals - Number of decimal places
 * @returns {String} Formatted file size
 */
export const formatFileSize = (bytes, decimals = 2) => {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
  
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`;
};

export default {
  formatMoney,
  formatLargeNumber,
  formatVolume,
  formatPercent,
  formatDate,
  formatDuration,
  parseStockCode,
  formatStockCode,
  formatFileSize
}; 
 
