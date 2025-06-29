/**
 * 手势操作服务
 * 提供移动端手势识别和操作功能
 */

class GestureService {
  constructor() {
    // 手势配置
    this.config = {
      // 滑动阈值
      swipeThreshold: 50,
      // 滑动速度阈值
      swipeVelocity: 0.3,
      // 长按时间阈值
      longPressDelay: 500,
      // 双击时间间隔
      doubleTapDelay: 300
    };
    
    // 手势状态
    this.gestureState = {
      startX: 0,
      startY: 0,
      startTime: 0,
      lastTapTime: 0,
      isLongPress: false,
      longPressTimer: null
    };
    
    // 手势回调
    this.callbacks = {
      swipeLeft: [],
      swipeRight: [],
      swipeUp: [],
      swipeDown: [],
      longPress: [],
      doubleTap: [],
      tap: []
    };
  }
  
  /**
   * 注册手势回调
   */
  on(gesture, callback) {
    if (this.callbacks[gesture]) {
      this.callbacks[gesture].push(callback);
    }
  }
  
  /**
   * 移除手势回调
   */
  off(gesture, callback) {
    if (this.callbacks[gesture]) {
      const index = this.callbacks[gesture].indexOf(callback);
      if (index > -1) {
        this.callbacks[gesture].splice(index, 1);
      }
    }
  }
  
  /**
   * 触发手势回调
   */
  trigger(gesture, data = {}) {
    if (this.callbacks[gesture]) {
      this.callbacks[gesture].forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error('手势回调执行失败:', error);
        }
      });
    }
  }
  
  /**
   * 处理触摸开始
   */
  handleTouchStart(event) {
    const touch = event.touches[0];
    this.gestureState.startX = touch.clientX;
    this.gestureState.startY = touch.clientY;
    this.gestureState.startTime = Date.now();
    this.gestureState.isLongPress = false;
    
    // 设置长按定时器
    this.gestureState.longPressTimer = setTimeout(() => {
      this.gestureState.isLongPress = true;
      this.trigger('longPress', {
        x: this.gestureState.startX,
        y: this.gestureState.startY
      });
    }, this.config.longPressDelay);
  }
  
  /**
   * 处理触摸移动
   */
  handleTouchMove(event) {
    // 如果有移动，取消长按
    if (this.gestureState.longPressTimer) {
      clearTimeout(this.gestureState.longPressTimer);
      this.gestureState.longPressTimer = null;
    }
  }
  
  /**
   * 处理触摸结束
   */
  handleTouchEnd(event) {
    // 清除长按定时器
    if (this.gestureState.longPressTimer) {
      clearTimeout(this.gestureState.longPressTimer);
      this.gestureState.longPressTimer = null;
    }
    
    // 如果是长按，不处理其他手势
    if (this.gestureState.isLongPress) {
      return;
    }
    
    const touch = event.changedTouches[0];
    const endX = touch.clientX;
    const endY = touch.clientY;
    const endTime = Date.now();
    
    const deltaX = endX - this.gestureState.startX;
    const deltaY = endY - this.gestureState.startY;
    const deltaTime = endTime - this.gestureState.startTime;
    
    const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY);
    const velocity = distance / deltaTime;
    
    // 判断是否为滑动手势
    if (distance > this.config.swipeThreshold && velocity > this.config.swipeVelocity) {
      this.handleSwipe(deltaX, deltaY, velocity);
    } else {
      // 判断是否为点击手势
      this.handleTap(endX, endY, endTime);
    }
  }
  
  /**
   * 处理滑动手势
   */
  handleSwipe(deltaX, deltaY, velocity) {
    const absDeltaX = Math.abs(deltaX);
    const absDeltaY = Math.abs(deltaY);
    
    const swipeData = {
      deltaX,
      deltaY,
      velocity,
      direction: null
    };
    
    if (absDeltaX > absDeltaY) {
      // 水平滑动
      if (deltaX > 0) {
        swipeData.direction = 'right';
        this.trigger('swipeRight', swipeData);
      } else {
        swipeData.direction = 'left';
        this.trigger('swipeLeft', swipeData);
      }
    } else {
      // 垂直滑动
      if (deltaY > 0) {
        swipeData.direction = 'down';
        this.trigger('swipeDown', swipeData);
      } else {
        swipeData.direction = 'up';
        this.trigger('swipeUp', swipeData);
      }
    }
  }
  
  /**
   * 处理点击手势
   */
  handleTap(x, y, time) {
    const tapData = { x, y, time };
    
    // 检查是否为双击
    if (time - this.gestureState.lastTapTime < this.config.doubleTapDelay) {
      this.trigger('doubleTap', tapData);
    } else {
      // 延迟触发单击，以便检测双击
      setTimeout(() => {
        if (time === this.gestureState.lastTapTime) {
          this.trigger('tap', tapData);
        }
      }, this.config.doubleTapDelay);
    }
    
    this.gestureState.lastTapTime = time;
  }
  
  /**
   * 绑定到DOM元素
   */
  bindToElement(element) {
    if (!element) return;
    
    element.addEventListener('touchstart', this.handleTouchStart.bind(this), { passive: false });
    element.addEventListener('touchmove', this.handleTouchMove.bind(this), { passive: false });
    element.addEventListener('touchend', this.handleTouchEnd.bind(this), { passive: false });
  }
  
  /**
   * 从DOM元素解绑
   */
  unbindFromElement(element) {
    if (!element) return;
    
    element.removeEventListener('touchstart', this.handleTouchStart.bind(this));
    element.removeEventListener('touchmove', this.handleTouchMove.bind(this));
    element.removeEventListener('touchend', this.handleTouchEnd.bind(this));
  }
  
  /**
   * 设置手势配置
   */
  setConfig(config) {
    this.config = { ...this.config, ...config };
  }
  
  /**
   * 获取手势配置
   */
  getConfig() {
    return { ...this.config };
  }
  
  /**
   * 清除所有回调
   */
  clearCallbacks() {
    Object.keys(this.callbacks).forEach(gesture => {
      this.callbacks[gesture] = [];
    });
  }
  
  /**
   * 获取支持的手势列表
   */
  getSupportedGestures() {
    return Object.keys(this.callbacks);
  }
}

// 创建单例实例
const gestureService = new GestureService();

export default gestureService;
