<template>
  <view :class="['container', isDarkMode ? 'dark-theme' : 'light-theme']">
    <view class="header">
      <text class="title">交易中心</text>
    </view>
    
    <!-- 东吴秀才账户信息组件 -->
    <view class="account-section">
      <DongwuAccountInfo />
    </view>
    
    <!-- 券商连接组件 -->
    <view class="connection-section">
      <BrokerConnection @connection-change="handleConnectionChange" />
    </view>
    
    <!-- 交易内容区,只有在连接成功后显示 -->
    <view class="trading-content" v-if="isConnected">
      <view class="tab-bar">
        <view 
          class="tab-item" 
          :class="{ active: activeTab === 'positions' }" 
          @click="activeTab = 'positions'"
        >持仓</view>
        <view 
          class="tab-item" 
          :class="{ active: activeTab === 'orders' }" 
          @click="activeTab = 'orders'"
        >委托</view>
        <view 
          class="tab-item" 
          :class="{ active: activeTab === 'trades' }" 
          @click="activeTab = 'trades'"
        >交易记录</view>
        <view 
          class="tab-item" 
          :class="{ active: activeTab === 'fees' }" 
          @click="activeTab = 'fees'"
        >费用分析</view>
      </view>
      
      <!-- 持仓列表 -->
      <view v-show="activeTab === 'positions'">
        <PositionList 
          :isConnected="isConnected" 
          @order-submitted="handleOrderSubmitted" 
        />
      </view>
      
      <!-- 委托列表 -->
      <view v-show="activeTab === 'orders'">
        <OrderList 
          :isConnected="isConnected" 
          @order-cancelled="handleOrderCancelled" 
        />
      </view>
      
      <!-- 交易记录 -->
      <view v-show="activeTab === 'trades'">
        <TradeHistory />
      </view>
      
      <!-- 费用分析 -->
      <view v-show="activeTab === 'fees'">
        <TransactionFeeAnalyzer />
      </view>
    </view>
    
    <!-- 未连接时的提示 -->
    <view v-else class="not-connected-tip">
      <image class="tip-image" src="/static/images/connect.svg" mode="aspectFit"></image>
      <text class="tip-text">请先连接到交易账户</text>
    </view>
  </view>
</template>

<script>
import BrokerConnection from '@/components/trade/BrokerConnection.vue';
import PositionList from '@/components/trade/PositionList.vue';
import OrderList from '@/components/trade/OrderList.vue';
import DongwuAccountInfo from '@/components/DongwuAccountInfo.vue';
import TransactionFeeAnalyzer from '@/components/TransactionFeeAnalyzer.vue';
import TradeHistory from '@/components/trade/TradeHistory.vue';

export default {
  components: {
    BrokerConnection,
    PositionList,
    OrderList,
    DongwuAccountInfo,
    TransactionFeeAnalyzer,
    TradeHistory
  },
  data() {
    return {
      isDarkMode: false,
      isConnected: false,
      activeTab: 'positions',
      connectedBroker: null
    };
  },
  onLoad() {
    // 获取当前主题设置
    const app = getApp();
    this.isDarkMode = app.globalData.isDarkMode;
  },
  onShow() {
    // 每次显示页面时检查当前主题
    const app = getApp();
    this.isDarkMode = app.globalData.isDarkMode;
  },
  methods: {
    // 处理连接状态变更
    handleConnectionChange(data) {
      this.isConnected = data.connected;
      if (data.connected) {
        this.connectedBroker = data.broker;
        uni.showToast({
          title: '已连接到交易服务',
          icon: 'success'
        });
      } else {
        this.connectedBroker = null;
      }
    },
    
    // 处理订单提交
    handleOrderSubmitted(orderData) {
      // 订单提交后可能需要刷新委托列表
      if (this.$refs.orderList) {
        this.$refs.orderList.refresh();
      }
      
      // 切换到委托标签页查看最新订单
      this.activeTab = 'orders';
    },
    
    // 处理订单取消
    handleOrderCancelled(data) {
      // 订单取消后可能需要刷新持仓列表
      if (this.$refs.positionList) {
        this.$refs.positionList.refresh();
      }
    }
  }
};
</script>

<style lang="scss">
.container {
  min-height: 100vh;
  padding: 20rpx;
}

.header {
  padding: 20rpx 0;
  margin-bottom: 20rpx;
}

.title {
  font-size: 38rpx;
  font-weight: bold;
}

.account-section {
  margin-bottom: 20rpx;
}

.connection-section {
  margin-bottom: 20rpx;
}

.tab-bar {
  display: flex;
  background: #fff;
  border-radius: 12rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.1);
  overflow: hidden;
  
  .tab-item {
    flex: 1;
    text-align: center;
    padding: 24rpx 0;
    font-size: 30rpx;
    color: #606266;
    position: relative;
    
    &.active {
      color: #409eff;
      font-weight: bold;
      
      &::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 25%;
        width: 50%;
        height: 4rpx;
        background: #409eff;
        border-radius: 2rpx;
      }
    }
  }
}

.not-connected-tip {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 100rpx 0;
  
  .tip-image {
    width: 200rpx;
    height: 200rpx;
    margin-bottom: 30rpx;
    opacity: 0.5;
  }
  
  .tip-text {
    font-size: 30rpx;
    color: #909399;
  }
}

/* 深色主题样式 */
.dark-theme {
  background-color: #141414;
  
  .title {
    color: #ffffff;
  }
  
  .tab-bar {
    background: #222222;
    box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.3);
    
    .tab-item {
      color: #909399;
      
      &.active {
        color: #409eff;
      }
    }
  }
  
  .not-connected-tip {
    .tip-text {
      color: #909399;
    }
  }
}
</style> 
