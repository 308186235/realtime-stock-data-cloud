/**
 * 移动端服务
 * 集成各种移动端特性和工具
 */

import gestureService from './gestureService.js';
import pushService from './pushService.js';

class MobileService {
  constructor() {
    // 设备信息
    this.deviceInfo = {};
    
    // 网络状态
    this.networkStatus = {
      isConnected: true,
      networkType: 'unknown'
    };
    
    // 应用状态
    this.appState = {
      isActive: true,
      isBackground: false
    };
    
    // 屏幕信息
    this.screenInfo = {};
    
    this.init();
  }
  
  /**
   * 初始化移动端服务
   */
  async init() {
    try {
      // 获取设备信息
      await this.getDeviceInfo();
      
      // 获取屏幕信息
      this.getScreenInfo();
      
      // 监听网络状态
      this.setupNetworkListener();
      
      // 监听应用状态
      this.setupAppStateListener();
      
      // 设置手势服务
      this.setupGestureService();
      
      // 设置状态栏
      this.setupStatusBar();
      
      console.log('移动端服务初始化完成');
    } catch (error) {
      console.error('移动端服务初始化失败:', error);
    }
  }
  
  /**
   * 获取设备信息
   */
  async getDeviceInfo() {
    return new Promise((resolve) => {
      uni.getSystemInfo({
        success: (res) => {
          this.deviceInfo = {
            platform: res.platform,
            system: res.system,
            version: res.version,
            model: res.model,
            brand: res.brand,
            screenWidth: res.screenWidth,
            screenHeight: res.screenHeight,
            windowWidth: res.windowWidth,
            windowHeight: res.windowHeight,
            statusBarHeight: res.statusBarHeight,
            safeArea: res.safeArea,
            safeAreaInsets: res.safeAreaInsets
          };
          resolve(this.deviceInfo);
        },
        fail: () => {
          resolve({});
        }
      });
    });
  }
  
  /**
   * 获取屏幕信息
   */
  getScreenInfo() {
    const systemInfo = uni.getSystemInfoSync();
    this.screenInfo = {
      screenWidth: systemInfo.screenWidth,
      screenHeight: systemInfo.screenHeight,
      windowWidth: systemInfo.windowWidth,
      windowHeight: systemInfo.windowHeight,
      pixelRatio: systemInfo.pixelRatio,
      statusBarHeight: systemInfo.statusBarHeight
    };
  }
  
  /**
   * 设置网络监听
   */
  setupNetworkListener() {
    // 监听网络状态变化
    uni.onNetworkStatusChange((res) => {
      this.networkStatus = {
        isConnected: res.isConnected,
        networkType: res.networkType
      };
      
      // 触发网络状态变化事件
      this.onNetworkChange(this.networkStatus);
    });
    
    // 获取初始网络状态
    uni.getNetworkType({
      success: (res) => {
        this.networkStatus = {
          isConnected: res.networkType !== 'none',
          networkType: res.networkType
        };
      }
    });
  }
  
  /**
   * 设置应用状态监听
   */
  setupAppStateListener() {
    // 监听应用进入前台
    uni.onAppShow(() => {
      this.appState.isActive = true;
      this.appState.isBackground = false;
      this.onAppShow();
    });
    
    // 监听应用进入后台
    uni.onAppHide(() => {
      this.appState.isActive = false;
      this.appState.isBackground = true;
      this.onAppHide();
    });
  }
  
  /**
   * 设置手势服务
   */
  setupGestureService() {
    // 设置快捷手势
    gestureService.setupQuickGestures();
  }
  
  /**
   * 设置状态栏
   */
  setupStatusBar() {
    // #ifdef APP-PLUS
    // 设置状态栏样式
    plus.navigator.setStatusBarStyle('dark');
    
    // 设置状态栏背景色
    plus.navigator.setStatusBarBackground('#141414');
    // #endif
  }
  
  /**
   * 网络状态变化回调
   */
  onNetworkChange(status) {
    console.log('网络状态变化:', status);
    
    if (!status.isConnected) {
      uni.showToast({
        title: '网络连接已断开',
        icon: 'none'
      });
    } else {
      uni.showToast({
        title: '网络连接已恢复',
        icon: 'success',
        duration: 1500
      });
    }
  }
  
  /**
   * 应用进入前台回调
   */
  onAppShow() {
    console.log('应用进入前台');
    
    // 刷新数据
    const pages = getCurrentPages();
    const currentPage = pages[pages.length - 1];
    if (currentPage && currentPage.$vm && currentPage.$vm.refreshData) {
      currentPage.$vm.refreshData();
    }
  }
  
  /**
   * 应用进入后台回调
   */
  onAppHide() {
    console.log('应用进入后台');
  }
  
  /**
   * 震动反馈
   */
  vibrate(type = 'short') {
    // #ifdef APP-PLUS
    if (type === 'long') {
      uni.vibrateLong();
    } else {
      uni.vibrateShort();
    }
    // #endif
  }
  
  /**
   * 保持屏幕常亮
   */
  keepScreenOn(keep = true) {
    uni.setKeepScreenOn({
      keepScreenOn: keep
    });
  }
  
  /**
   * 设置屏幕亮度
   */
  setScreenBrightness(value) {
    uni.setScreenBrightness({
      value: value // 0-1之间的数值
    });
  }
  
  /**
   * 获取屏幕亮度
   */
  getScreenBrightness() {
    return new Promise((resolve) => {
      uni.getScreenBrightness({
        success: (res) => {
          resolve(res.value);
        },
        fail: () => {
          resolve(0.5);
        }
      });
    });
  }
  
  /**
   * 复制到剪贴板
   */
  copyToClipboard(text) {
    return new Promise((resolve) => {
      uni.setClipboardData({
        data: text,
        success: () => {
          uni.showToast({
            title: '已复制到剪贴板',
            icon: 'success'
          });
          resolve(true);
        },
        fail: () => {
          uni.showToast({
            title: '复制失败',
            icon: 'none'
          });
          resolve(false);
        }
      });
    });
  }
  
  /**
   * 从剪贴板读取
   */
  getClipboardData() {
    return new Promise((resolve) => {
      uni.getClipboardData({
        success: (res) => {
          resolve(res.data);
        },
        fail: () => {
          resolve('');
        }
      });
    });
  }
  
  /**
   * 分享内容
   */
  share(options) {
    // #ifdef APP-PLUS
    uni.share({
      provider: options.provider || 'weixin',
      scene: options.scene || 'WXSceneSession',
      type: options.type || 0,
      title: options.title || '',
      summary: options.summary || '',
      href: options.href || '',
      imageUrl: options.imageUrl || '',
      success: () => {
        uni.showToast({
          title: '分享成功',
          icon: 'success'
        });
      },
      fail: (err) => {
        uni.showToast({
          title: '分享失败',
          icon: 'none'
        });
      }
    });
    // #endif
  }
  
  /**
   * 获取设备信息
   */
  getDeviceInfo() {
    return this.deviceInfo;
  }
  
  /**
   * 获取网络状态
   */
  getNetworkStatus() {
    return this.networkStatus;
  }
  
  /**
   * 获取应用状态
   */
  getAppState() {
    return this.appState;
  }
  
  /**
   * 获取屏幕信息
   */
  getScreenInfo() {
    return this.screenInfo;
  }
  
  /**
   * 检查是否为刘海屏
   */
  hasNotch() {
    return this.deviceInfo.safeAreaInsets && 
           this.deviceInfo.safeAreaInsets.top > this.deviceInfo.statusBarHeight;
  }
  
  /**
   * 获取安全区域
   */
  getSafeArea() {
    return this.deviceInfo.safeArea || {
      left: 0,
      right: this.screenInfo.screenWidth,
      top: this.deviceInfo.statusBarHeight || 0,
      bottom: this.screenInfo.screenHeight,
      width: this.screenInfo.screenWidth,
      height: this.screenInfo.screenHeight - (this.deviceInfo.statusBarHeight || 0)
    };
  }
}

// 创建单例实例
const mobileService = new MobileService();

export default mobileService;
