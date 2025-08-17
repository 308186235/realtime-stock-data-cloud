# WebSocket客户端使用指南

本文档提供了如何在交易系统中使用增强版WebSocket客户端的说明和示例。

## 基本使用

### 导入WebSocket客户端

```javascript
import WebSocketClient, { EVENTS, MSG_TYPES } from '@/utils/websocket_client';
```

### 创建并连接WebSocket

```javascript
// 创建WebSocket客户端实例
const wsClient = new WebSocketClient({
  // 覆盖默认配置
  url: 'ws://api.example.com/ws', // 生产环境URL
  debug: process.env.NODE_ENV === 'development', // 仅在开发环境启用调试
  reconnectInterval: 3000, // 3秒重连
  heartbeatInterval: 15000 // 15秒心跳
});

// 连接到服务器
wsClient.connect()
  .then(() => {
    console.log('WebSocket连接成功');
  })
  .catch(error => {
    console.error('WebSocket连接失败:', error);
  });
```

### 在Vue组件中使用

```javascript
export default {
  data() {
    return {
      wsClient: null,
      stockData: {},
      connected: false
    };
  },
  
  created() {
    // 创建WebSocket客户端
    this.wsClient = new WebSocketClient();
    
    // 添加事件监听器
    this.wsClient.on(EVENTS.OPEN, this.handleOpen);
    this.wsClient.on(EVENTS.CLOSE, this.handleClose);
    this.wsClient.on(EVENTS.ERROR, this.handleError);
    this.wsClient.on(EVENTS.MESSAGE, this.handleMessage);
    
    // 连接到服务器
    this.wsClient.connect();
  },
  
  beforeDestroy() {
    // 断开连接
    if (this.wsClient) {
      this.wsClient.disconnect();
      this.wsClient = null;
    }
  },
  
  methods: {
    handleOpen() {
      this.connected = true;
      
      // 连接成功后订阅股票数据
      this.subscribeToStock('sh600000');
    },
    
    handleClose() {
      this.connected = false;
    },
    
    handleError(error) {
      console.error('WebSocket错误:', error);
      uni.showToast({
        title: '数据连接错误',
        icon: 'none'
      });
    },
    
    handleMessage(message) {
      // 处理不同类型的消息
      if (message.type === 'quote') {
        // 更新股票数据
        const stock = message.data;
        this.stockData[stock.code] = stock;
      }
    },
    
    subscribeToStock(code) {
      if (!this.connected) {
        return;
      }
      
      this.wsClient.subscribe('quote', { code });
    },
    
    unsubscribeFromStock(code) {
      if (!this.connected) {
        return;
      }
      
      this.wsClient.unsubscribe('quote');
    }
  }
};
```

## 高级用法

### 重连机制

WebSocket客户端内置了自动重连机制,当连接断开时会自动尝试重连。您也可以监听重连相关事件:

```javascript
// 监听重连尝试
wsClient.on(EVENTS.RECONNECT_ATTEMPT, attempt => {
  console.log(`正在尝试重连 (${attempt})...`);
});

// 监听重连成功
wsClient.on(EVENTS.RECONNECT, attempt => {
  console.log(`重连成功,用了 ${attempt} 次尝试`);
});
```

### 自定义消息处理

您可以发送自定义消息到服务器:

```javascript
// 发送自定义消息
wsClient.send({
  type: 'custom_action',
  data: {
    action: 'refresh',
    params: { timestamp: Date.now() }
  }
});
```

### 在交易组件中使用

以下是在交易组件中使用WebSocket客户端的完整示例:

```html
<template>
  <view class="trading-container">
    <!-- 连接状态指示器 -->
    <view class="connection-status" :class="{ connected }">
      {{ connected ? '已连接' : '未连接' }}
    </view>
    
    <!-- 股票行情展示 -->
    <view v-if="currentStock" class="stock-quote">
      <text class="stock-name">{{ currentStock.name }}</text>
      <text class="stock-price" :class="priceClass">
        {{ currentStock.price }} 
        <text class="change">{{ priceChangeText }}</text>
      </text>
    </view>
    
    <!-- 交易操作区 -->
    <view class="trading-actions">
      <button type="primary" @click="subscribe" :disabled="!connected">
        订阅行情
      </button>
      <button type="default" @click="unsubscribe" :disabled="!connected">
        取消订阅
      </button>
    </view>
  </view>
</template>

<script>
import WebSocketClient, { EVENTS } from '@/utils/websocket_client';

export default {
  data() {
    return {
      wsClient: null,
      connected: false,
      stockCode: 'sh600000',
      stockData: {}
    };
  },
  
  computed: {
    currentStock() {
      return this.stockData[this.stockCode];
    },
    
    priceClass() {
      if (!this.currentStock) return '';
      return this.currentStock.change > 0 ? 'price-up' : 
             this.currentStock.change < 0 ? 'price-down' : '';
    },
    
    priceChangeText() {
      if (!this.currentStock) return '';
      const sign = this.currentStock.change > 0 ? '+' : '';
      return `${sign}${this.currentStock.change} (${sign}${this.currentStock.change_percent}%)`;
    }
  },
  
  onLoad() {
    // 创建WebSocket客户端
    this.wsClient = new WebSocketClient({
      debug: true
    });
    
    // 添加事件监听器
    this.wsClient.on(EVENTS.OPEN, this.handleOpen);
    this.wsClient.on(EVENTS.CLOSE, this.handleClose);
    this.wsClient.on(EVENTS.ERROR, this.handleError);
    this.wsClient.on(EVENTS.MESSAGE, this.handleMessage);
    
    // 连接到服务器
    this.wsClient.connect();
  },
  
  onUnload() {
    // 断开连接
    if (this.wsClient) {
      this.wsClient.disconnect();
      this.wsClient = null;
    }
  },
  
  methods: {
    handleOpen() {
      this.connected = true;
      
      // 可以选择自动订阅
      // this.subscribe();
    },
    
    handleClose() {
      this.connected = false;
    },
    
    handleError(error) {
      console.error('WebSocket错误:', error);
      uni.showToast({
        title: '数据连接错误',
        icon: 'none'
      });
    },
    
    handleMessage(message) {
      console.log('收到消息:', message);
      
      if (message.type === 'quote') {
        // 更新股票数据
        const stock = message.data;
        this.$set(this.stockData, stock.code, stock);
      }
    },
    
    subscribe() {
      if (!this.connected) {
        uni.showToast({
          title: '未连接到服务器',
          icon: 'none'
        });
        return;
      }
      
      this.wsClient.subscribe('quote', { code: this.stockCode });
      uni.showToast({
        title: '已订阅行情',
        icon: 'success'
      });
    },
    
    unsubscribe() {
      if (!this.connected) return;
      
      this.wsClient.unsubscribe('quote');
      uni.showToast({
        title: '已取消订阅',
        icon: 'success'
      });
    }
  }
};
</script>

<style>
.connection-status {
  padding: 5px 10px;
  background-color: #ffcccc;
  border-radius: 4px;
  margin-bottom: 10px;
  text-align: center;
}

.connection-status.connected {
  background-color: #ccffcc;
}

.stock-quote {
  padding: 15px;
  background-color: #f8f8f8;
  border-radius: 4px;
  margin-bottom: 15px;
}

.stock-name {
  font-size: 16px;
  font-weight: bold;
  display: block;
  margin-bottom: 5px;
}

.stock-price {
  font-size: 24px;
  font-weight: bold;
}

.price-up {
  color: #f04048;
}

.price-down {
  color: #00a800;
}

.change {
  font-size: 14px;
  margin-left: 5px;
}

.trading-actions {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}
</style>
```

## 配置参数

WebSocket客户端支持以下配置参数:

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| url | string | ws://localhost:8000/ws | WebSocket服务器URL |
| reconnectInterval | number | 5000 | 重连间隔(毫秒) |
| reconnectAttempts | number | 10 | 最大重连次数 |
| heartbeatInterval | number | 30000 | 心跳间隔(毫秒) |
| debug | boolean | false | 是否启用调试日志 |

## 事件类型

WebSocket客户端支持以下事件:

| 事件 | 说明 |
|------|------|
| EVENTS.OPEN | 连接打开 |
| EVENTS.CLOSE | 连接关闭 |
| EVENTS.ERROR | 连接错误 |
| EVENTS.MESSAGE | 收到消息 |
| EVENTS.RECONNECT | 重连成功 |
| EVENTS.RECONNECT_ATTEMPT | 开始尝试重连 |
| EVENTS.SUBSCRIBE | 订阅频道 |
| EVENTS.UNSUBSCRIBE | 取消订阅 |

## 消息类型

WebSocket客户端支持以下消息类型:

| 类型 | 说明 |
|------|------|
| MSG_TYPES.PING | 心跳请求 |
| MSG_TYPES.PONG | 心跳响应 |
| MSG_TYPES.SUBSCRIBE | 订阅请求 |
| MSG_TYPES.UNSUBSCRIBE | 取消订阅请求 |
| MSG_TYPES.DATA | 数据消息 |
| MSG_TYPES.ERROR | 错误消息 |

## 注意事项

1. 在组件销毁时务必调用`disconnect()`方法断开连接,避免内存泄漏
2. 在生产环境中应禁用debug日志
3. 在网络不稳定的环境中,可以增加`reconnectAttempts`和调整`reconnectInterval`提高连接可靠性
4. 可以考虑将WebSocket客户端封装为Vuex模块,实现全局状态管理 
 
