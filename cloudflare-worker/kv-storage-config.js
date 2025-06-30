/**
 * Cloudflare Worker KV存储配置
 * 用于缓存实时股票数据，提高访问速度
 */

// KV命名空间配置
const KV_NAMESPACES = {
    STOCK_CACHE: 'STOCK_CACHE',           // 股票数据缓存
    MARKET_DATA: 'MARKET_DATA',           // 市场数据缓存
    USER_SESSIONS: 'USER_SESSIONS',       // 用户会话缓存
    API_RATE_LIMIT: 'API_RATE_LIMIT'      // API限流缓存
};

// 缓存配置
const CACHE_CONFIG = {
    // 股票数据缓存时间（秒）
    STOCK_DATA_TTL: 300,        // 5分钟
    MARKET_DATA_TTL: 600,       // 10分钟
    USER_SESSION_TTL: 3600,     // 1小时
    RATE_LIMIT_TTL: 60,         // 1分钟
    
    // 缓存键前缀
    PREFIXES: {
        STOCK: 'stock:',
        MARKET: 'market:',
        USER: 'user:',
        RATE: 'rate:'
    }
};

/**
 * KV存储管理类
 */
class KVStorageManager {
    constructor(env) {
        this.env = env;
        this.stockCache = env.STOCK_CACHE;
        this.marketData = env.MARKET_DATA;
        this.userSessions = env.USER_SESSIONS;
        this.apiRateLimit = env.API_RATE_LIMIT;
    }

    /**
     * 存储股票数据
     */
    async setStockData(stockCode, data, ttl = CACHE_CONFIG.STOCK_DATA_TTL) {
        const key = CACHE_CONFIG.PREFIXES.STOCK + stockCode;
        const value = JSON.stringify({
            data: data,
            timestamp: Date.now(),
            ttl: ttl
        });
        
        await this.stockCache.put(key, value, {
            expirationTtl: ttl
        });
    }

    /**
     * 获取股票数据
     */
    async getStockData(stockCode) {
        const key = CACHE_CONFIG.PREFIXES.STOCK + stockCode;
        const value = await this.stockCache.get(key);
        
        if (!value) {
            return null;
        }
        
        try {
            const parsed = JSON.parse(value);
            return parsed.data;
        } catch (error) {
            console.error('解析股票数据失败:', error);
            return null;
        }
    }

    /**
     * 批量存储股票数据
     */
    async setStockDataBatch(stockDataMap, ttl = CACHE_CONFIG.STOCK_DATA_TTL) {
        const promises = [];
        
        for (const [stockCode, data] of Object.entries(stockDataMap)) {
            promises.push(this.setStockData(stockCode, data, ttl));
        }
        
        await Promise.all(promises);
    }

    /**
     * 批量获取股票数据
     */
    async getStockDataBatch(stockCodes) {
        const promises = stockCodes.map(code => this.getStockData(code));
        const results = await Promise.all(promises);
        
        const stockDataMap = {};
        stockCodes.forEach((code, index) => {
            if (results[index]) {
                stockDataMap[code] = results[index];
            }
        });
        
        return stockDataMap;
    }

    /**
     * 存储市场数据
     */
    async setMarketData(market, data, ttl = CACHE_CONFIG.MARKET_DATA_TTL) {
        const key = CACHE_CONFIG.PREFIXES.MARKET + market;
        const value = JSON.stringify({
            data: data,
            timestamp: Date.now(),
            ttl: ttl
        });
        
        await this.marketData.put(key, value, {
            expirationTtl: ttl
        });
    }

    /**
     * 获取市场数据
     */
    async getMarketData(market) {
        const key = CACHE_CONFIG.PREFIXES.MARKET + market;
        const value = await this.marketData.get(key);
        
        if (!value) {
            return null;
        }
        
        try {
            const parsed = JSON.parse(value);
            return parsed.data;
        } catch (error) {
            console.error('解析市场数据失败:', error);
            return null;
        }
    }

    /**
     * 存储用户会话
     */
    async setUserSession(userId, sessionData, ttl = CACHE_CONFIG.USER_SESSION_TTL) {
        const key = CACHE_CONFIG.PREFIXES.USER + userId;
        const value = JSON.stringify({
            data: sessionData,
            timestamp: Date.now(),
            ttl: ttl
        });
        
        await this.userSessions.put(key, value, {
            expirationTtl: ttl
        });
    }

    /**
     * 获取用户会话
     */
    async getUserSession(userId) {
        const key = CACHE_CONFIG.PREFIXES.USER + userId;
        const value = await this.userSessions.get(key);
        
        if (!value) {
            return null;
        }
        
        try {
            const parsed = JSON.parse(value);
            return parsed.data;
        } catch (error) {
            console.error('解析用户会话失败:', error);
            return null;
        }
    }

    /**
     * API限流检查
     */
    async checkRateLimit(clientId, limit = 100, window = 60) {
        const key = CACHE_CONFIG.PREFIXES.RATE + clientId;
        const value = await this.apiRateLimit.get(key);
        
        let count = 1;
        if (value) {
            try {
                const parsed = JSON.parse(value);
                count = parsed.count + 1;
            } catch (error) {
                count = 1;
            }
        }
        
        // 更新计数
        await this.apiRateLimit.put(key, JSON.stringify({
            count: count,
            timestamp: Date.now()
        }), {
            expirationTtl: window
        });
        
        return count <= limit;
    }

    /**
     * 清理过期数据
     */
    async cleanup() {
        // KV会自动清理过期数据，这里可以添加额外的清理逻辑
        console.log('KV存储清理完成');
    }

    /**
     * 获取存储统计
     */
    async getStats() {
        // 由于KV限制，无法直接获取统计信息
        // 可以通过其他方式实现统计功能
        return {
            message: 'KV存储统计功能需要额外实现',
            timestamp: Date.now()
        };
    }
}

/**
 * 创建KV存储管理器
 */
function createKVManager(env) {
    return new KVStorageManager(env);
}

/**
 * 中间件：缓存响应
 */
async function cacheMiddleware(request, env, next) {
    const kvManager = createKVManager(env);
    const url = new URL(request.url);
    const cacheKey = url.pathname + url.search;
    
    // 尝试从缓存获取
    const cached = await kvManager.stockCache.get(cacheKey);
    if (cached) {
        return new Response(cached, {
            headers: {
                'Content-Type': 'application/json',
                'Cache-Control': 'public, max-age=300',
                'X-Cache': 'HIT'
            }
        });
    }
    
    // 执行请求
    const response = await next();
    
    // 缓存响应
    if (response.ok) {
        const responseText = await response.text();
        await kvManager.stockCache.put(cacheKey, responseText, {
            expirationTtl: 300
        });
        
        return new Response(responseText, {
            headers: {
                'Content-Type': 'application/json',
                'Cache-Control': 'public, max-age=300',
                'X-Cache': 'MISS'
            }
        });
    }
    
    return response;
}

/**
 * 中间件：API限流
 */
async function rateLimitMiddleware(request, env, next) {
    const kvManager = createKVManager(env);
    const clientId = request.headers.get('CF-Connecting-IP') || 'unknown';
    
    const allowed = await kvManager.checkRateLimit(clientId, 1000, 60); // 每分钟1000次
    
    if (!allowed) {
        return new Response(JSON.stringify({
            error: 'Rate limit exceeded',
            message: '请求频率过高，请稍后再试'
        }), {
            status: 429,
            headers: {
                'Content-Type': 'application/json',
                'Retry-After': '60'
            }
        });
    }
    
    return next();
}

// 导出配置和类
export {
    KV_NAMESPACES,
    CACHE_CONFIG,
    KVStorageManager,
    createKVManager,
    cacheMiddleware,
    rateLimitMiddleware
};
