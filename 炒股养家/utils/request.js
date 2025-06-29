/**
 * 网络请求工具
 * 封装uni.request,添加拦截器,统一处理请求和响应
 */

import env from '../env';

// 获取当前环境配置
const currentEnv = env.current;

// 服务器基础地址
const BASE_URL = currentEnv.apiBaseUrl;

// 请求超时时间 (毫秒)
const TIMEOUT = env.requestTimeout || 30000;

// 确保USE_MOCK_DATA在所有环境中都一致
const USE_MOCK_DATA = currentEnv.useMockData === true || currentEnv.useMockData === 'true';

// 是否开启调试日志
const DEBUG = currentEnv.logLevel === 'debug';

// 统一请求方法
const request = (options = {}) => {
  return new Promise((resolve, reject) => {
    // 如果启用了模拟数据,在有mock处理器的情况下直接返回模拟数据
    if (USE_MOCK_DATA && typeof window.mockResponse === 'function') {
      try {
        const mockData = window.mockResponse(options.url, options.method, options.data);
        if (mockData) {
          console.log('使用模拟数据', options.url);
          setTimeout(() => resolve(mockData), 300); // 模拟网络延迟
          return;
        }
      } catch (err) {
        console.error('模拟数据处理出错', err);
      }
    }
    
    // 请求拦截器
    const token = uni.getStorageSync('token') || '';
    
    // 组装请求选项
    const requestOptions = {
      url: options.url.startsWith('http') ? options.url : BASE_URL + options.url,
      data: options.data || {},
      method: options.method || 'GET',
      header: {
        'content-type': options.contentType || 'application/json',
        'Authorization': token ? `Bearer ${token}` : '',
        ...options.header
      },
      timeout: options.timeout || TIMEOUT
    };
    
    // 控制台输出请求信息(仅开发环境)
    if (DEBUG) {
      console.log(`🚀 ${requestOptions.method} ${requestOptions.url}`, options.data || {});
    }
    
    // 发起请求
    uni.request({
      ...requestOptions,
      success: (res) => {
        // 控制台输出响应信息(仅开发环境)
        if (DEBUG) {
          console.log(`📨 ${requestOptions.method} ${requestOptions.url}`, res.data);
        }
        
        // 响应拦截器
        if (res.statusCode >= 200 && res.statusCode < 300) {
          // 请求成功
          resolve(res.data);
        } else if (res.statusCode === 401) {
          // 未授权,跳转到登录
          uni.showToast({
            title: '请先登录',
            icon: 'none'
          });
          // 可以在这里添加重定向到登录页的逻辑
          setTimeout(() => {
            uni.navigateTo({
              url: '/pages/login/index'
            });
          }, 1500);
          reject(new Error('需要登录'));
        } else {
          // 其他错误
          const errMsg = res.data && res.data.message 
            ? res.data.message 
            : `请求失败 (${res.statusCode})`;
            
          uni.showToast({
            title: errMsg,
            icon: 'none'
          });
          reject(res);
        }
      },
      fail: (err) => {
        // 请求失败
        console.error('请求失败', err);
        const errMsg = err.errMsg && err.errMsg.includes('timeout') 
          ? '请求超时,请检查网络连接' 
          : '网络请求失败';
          
        uni.showToast({
          title: errMsg,
          icon: 'none'
        });
        reject(err);
      }
    });
  });
};

export default request; 
