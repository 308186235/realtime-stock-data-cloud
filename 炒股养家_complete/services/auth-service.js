/**
 * 认证服务,提供登录,登出和令牌管理功能
 */

// 配置API基础URL
const API_BASE_URL = '/api/auth';

// 存储令牌的本地存储键
const TOKEN_KEY = 'auth_token';
const USER_KEY = 'auth_user';

/**
 * 登录
 * @param {string} username 用户名
 * @param {string} password 密码
 * @returns {Promise} 登录结果
 */
export async function login(username, password) {
    try {
        // 构建JSON数据匹配simple_api_server.py的格式
        const requestBody = {
            username,
            password
        };
        
        const response = await fetch(`${API_BASE_URL}/token`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || '登录失败');
        }
        
        // 获取登录结果
        const authData = await response.json();
        
        // 存储认证信息
        localStorage.setItem(TOKEN_KEY, authData.access_token);
        localStorage.setItem(USER_KEY, JSON.stringify({
            username: authData.username,
            expires_at: authData.expires_at
        }));
        
        return {
            username: authData.username,
            token: authData.access_token,
            expiresAt: new Date(authData.expires_at)
        };
    } catch (error) {
        console.error('登录失败:', error);
        throw error;
    }
}

/**
 * 登出
 */
export function logout() {
    // 清除认证信息
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    
    // 刷新页面或重定向到登录页
    window.location.href = '/login';
}

/**
 * 获取当前用户信息
 * @returns {Object|null} 用户信息
 */
export function getCurrentUser() {
    const userJson = localStorage.getItem(USER_KEY);
    if (!userJson) return null;
    
    try {
        const user = JSON.parse(userJson);
        
        // 检查令牌是否过期
        if (user.expires_at) {
            const expiresAt = new Date(user.expires_at);
            if (expiresAt < new Date()) {
                // 令牌已过期,清除信息
                logout();
                return null;
            }
        }
        
        return user;
    } catch (error) {
        console.error('解析用户信息失败:', error);
        return null;
    }
}

/**
 * 获取认证令牌
 * @returns {string|null} 认证令牌
 */
export function getAuthToken() {
    return localStorage.getItem(TOKEN_KEY);
}

/**
 * 检查用户是否已认证
 * @returns {boolean} 是否已认证
 */
export function isAuthenticated() {
    return getCurrentUser() !== null && getAuthToken() !== null;
}

/**
 * 刷新用户信息
 * @returns {Promise} 用户信息
 */
export async function refreshUserInfo() {
    try {
        const token = getAuthToken();
        if (!token) {
            throw new Error('未登录');
        }
        
        const response = await fetch(`${API_BASE_URL}/me`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (!response.ok) {
            if (response.status === 401) {
                // 认证失败,清除信息
                logout();
            }
            throw new Error('获取用户信息失败');
        }
        
        const userData = await response.json();
        
        // 更新用户信息
        const currentUser = getCurrentUser();
        if (currentUser) {
            localStorage.setItem(USER_KEY, JSON.stringify({
                ...userData,
                expires_at: currentUser.expires_at
            }));
        }
        
        return userData;
    } catch (error) {
        console.error('刷新用户信息失败:', error);
        throw error;
    }
}

/**
 * 为API请求添加认证头
 * @param {Object} options 请求选项
 * @returns {Object} 添加认证头后的请求选项
 */
export function withAuth(options = {}) {
    const token = getAuthToken();
    if (!token) return options;
    
    const headers = {
        ...options.headers,
        'Authorization': `Bearer ${token}`
    };
    
    return {
        ...options,
        headers
    };
}

// CSRF令牌处理
export function getCSRFToken() {
    return document.cookie.replace(/(?:(?:^|.*;\s*)csrf_token\s*=\s*([^;]*).*$)|^.*$/, "$1");
}

// 添加CSRF令牌到请求头
export function withCSRF(options = {}) {
    const csrfToken = getCSRFToken();
    if (!csrfToken) return options;
    
    const headers = {
        ...options.headers,
        'X-CSRF-Token': csrfToken
    };
    
    return {
        ...options,
        headers
    };
}

// 完整的安全请求
export function secureRequest(options = {}) {
    return withCSRF(withAuth(options));
}

// 导出认证服务
export const authService = {
    login,
    logout,
    getCurrentUser,
    getAuthToken,
    isAuthenticated,
    refreshUserInfo,
    withAuth,
    getCSRFToken,
    withCSRF,
    secureRequest
}; 
