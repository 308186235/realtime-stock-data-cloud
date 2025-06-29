/**
 * WebSocket Utility
 * Handles real-time data connections and subscriptions
 */

import env from '../env';

// Current environment settings
const ENV = env.current;

// WebSocket configuration
const WS_BASE_URL = ENV.wsBaseUrl || ENV.apiBaseUrl.replace(/^http/, 'ws');
const RECONNECT_INTERVAL = 5000; // 5 seconds
const MAX_RECONNECT_ATTEMPTS = 10;
const PING_INTERVAL = 30000; // 30 seconds

// Message types
export const MSG_TYPES = {
  PING: 'ping',
  PONG: 'pong',
  AUTH: 'auth',
  SUBSCRIBE: 'subscribe',
  UNSUBSCRIBE: 'unsubscribe',
  QUOTE: 'quote',
  TRADE: 'trade',
  ERROR: 'error'
};

// Connection states
export const CONN_STATES = {
  CONNECTING: 0,
  OPEN: 1,
  CLOSING: 2,
  CLOSED: 3
};

// Event types
export const EVENTS = {
  OPEN: 'open',
  CLOSE: 'close',
  ERROR: 'error',
  MESSAGE: 'message',
  RECONNECT: 'reconnect',
  SUBSCRIBE: 'subscribe',
  UNSUBSCRIBE: 'unsubscribe'
};

export default class WebSocketClient {
  constructor(options = {}) {
    this.options = {
      url: options.url || `${WS_BASE_URL}/ws`,
      protocols: options.protocols || [],
      autoReconnect: options.autoReconnect !== false,
      autoAuth: options.autoAuth !== false,
      debug: options.debug || (ENV.logLevel === 'debug')
    };
    
    this.socket = null;
    this.reconnectAttempts = 0;
    this.reconnectTimer = null;
    this.pingTimer = null;
    this.eventListeners = {};
    this.subscriptions = new Set();
    this.isAuthenticated = false;
    this.isConnecting = false;
    
    // Bind methods to prevent 'this' issues
    this.connect = this.connect.bind(this);
    this.disconnect = this.disconnect.bind(this);
    this.reconnect = this.reconnect.bind(this);
    this.onMessage = this.onMessage.bind(this);
    this.onOpen = this.onOpen.bind(this);
    this.onClose = this.onClose.bind(this);
    this.onError = this.onError.bind(this);
  }
  
  /**
   * Connect to WebSocket server
   * @returns {Promise} Promise that resolves when connected
   */
  connect() {
    if (this.socket && (this.socket.readyState === CONN_STATES.OPEN || this.socket.readyState === CONN_STATES.CONNECTING)) {
      return Promise.resolve();
    }
    
    this.isConnecting = true;
    
    return new Promise((resolve, reject) => {
      try {
        this.log('Connecting to WebSocket:', this.options.url);
        
        // Create WebSocket connection
        this.socket = new WebSocket(this.options.url, this.options.protocols);
        
        // Set up event handlers
        this.socket.onopen = (event) => {
          this.onOpen(event);
          resolve();
        };
        
        this.socket.onclose = this.onClose;
        this.socket.onerror = (error) => {
          this.onError(error);
          if (this.isConnecting) {
            reject(error);
          }
        };
        
        this.socket.onmessage = this.onMessage;
      } catch (error) {
        this.log('Connection error:', error);
        this.isConnecting = false;
        reject(error);
      }
    });
  }
  
  /**
   * Disconnect from WebSocket server
   */
  disconnect() {
    this.clearReconnectTimer();
    this.clearPingTimer();
    
    if (this.socket) {
      this.socket.onopen = null;
      this.socket.onclose = null;
      this.socket.onerror = null;
      this.socket.onmessage = null;
      
      if (this.socket.readyState === CONN_STATES.OPEN || this.socket.readyState === CONN_STATES.CONNECTING) {
        this.socket.close();
      }
      
      this.socket = null;
    }
    
    this.isAuthenticated = false;
  }
  
  /**
   * Reconnect to WebSocket server
   */
  reconnect() {
    this.clearReconnectTimer();
    
    if (this.reconnectAttempts >= MAX_RECONNECT_ATTEMPTS) {
      this.log('Max reconnect attempts reached');
      this.emit(EVENTS.ERROR, new Error('Max reconnect attempts reached'));
      return;
    }
    
    this.reconnectAttempts++;
    this.log(`Reconnecting (attempt ${this.reconnectAttempts}/${MAX_RECONNECT_ATTEMPTS})...`);
    this.emit(EVENTS.RECONNECT, { attempt: this.reconnectAttempts });
    
    this.disconnect();
    this.connect()
      .then(() => {
        this.reconnectAttempts = 0;
        this.resubscribe();
      })
      .catch(() => {
        // Schedule next reconnect
        this.reconnectTimer = setTimeout(this.reconnect, RECONNECT_INTERVAL);
      });
  }
  
  /**
   * Handle WebSocket open event
   * @param {Event} event - WebSocket event
   */
  onOpen(event) {
    this.log('WebSocket connected');
    this.isConnecting = false;
    this.reconnectAttempts = 0;
    
    // Start ping timer
    this.startPingTimer();
    
    // Handle authentication if needed
    if (this.options.autoAuth) {
      this.authenticate();
    }
    
    // Emit open event
    this.emit(EVENTS.OPEN, event);
  }
  
  /**
   * Handle WebSocket close event
   * @param {Event} event - WebSocket event
   */
  onClose(event) {
    this.log('WebSocket disconnected:', event.code, event.reason);
    this.isConnecting = false;
    this.isAuthenticated = false;
    
    // Clear timers
    this.clearPingTimer();
    
    // Emit close event
    this.emit(EVENTS.CLOSE, event);
    
    // Reconnect if enabled
    if (this.options.autoReconnect && event.code !== 1000) {
      this.reconnectTimer = setTimeout(this.reconnect, RECONNECT_INTERVAL);
    }
  }
  
  /**
   * Handle WebSocket error event
   * @param {Event} error - WebSocket error
   */
  onError(error) {
    this.log('WebSocket error:', error);
    this.isConnecting = false;
    
    // Emit error event
    this.emit(EVENTS.ERROR, error);
  }
  
  /**
   * Handle WebSocket message event
   * @param {MessageEvent} event - WebSocket message event
   */
  onMessage(event) {
    try {
      const message = JSON.parse(event.data);
      
      // Process message based on type
      switch (message.type) {
        case MSG_TYPES.PONG:
          // Ping response, do nothing
          break;
          
        case MSG_TYPES.AUTH:
          this.handleAuthResponse(message);
          break;
          
        case MSG_TYPES.QUOTE:
        case MSG_TYPES.TRADE:
          // Process market data
          this.emit(message.type, message.data);
          break;
          
        case MSG_TYPES.ERROR:
          this.log('Server error:', message.error);
          this.emit(EVENTS.ERROR, new Error(message.error));
          break;
          
        default:
          // For all other message types, emit an event with the message type
          this.emit(message.type, message);
      }
      
      // Also emit a generic message event
      this.emit(EVENTS.MESSAGE, message);
    } catch (error) {
      this.log('Error parsing message:', error, event.data);
    }
  }
  
  /**
   * Send message to WebSocket server
   * @param {Object} message - Message to send
   * @returns {Boolean} Success status
   */
  send(message) {
    if (!this.socket || this.socket.readyState !== CONN_STATES.OPEN) {
      this.log('Cannot send message, socket not open');
      return false;
    }
    
    try {
      const data = typeof message === 'string' ? message : JSON.stringify(message);
      this.socket.send(data);
      return true;
    } catch (error) {
      this.log('Error sending message:', error);
      return false;
    }
  }
  
  /**
   * Send ping to keep connection alive
   */
  sendPing() {
    this.send({
      type: MSG_TYPES.PING,
      timestamp: Date.now()
    });
  }
  
  /**
   * Start ping timer
   */
  startPingTimer() {
    this.clearPingTimer();
    this.pingTimer = setInterval(() => this.sendPing(), PING_INTERVAL);
  }
  
  /**
   * Clear ping timer
   */
  clearPingTimer() {
    if (this.pingTimer) {
      clearInterval(this.pingTimer);
      this.pingTimer = null;
    }
  }
  
  /**
   * Clear reconnect timer
   */
  clearReconnectTimer() {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
  }
  
  /**
   * Authenticate with WebSocket server
   */
  authenticate() {
    const token = uni.getStorageSync('token');
    
    if (!token) {
      this.log('No authentication token available');
      return;
    }
    
    this.send({
      type: MSG_TYPES.AUTH,
      token
    });
  }
  
  /**
   * Handle authentication response
   * @param {Object} response - Authentication response
   */
  handleAuthResponse(response) {
    if (response.success) {
      this.log('Authentication successful');
      this.isAuthenticated = true;
      
      // Resubscribe to previous subscriptions
      this.resubscribe();
    } else {
      this.log('Authentication failed:', response.error);
      this.isAuthenticated = false;
      
      // Emit error event
      this.emit(EVENTS.ERROR, new Error(response.error || 'Authentication failed'));
    }
  }
  
  /**
   * Subscribe to a data channel
   * @param {String} channel - Channel to subscribe to
   * @param {Object} params - Additional parameters
   * @returns {Boolean} Success status
   */
  subscribe(channel, params = {}) {
    const subscriptionKey = this.getSubscriptionKey(channel, params);
    
    // Add to subscriptions list
    this.subscriptions.add(subscriptionKey);
    
    // Only send if connected
    if (this.socket && this.socket.readyState === CONN_STATES.OPEN) {
      const success = this.send({
        type: MSG_TYPES.SUBSCRIBE,
        channel,
        params
      });
      
      if (success) {
        this.emit(EVENTS.SUBSCRIBE, { channel, params });
      }
      
      return success;
    }
    
    return false;
  }
  
  /**
   * Unsubscribe from a data channel
   * @param {String} channel - Channel to unsubscribe from
   * @param {Object} params - Additional parameters
   * @returns {Boolean} Success status
   */
  unsubscribe(channel, params = {}) {
    const subscriptionKey = this.getSubscriptionKey(channel, params);
    
    // Remove from subscriptions list
    this.subscriptions.delete(subscriptionKey);
    
    // Only send if connected
    if (this.socket && this.socket.readyState === CONN_STATES.OPEN) {
      const success = this.send({
        type: MSG_TYPES.UNSUBSCRIBE,
        channel,
        params
      });
      
      if (success) {
        this.emit(EVENTS.UNSUBSCRIBE, { channel, params });
      }
      
      return success;
    }
    
    return false;
  }
  
  /**
   * Resubscribe to all previous subscriptions
   */
  resubscribe() {
    if (this.subscriptions.size === 0) {
      return;
    }
    
    this.log(`Resubscribing to ${this.subscriptions.size} channels`);
    
    for (const key of this.subscriptions) {
      const { channel, params } = this.parseSubscriptionKey(key);
      
      this.send({
        type: MSG_TYPES.SUBSCRIBE,
        channel,
        params
      });
    }
  }
  
  /**
   * Get subscription key
   * @param {String} channel - Channel
   * @param {Object} params - Parameters
   * @returns {String} Subscription key
   */
  getSubscriptionKey(channel, params) {
    return `${channel}:${JSON.stringify(params || {})}`;
  }
  
  /**
   * Parse subscription key
   * @param {String} key - Subscription key
   * @returns {Object} Parsed key with channel and params
   */
  parseSubscriptionKey(key) {
    const [channel, paramsJson] = key.split(':');
    try {
      const params = JSON.parse(paramsJson || '{}');
      return { channel, params };
    } catch (error) {
      return { channel, params: {} };
    }
  }
  
  /**
   * Add event listener
   * @param {String} event - Event type
   * @param {Function} callback - Event callback
   */
  on(event, callback) {
    if (!this.eventListeners[event]) {
      this.eventListeners[event] = [];
    }
    
    this.eventListeners[event].push(callback);
  }
  
  /**
   * Remove event listener
   * @param {String} event - Event type
   * @param {Function} callback - Event callback
   */
  off(event, callback) {
    if (!this.eventListeners[event]) {
      return;
    }
    
    if (callback) {
      this.eventListeners[event] = this.eventListeners[event].filter(cb => cb !== callback);
    } else {
      this.eventListeners[event] = [];
    }
  }
  
  /**
   * Emit event
   * @param {String} event - Event type
   * @param {*} data - Event data
   */
  emit(event, data) {
    if (!this.eventListeners[event]) {
      return;
    }
    
    for (const callback of this.eventListeners[event]) {
      try {
        callback(data);
      } catch (error) {
        console.error('Error in event listener:', error);
      }
    }
  }
  
  /**
   * Log message if debug is enabled
   */
  log(...args) {
    if (this.options.debug) {
      console.log('[WebSocket]', ...args);
    }
  }
  
  /**
   * Get connection state
   * @returns {Number} Connection state
   */
  get state() {
    return this.socket ? this.socket.readyState : CONN_STATES.CLOSED;
  }
  
  /**
   * Check if connected
   * @returns {Boolean} Connected status
   */
  get connected() {
    return this.socket && this.socket.readyState === CONN_STATES.OPEN;
  }
  
  /**
   * Get connection state name
   * @returns {String} Connection state name
   */
  get stateName() {
    switch (this.state) {
      case CONN_STATES.CONNECTING: return 'CONNECTING';
      case CONN_STATES.OPEN: return 'OPEN';
      case CONN_STATES.CLOSING: return 'CLOSING';
      case CONN_STATES.CLOSED: return 'CLOSED';
      default: return 'UNKNOWN';
    }
  }
} 
 
