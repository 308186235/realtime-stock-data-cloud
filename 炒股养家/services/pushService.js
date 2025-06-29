/**
 * 推送通知服务
 * 处理移动端推送通知功能
 */

class PushService {
  constructor() {
    // 推送配置
    this.config = {
      enabled: true,
      sound: true,
      vibrate: true,
      badge: true
    };
    
    // 通知类型
    this.notificationTypes = {
      TRADE_ALERT: 'trade_alert',        // 交易提醒
      PRICE_ALERT: 'price_alert',        // 价格提醒
      SYSTEM_ALERT: 'system_alert',      // 系统提醒
      MARKET_NEWS: 'market_news',        // 市场资讯
      AI_DECISION: 'ai_decision'         // AI决策通知
    };
    
    // 通知队列
    this.notificationQueue = [];
    
    // 权限状态
    this.permissionGranted = false;
    
    this.init();
  }
  
  /**
   * 初始化推送服务
   */
  async init() {
    try {
      // 检查推送权限
      await this.checkPermission();
      
      // 加载用户设置
      this.loadSettings();
      
      // 设置推送监听
      this.setupPushListeners();
      
      console.log('推送服务初始化完成');
    } catch (error) {
      console.error('推送服务初始化失败:', error);
    }
  }
  
  /**
   * 检查推送权限
   */
  async checkPermission() {
    return new Promise((resolve) => {
      // #ifdef APP-PLUS
      try {
        const main = plus.android.runtimeMainActivity();
        const pkgName = main.getPackageName();
        const uid = main.getApplicationInfo().uid;
        const NotificationManagerCompat = plus.android.importClass("android.support.v4.app.NotificationManagerCompat");

        if (NotificationManagerCompat && NotificationManagerCompat.from(main).areNotificationsEnabled()) {
          this.permissionGranted = true;
          resolve(true);
        } else {
          this.requestPermission().then(resolve);
        }
      } catch (error) {
        console.error('检查推送权限失败:', error);
        resolve(false);
      }
      // #endif
      
      // #ifdef H5
      if ('Notification' in window) {
        if (Notification.permission === 'granted') {
          this.permissionGranted = true;
          resolve(true);
        } else if (Notification.permission !== 'denied') {
          this.requestPermission().then(resolve);
        } else {
          resolve(false);
        }
      } else {
        resolve(false);
      }
      // #endif
      
      // #ifdef MP
      resolve(false); // 小程序不支持推送通知
      // #endif
    });
  }
  
  /**
   * 请求推送权限
   */
  async requestPermission() {
    return new Promise((resolve) => {
      // #ifdef APP-PLUS
      uni.showModal({
        title: '开启通知权限',
        content: '为了及时接收交易提醒和市场资讯，请开启通知权限',
        confirmText: '去设置',
        success: (res) => {
          if (res.confirm) {
            const main = plus.android.runtimeMainActivity();
            const Intent = plus.android.importClass("android.content.Intent");
            const Settings = plus.android.importClass("android.provider.Settings");
            const intent = new Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS);
            const Uri = plus.android.importClass("android.net.Uri");
            intent.setData(Uri.parse("package:" + main.getPackageName()));
            main.startActivity(intent);
          }
          resolve(false);
        }
      });
      // #endif
      
      // #ifdef H5
      if ('Notification' in window) {
        Notification.requestPermission().then((permission) => {
          this.permissionGranted = permission === 'granted';
          resolve(this.permissionGranted);
        });
      } else {
        resolve(false);
      }
      // #endif
    });
  }
  
  /**
   * 加载用户设置
   */
  loadSettings() {
    try {
      const settings = uni.getStorageSync('push_settings');
      if (settings) {
        this.config = { ...this.config, ...settings };
      }
    } catch (error) {
      console.error('加载推送设置失败:', error);
    }
  }
  
  /**
   * 保存用户设置
   */
  saveSettings() {
    try {
      uni.setStorageSync('push_settings', this.config);
    } catch (error) {
      console.error('保存推送设置失败:', error);
    }
  }
  
  /**
   * 设置推送监听
   */
  setupPushListeners() {
    // #ifdef APP-PLUS
    // 监听推送点击事件
    plus.push.addEventListener('click', (message) => {
      this.handlePushClick(message);
    });
    
    // 监听推送接收事件
    plus.push.addEventListener('receive', (message) => {
      this.handlePushReceive(message);
    });
    // #endif
  }
  
  /**
   * 处理推送点击
   */
  handlePushClick(message) {
    console.log('推送点击:', message);
    
    // 根据推送类型跳转到相应页面
    if (message.payload && message.payload.type) {
      switch (message.payload.type) {
        case this.notificationTypes.TRADE_ALERT:
          uni.navigateTo({ url: '/pages/trade/index' });
          break;
        case this.notificationTypes.AI_DECISION:
          uni.navigateTo({ url: '/pages/ai-analysis/index' });
          break;
        case this.notificationTypes.PRICE_ALERT:
          uni.navigateTo({ url: '/pages/portfolio/index' });
          break;
        default:
          uni.switchTab({ url: '/pages/index/index' });
      }
    }
  }
  
  /**
   * 处理推送接收
   */
  handlePushReceive(message) {
    console.log('推送接收:', message);
    
    // 如果应用在前台，显示应用内通知
    if (message.aps && message.aps.alert) {
      uni.showToast({
        title: message.aps.alert,
        icon: 'none',
        duration: 3000
      });
    }
  }
  
  /**
   * 发送本地通知
   */
  sendLocalNotification(options) {
    if (!this.config.enabled || !this.permissionGranted) {
      return;
    }
    
    const notification = {
      id: Date.now(),
      title: options.title || '炒股养家',
      content: options.content || '',
      type: options.type || this.notificationTypes.SYSTEM_ALERT,
      when: options.when || Date.now(),
      sound: this.config.sound ? 'system' : 'none',
      vibrate: this.config.vibrate,
      ...options
    };
    
    // #ifdef APP-PLUS
    plus.push.createMessage(
      notification.content,
      JSON.stringify({ type: notification.type }),
      {
        title: notification.title,
        when: new Date(notification.when),
        sound: notification.sound,
        vibrate: notification.vibrate
      }
    );
    // #endif
    
    // #ifdef H5
    if ('Notification' in window && this.permissionGranted) {
      new Notification(notification.title, {
        body: notification.content,
        icon: '/static/app-logo.png',
        tag: notification.type,
        vibrate: notification.vibrate ? [200, 100, 200] : []
      });
    }
    // #endif
  }
  
  /**
   * 发送交易提醒
   */
  sendTradeAlert(message, stockCode = '') {
    this.sendLocalNotification({
      title: '交易提醒',
      content: message,
      type: this.notificationTypes.TRADE_ALERT,
      payload: { stockCode }
    });
  }
  
  /**
   * 发送价格提醒
   */
  sendPriceAlert(stockName, price, change) {
    this.sendLocalNotification({
      title: `${stockName} 价格提醒`,
      content: `当前价格: ¥${price} (${change > 0 ? '+' : ''}${change}%)`,
      type: this.notificationTypes.PRICE_ALERT
    });
  }
  
  /**
   * 发送AI决策通知
   */
  sendAIDecision(action, stockName, confidence) {
    this.sendLocalNotification({
      title: 'AI交易决策',
      content: `建议${action} ${stockName} (置信度: ${confidence}%)`,
      type: this.notificationTypes.AI_DECISION
    });
  }
  
  /**
   * 发送系统提醒
   */
  sendSystemAlert(message) {
    this.sendLocalNotification({
      title: '系统提醒',
      content: message,
      type: this.notificationTypes.SYSTEM_ALERT
    });
  }
  
  /**
   * 设置推送配置
   */
  setConfig(config) {
    this.config = { ...this.config, ...config };
    this.saveSettings();
  }
  
  /**
   * 获取推送配置
   */
  getConfig() {
    return { ...this.config };
  }
  
  /**
   * 启用推送
   */
  enable() {
    this.config.enabled = true;
    this.saveSettings();
  }
  
  /**
   * 禁用推送
   */
  disable() {
    this.config.enabled = false;
    this.saveSettings();
  }
  
  /**
   * 清除所有通知
   */
  clearAllNotifications() {
    // #ifdef APP-PLUS
    plus.push.clear();
    // #endif
  }
  
  /**
   * 获取推送状态
   */
  getStatus() {
    return {
      enabled: this.config.enabled,
      permissionGranted: this.permissionGranted,
      config: this.config
    };
  }
}

// 创建单例实例
const pushService = new PushService();

export default pushService;
