/**
 * API Key管理服务
 * 管理多个股票数据API Key，支持快速切换
 */

class ApiKeyManager {
  constructor() {
    this.currentKeyIndex = 0;
    this.apiKeys = [
      {
        id: 'primary',
        key: 'QT_wat5QfcJ6N9pDZM5',
        name: '主要API Key',
        status: 'active',
        lastUsed: null,
        errorCount: 0,
        maxErrors: 5
      }
    ];
    this.loadFromStorage();
  }

  /**
   * 添加新的API Key
   */
  addApiKey(keyData) {
    const newKey = {
      id: keyData.id || `key_${Date.now()}`,
      key: keyData.key,
      name: keyData.name || `API Key ${this.apiKeys.length + 1}`,
      status: 'inactive',
      lastUsed: null,
      errorCount: 0,
      maxErrors: keyData.maxErrors || 5,
      description: keyData.description || '',
      addedAt: new Date().toISOString()
    };

    this.apiKeys.push(newKey);
    this.saveToStorage();
    
    console.log('[API Key管理] 添加新API Key:', newKey.name);
    return newKey;
  }

  /**
   * 删除API Key
   */
  removeApiKey(keyId) {
    const index = this.apiKeys.findIndex(key => key.id === keyId);
    if (index > -1) {
      const removedKey = this.apiKeys.splice(index, 1)[0];
      
      // 如果删除的是当前使用的Key，切换到下一个
      if (this.currentKeyIndex >= this.apiKeys.length) {
        this.currentKeyIndex = 0;
      }
      
      this.saveToStorage();
      console.log('[API Key管理] 删除API Key:', removedKey.name);
      return true;
    }
    return false;
  }

  /**
   * 获取当前API Key
   */
  getCurrentApiKey() {
    if (this.apiKeys.length === 0) {
      return null;
    }
    
    const currentKey = this.apiKeys[this.currentKeyIndex];
    if (currentKey) {
      currentKey.lastUsed = new Date().toISOString();
      this.saveToStorage();
    }
    
    return currentKey;
  }

  /**
   * 切换到下一个API Key
   */
  switchToNextKey() {
    if (this.apiKeys.length <= 1) {
      console.warn('[API Key管理] 没有备用API Key可切换');
      return null;
    }

    // 标记当前Key为有问题
    const currentKey = this.apiKeys[this.currentKeyIndex];
    if (currentKey) {
      currentKey.status = 'error';
      currentKey.errorCount++;
    }

    // 切换到下一个可用的Key
    const startIndex = this.currentKeyIndex;
    do {
      this.currentKeyIndex = (this.currentKeyIndex + 1) % this.apiKeys.length;
      const nextKey = this.apiKeys[this.currentKeyIndex];
      
      if (nextKey && nextKey.status !== 'disabled' && nextKey.errorCount < nextKey.maxErrors) {
        nextKey.status = 'active';
        this.saveToStorage();
        
        console.log('[API Key管理] 切换到API Key:', nextKey.name);
        return nextKey;
      }
    } while (this.currentKeyIndex !== startIndex);

    console.error('[API Key管理] 没有可用的API Key');
    return null;
  }

  /**
   * 切换到指定API Key
   */
  switchToKey(keyId) {
    const index = this.apiKeys.findIndex(key => key.id === keyId);
    if (index > -1) {
      // 重置之前的Key状态
      if (this.apiKeys[this.currentKeyIndex]) {
        this.apiKeys[this.currentKeyIndex].status = 'inactive';
      }
      
      // 激活新Key
      this.currentKeyIndex = index;
      this.apiKeys[index].status = 'active';
      this.apiKeys[index].errorCount = 0; // 重置错误计数
      
      this.saveToStorage();
      console.log('[API Key管理] 手动切换到API Key:', this.apiKeys[index].name);
      return this.apiKeys[index];
    }
    return null;
  }

  /**
   * 报告API Key错误
   */
  reportError(keyId, error) {
    const key = this.apiKeys.find(k => k.id === keyId);
    if (key) {
      key.errorCount++;
      key.lastError = {
        message: error.message,
        timestamp: new Date().toISOString()
      };

      // 如果错误次数超过限制，禁用该Key
      if (key.errorCount >= key.maxErrors) {
        key.status = 'disabled';
        console.warn(`[API Key管理] API Key ${key.name} 错误次数过多，已禁用`);
        
        // 自动切换到下一个Key
        if (key.id === this.getCurrentApiKey()?.id) {
          this.switchToNextKey();
        }
      }

      this.saveToStorage();
    }
  }

  /**
   * 重置API Key状态
   */
  resetKeyStatus(keyId) {
    const key = this.apiKeys.find(k => k.id === keyId);
    if (key) {
      key.errorCount = 0;
      key.status = 'inactive';
      key.lastError = null;
      this.saveToStorage();
      
      console.log('[API Key管理] 重置API Key状态:', key.name);
      return true;
    }
    return false;
  }

  /**
   * 获取所有API Key列表
   */
  getAllKeys() {
    return this.apiKeys.map(key => ({
      ...key,
      key: this.maskApiKey(key.key) // 隐藏部分Key内容
    }));
  }

  /**
   * 获取API Key统计信息
   */
  getStatistics() {
    const total = this.apiKeys.length;
    const active = this.apiKeys.filter(k => k.status === 'active').length;
    const disabled = this.apiKeys.filter(k => k.status === 'disabled').length;
    const error = this.apiKeys.filter(k => k.status === 'error').length;

    return {
      total,
      active,
      disabled,
      error,
      currentKey: this.getCurrentApiKey()?.name || 'None'
    };
  }

  /**
   * 测试API Key可用性
   */
  async testApiKey(keyId) {
    const key = this.apiKeys.find(k => k.id === keyId);
    if (!key) {
      return { success: false, error: 'API Key not found' };
    }

    try {
      // 这里可以添加实际的API测试逻辑
      console.log(`[API Key管理] 测试API Key: ${key.name}`);
      
      // 模拟测试结果
      const testResult = {
        success: true,
        responseTime: Math.random() * 1000 + 100,
        timestamp: new Date().toISOString()
      };

      key.lastTest = testResult;
      this.saveToStorage();

      return testResult;
    } catch (error) {
      const testResult = {
        success: false,
        error: error.message,
        timestamp: new Date().toISOString()
      };

      key.lastTest = testResult;
      this.reportError(keyId, error);

      return testResult;
    }
  }

  /**
   * 批量测试所有API Key
   */
  async testAllKeys() {
    const results = {};
    
    for (const key of this.apiKeys) {
      if (key.status !== 'disabled') {
        results[key.id] = await this.testApiKey(key.id);
      }
    }

    return results;
  }

  /**
   * 隐藏API Key部分内容
   */
  maskApiKey(key) {
    if (!key || key.length < 8) {
      return key;
    }
    return key.substring(0, 4) + '*'.repeat(key.length - 8) + key.substring(key.length - 4);
  }

  /**
   * 保存到本地存储
   */
  saveToStorage() {
    try {
      const data = {
        currentKeyIndex: this.currentKeyIndex,
        apiKeys: this.apiKeys,
        lastUpdated: new Date().toISOString()
      };
      
      uni.setStorageSync('apiKeyManager', JSON.stringify(data));
    } catch (error) {
      console.error('[API Key管理] 保存到存储失败:', error);
    }
  }

  /**
   * 从本地存储加载
   */
  loadFromStorage() {
    try {
      const data = uni.getStorageSync('apiKeyManager');
      if (data) {
        const parsed = JSON.parse(data);
        this.currentKeyIndex = parsed.currentKeyIndex || 0;
        
        // 合并存储的Keys和默认Keys
        if (parsed.apiKeys && parsed.apiKeys.length > 0) {
          this.apiKeys = parsed.apiKeys;
        }
        
        console.log('[API Key管理] 从存储加载配置');
      }
    } catch (error) {
      console.error('[API Key管理] 从存储加载失败:', error);
    }
  }

  /**
   * 导出配置
   */
  exportConfig() {
    return {
      version: '1.0',
      exportTime: new Date().toISOString(),
      apiKeys: this.apiKeys.map(key => ({
        ...key,
        key: this.maskApiKey(key.key) // 导出时隐藏完整Key
      }))
    };
  }

  /**
   * 导入配置
   */
  importConfig(config) {
    try {
      if (config.apiKeys && Array.isArray(config.apiKeys)) {
        // 验证导入的数据格式
        const validKeys = config.apiKeys.filter(key => 
          key.id && key.key && key.name
        );

        if (validKeys.length > 0) {
          this.apiKeys = [...this.apiKeys, ...validKeys];
          this.saveToStorage();
          
          console.log(`[API Key管理] 导入 ${validKeys.length} 个API Key`);
          return { success: true, imported: validKeys.length };
        }
      }
      
      return { success: false, error: 'Invalid config format' };
    } catch (error) {
      console.error('[API Key管理] 导入配置失败:', error);
      return { success: false, error: error.message };
    }
  }
}

// 创建单例实例
const apiKeyManager = new ApiKeyManager();

export default apiKeyManager;
