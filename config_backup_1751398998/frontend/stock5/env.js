/**
 * Environment Configuration File
 * Used to manage configuration for different environments
 */

// Environment types
const ENV_TYPE = {
  DEV: 'development',
  PROD: 'production'
};

// Current environment
const currentEnv = process.env.NODE_ENV || ENV_TYPE.DEV;

// Base configuration
const baseConfig = {
  // Version number
  version: '1.0.0',
  
  // Cache expiration time (milliseconds)
  cacheExpiration: 5 * 60 * 1000, // 5 minutes
  
  // WebSocket heartbeat interval (milliseconds)
  wsHeartbeatInterval: 30000, // 30 seconds
  
  // Request timeout (milliseconds)
  requestTimeout: 30000, // 30 seconds
};

// Get the device IP address dynamically if possible, fallback to localhost
let localIpAddress = 'localhost';
try {
  // This is a dummy check. In real implementation, we'd use platform-specific methods
  // to get the actual IP address of the device.
  const networkInterfaces = uni.getSystemInfoSync().networkInterfaces;
  if (networkInterfaces && networkInterfaces.length > 0) {
    // Find a non-localhost IP address that's suitable for connections
    for (const iface of networkInterfaces) {
      if (iface.family === 'IPv4' && !iface.address.startsWith('127.')) {
        localIpAddress = iface.address;
        break;
      }
    }
  }
} catch (e) {
  console.log('Unable to detect local IP address, using localhost');
}

// Environment-specific configurations
const envConfigs = {
  // Development environment
  [ENV_TYPE.DEV]: {
    // API base URL - use domain for external access
    apiBaseUrl: 'https://api.aigupiao.me',

    // WebSocket address
    wsUrl: 'wss://api.aigupiao.me/ws',
    
    // Enable debugging
    debug: true,
    
    // Use mock data
    useMockData: true,
    
    // Default theme
    defaultTheme: 'light',
    
    // Log level
    logLevel: 'debug'
  },
  
  // Production environment
  [ENV_TYPE.PROD]: {
    // API base URL
    apiBaseUrl: 'https://1caf-39-188-128-188.ngrok-free.app',

    // WebSocket address
    wsUrl: 'wss://1caf-39-188-128-188.ngrok-free.app/ws',
    
    // Disable debugging
    debug: false,
    
    // Disable mock data
    useMockData: false,
    
    // Default theme
    defaultTheme: 'light',
    
    // Log level
    logLevel: 'error'
  }
};

// Export current environment configuration
export default {
  ...baseConfig,
  ...envConfigs[currentEnv],
  
  // Export environment type constants
  ENV_TYPE,
  
  // Current environment
  currentEnv,
  
  // Check if development environment
  isDev: currentEnv === ENV_TYPE.DEV,
  
  // Check if production environment
  isProd: currentEnv === ENV_TYPE.PROD,
  
  // Get current environment
  get current() {
    // Determine environment based on build type
    const isDev = process.env.NODE_ENV === 'development';
    return isDev ? envConfigs[ENV_TYPE.DEV] : envConfigs[ENV_TYPE.PROD];
  }
}; 
 
