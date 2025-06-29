/**
 * 回测服务,提供与回测API的交互功能
 */

import { authService } from '../../services/auth-service.js';

// 配置API基础URL
const API_BASE_URL = '/api/backtesting';

/**
 * 执行回测
 * @param {Object} params 回测参数
 * @returns {Promise} 回测结果
 */
export async function runBacktest(params) {
    try {
        // 使用安全请求
        const options = authService.secureRequest({
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(params)
        });
        
        const response = await fetch(`${API_BASE_URL}/run`, options);
        
        if (!response.ok) {
            // 处理认证错误
            if (response.status === 401 || response.status === 403) {
                // 如果是认证问题,重定向到登录页
                authService.logout();
                throw new Error('请先登录');
            }
            
            const errorData = await response.json();
            throw new Error(errorData.detail || '回测执行失败');
        }
        
        return await response.json();
    } catch (error) {
        console.error('回测执行失败:', error);
        throw error;
    }
}

/**
 * 获取回测结果
 * @param {string} backtestId 回测ID
 * @returns {Promise} 回测结果
 */
export async function getBacktestResults(backtestId) {
    try {
        // 使用安全请求
        const options = authService.secureRequest();
        
        const response = await fetch(`${API_BASE_URL}/results/${backtestId}`, options);
        
        if (!response.ok) {
            if (response.status === 401 || response.status === 403) {
                authService.logout();
                throw new Error('请先登录');
            }
            
            const errorData = await response.json();
            throw new Error(errorData.detail || '获取回测结果失败');
        }
        
        return await response.json();
    } catch (error) {
        console.error('获取回测结果失败:', error);
        throw error;
    }
}

/**
 * 保存回测
 * @param {string} backtestId 回测ID
 * @param {string} name 回测名称
 * @returns {Promise} 保存结果
 */
export async function saveBacktest(backtestId, name) {
    try {
        // 使用安全请求
        const options = authService.secureRequest({
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                backtest_id: backtestId,
                name: name
            })
        });
        
        const response = await fetch(`${API_BASE_URL}/save`, options);
        
        if (!response.ok) {
            if (response.status === 401 || response.status === 403) {
                authService.logout();
                throw new Error('请先登录');
            }
            
            const errorData = await response.json();
            throw new Error(errorData.detail || '保存回测失败');
        }
        
        return await response.json();
    } catch (error) {
        console.error('保存回测失败:', error);
        throw error;
    }
}

/**
 * 获取回测历史
 * @returns {Promise} 回测历史
 */
export async function getBacktestHistory() {
    try {
        // 使用安全请求
        const options = authService.secureRequest();
        
        const response = await fetch(`${API_BASE_URL}/history`, options);
        
        if (!response.ok) {
            if (response.status === 401 || response.status === 403) {
                authService.logout();
                throw new Error('请先登录');
            }
            
            const errorData = await response.json();
            throw new Error(errorData.detail || '获取回测历史失败');
        }
        
        return await response.json();
    } catch (error) {
        console.error('获取回测历史失败:', error);
        throw error;
    }
}

// 导出回测服务
export const backtestService = {
    runBacktest,
    getBacktestResults,
    saveBacktest,
    getBacktestHistory
}; 
