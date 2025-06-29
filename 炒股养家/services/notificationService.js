/**
 * 通知服务
 * 统一管理应用内通知、错误提示、成功消息等
 */

class NotificationService {
  constructor() {
    // 通知队列
    this.notificationQueue = [];
    
    // 通知配置
    this.config = {
      maxQueueSize: 10,
      defaultDuration: 2000,
      errorDuration: 3000,
      successDuration: 1500
    };
    
    // 通知类型
    this.types = {
      SUCCESS: 'success',
      ERROR: 'error',
      WARNING: 'warning',
      INFO: 'info',
      LOADING: 'loading'
    };
    
    // 当前显示的通知
    this.currentNotification = null;
  }
  
  /**
   * 显示成功消息
   */
  success(message, duration = this.config.successDuration) {
    return this.show({
      type: this.types.SUCCESS,
      message,
      duration,
      icon: 'success'
    });
  }
  
  /**
   * 显示错误消息
   */
  error(message, duration = this.config.errorDuration) {
    return this.show({
      type: this.types.ERROR,
      message,
      duration,
      icon: 'none'
    });
  }
  
  /**
   * 显示警告消息
   */
  warning(message, duration = this.config.defaultDuration) {
    return this.show({
      type: this.types.WARNING,
      message,
      duration,
      icon: 'none'
    });
  }
  
  /**
   * 显示信息消息
   */
  info(message, duration = this.config.defaultDuration) {
    return this.show({
      type: this.types.INFO,
      message,
      duration,
      icon: 'none'
    });
  }
  
  /**
   * 显示加载消息
   */
  loading(message = '加载中...') {
    return this.show({
      type: this.types.LOADING,
      message,
      duration: 0, // 不自动关闭
      icon: 'loading'
    });
  }
  
  /**
   * 显示通知
   */
  show(options) {
    const notification = {
      id: Date.now() + Math.random(),
      type: options.type || this.types.INFO,
      message: options.message || '',
      duration: options.duration || this.config.defaultDuration,
      icon: options.icon || 'none',
      timestamp: Date.now()
    };
    
    // 如果是加载类型，直接显示
    if (notification.type === this.types.LOADING) {
      this.currentNotification = notification;
      uni.showLoading({
        title: notification.message,
        mask: true
      });
      return notification;
    }
    
    // 添加到队列
    this.addToQueue(notification);
    
    // 如果当前没有显示通知，立即显示
    if (!this.currentNotification) {
      this.processQueue();
    }
    
    return notification;
  }
  
  /**
   * 添加到通知队列
   */
  addToQueue(notification) {
    // 限制队列大小
    if (this.notificationQueue.length >= this.config.maxQueueSize) {
      this.notificationQueue.shift(); // 移除最旧的通知
    }
    
    this.notificationQueue.push(notification);
  }
  
  /**
   * 处理通知队列
   */
  processQueue() {
    if (this.notificationQueue.length === 0) {
      return;
    }
    
    const notification = this.notificationQueue.shift();
    this.currentNotification = notification;
    
    // 显示通知
    uni.showToast({
      title: notification.message,
      icon: notification.icon,
      duration: notification.duration,
      mask: false
    });
    
    // 设置自动关闭
    if (notification.duration > 0) {
      setTimeout(() => {
        this.currentNotification = null;
        this.processQueue(); // 处理下一个通知
      }, notification.duration);
    }
  }
  
  /**
   * 隐藏当前通知
   */
  hide() {
    if (this.currentNotification) {
      if (this.currentNotification.type === this.types.LOADING) {
        uni.hideLoading();
      } else {
        uni.hideToast();
      }
      this.currentNotification = null;
      
      // 处理队列中的下一个通知
      setTimeout(() => {
        this.processQueue();
      }, 100);
    }
  }
  
  /**
   * 清空通知队列
   */
  clear() {
    this.notificationQueue = [];
    this.hide();
  }
  
  /**
   * 显示确认对话框
   */
  confirm(options) {
    return new Promise((resolve) => {
      uni.showModal({
        title: options.title || '确认',
        content: options.content || '',
        showCancel: options.showCancel !== false,
        cancelText: options.cancelText || '取消',
        confirmText: options.confirmText || '确定',
        success: (res) => {
          resolve(res.confirm);
        },
        fail: () => {
          resolve(false);
        }
      });
    });
  }
  
  /**
   * 显示操作菜单
   */
  showActionSheet(options) {
    return new Promise((resolve) => {
      uni.showActionSheet({
        itemList: options.itemList || [],
        success: (res) => {
          resolve({
            success: true,
            tapIndex: res.tapIndex,
            item: options.itemList[res.tapIndex]
          });
        },
        fail: () => {
          resolve({
            success: false,
            tapIndex: -1,
            item: null
          });
        }
      });
    });
  }
  
  /**
   * 处理API错误
   */
  handleApiError(error, context = '') {
    let message = '操作失败';
    
    if (error && error.message) {
      message = error.message;
    } else if (error && error.errMsg) {
      if (error.errMsg.includes('timeout')) {
        message = '请求超时，请检查网络连接';
      } else if (error.errMsg.includes('fail')) {
        message = '网络连接失败';
      } else {
        message = error.errMsg;
      }
    } else if (typeof error === 'string') {
      message = error;
    }
    
    // 添加上下文信息
    if (context) {
      message = `${context}: ${message}`;
    }
    
    console.error('API错误:', error);
    this.error(message);
  }
  
  /**
   * 处理网络错误
   */
  handleNetworkError(error) {
    let message = '网络连接失败';
    
    if (error && error.errMsg) {
      if (error.errMsg.includes('timeout')) {
        message = '网络请求超时';
      } else if (error.errMsg.includes('fail')) {
        message = '网络连接失败';
      }
    }
    
    this.error(message);
  }
  
  /**
   * 显示数据加载状态
   */
  showDataLoading(message = '加载数据中...') {
    return this.loading(message);
  }
  
  /**
   * 显示数据加载成功
   */
  showDataSuccess(message = '数据加载成功') {
    this.hide(); // 隐藏loading
    this.success(message);
  }
  
  /**
   * 显示数据加载失败
   */
  showDataError(error, context = '数据加载') {
    this.hide(); // 隐藏loading
    this.handleApiError(error, context);
  }
  
  /**
   * 获取通知统计
   */
  getStats() {
    return {
      queueLength: this.notificationQueue.length,
      currentNotification: this.currentNotification,
      hasActiveNotification: !!this.currentNotification
    };
  }
}

// 创建单例实例
const notificationService = new NotificationService();

export default notificationService;
