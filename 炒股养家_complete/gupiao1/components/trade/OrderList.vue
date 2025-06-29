<template>
  <view class="order-list">
    <view class="order-header">
      <view class="section-title">委托列表</view>
      <view class="header-actions">
        <button size="mini" type="primary" @click="refresh" :loading="loading">刷新</button>
      </view>
    </view>
    
    <view class="tab-bar">
      <view 
        class="tab-item" 
        :class="{ active: activeTab === 'today' }" 
        @click="activeTab = 'today'"
      >当日委托</view>
      <view 
        class="tab-item" 
        :class="{ active: activeTab === 'history' }" 
        @click="activeTab = 'history'"
      >历史委托</view>
    </view>
    
    <view class="loading-box" v-if="loading">
      <uni-load-more status="loading" :contentText="loadingText"></uni-load-more>
    </view>
    
    <view class="error-box" v-else-if="error">
      <text class="error-text">{{ error }}</text>
      <button size="mini" type="primary" @click="refresh">重试</button>
    </view>
    
    <view class="empty-box" v-else-if="displayOrders.length === 0">
      <image class="empty-image" src="/static/images/empty.png" mode="widthFix"></image>
      <text class="empty-text">暂无委托记录</text>
    </view>
    
    <view class="order-table" v-else>
      <view class="order-item" v-for="(order, index) in displayOrders" :key="index">
        <view class="order-header">
          <view class="stock-info">
            <text class="stock-name">{{ order.name }}</text>
            <text class="stock-code">{{ order.symbol }}</text>
          </view>
          <view class="order-status" :class="getStatusClass(order.status)">
            {{ getStatusText(order.status) }}
          </view>
        </view>
        
        <view class="order-body">
          <view class="data-row">
            <view class="data-col">
              <text class="data-label">方向</text>
              <text class="data-value" :class="getDirectionClass(order.direction)">
                {{ getDirectionText(order.direction) }}
              </text>
            </view>
            <view class="data-col">
              <text class="data-label">价格</text>
              <text class="data-value">{{ formatMoney(order.price) }}</text>
            </view>
            <view class="data-col">
              <text class="data-label">数量</text>
              <text class="data-value">{{ order.volume }}</text>
            </view>
          </view>
          
          <view class="data-row">
            <view class="data-col">
              <text class="data-label">已成交</text>
              <text class="data-value">{{ order.traded_volume || 0 }}</text>
            </view>
            <view class="data-col">
              <text class="data-label">时间</text>
              <text class="data-value">{{ formatTime(order.submit_time) }}</text>
            </view>
            <view class="data-col">
              <button 
                size="mini" 
                type="warn" 
                @click="cancelOrder(order)" 
                v-if="canCancel(order.status)"
                :disabled="cancelling[order.order_id]"
              >
                {{ cancelling[order.order_id] ? '撤单中' : '撤单' }}
              </button>
            </view>
          </view>
          
          <view class="order-message" v-if="order.message">
            <text class="message-text">{{ order.message }}</text>
          </view>
        </view>
      </view>
    </view>
    
    <view class="load-more" v-if="hasMore && !loading && !error">
      <uni-load-more status="more" :contentText="loadingText" @clickLoadMore="loadMore"></uni-load-more>
    </view>
  </view>
</template>

<script>
import tradingService from '@/services/tradingService.js';
import uniLoadMore from '@dcloudio/uni-ui/lib/uni-load-more/uni-load-more.vue';

export default {
  name: 'OrderList',
  components: {
    uniLoadMore
  },
  props: {
    isConnected: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      activeTab: 'today',
      todayOrders: [],
      historyOrders: [],
      loading: false,
      error: null,
      refreshTimer: null,
      loadingText: {
        contentdown: '点击加载更多',
        contentrefresh: '加载中...',
        contentnomore: '没有更多数据了'
      },
      hasMore: false,
      page: 1,
      pageSize: 10,
      cancelling: {} // 记录正在撤单的委托ID
    };
  },
  computed: {
    today() {
      const now = new Date();
      return now.toISOString().split('T')[0]; // 获取今天的日期,格式为YYYY-MM-DD
    },
    displayOrders() {
      return this.activeTab === 'today' ? this.todayOrders : this.historyOrders;
    }
  },
  watch: {
    isConnected(newVal) {
      if (newVal) {
        this.refresh();
        this.startAutoRefresh();
      } else {
        this.stopAutoRefresh();
        this.todayOrders = [];
        this.historyOrders = [];
      }
    },
    activeTab() {
      this.refresh();
    }
  },
  mounted() {
    if (this.isConnected) {
      this.refresh();
      this.startAutoRefresh();
    }
  },
  beforeDestroy() {
    this.stopAutoRefresh();
  },
  methods: {
    async refresh() {
      if (!this.isConnected || this.loading) return;
      
      this.loading = true;
      this.error = null;
      this.page = 1;
      
      try {
        if (this.activeTab === 'today') {
          await this.fetchTodayOrders();
        } else {
          await this.fetchHistoryOrders();
        }
      } catch (error) {
        console.error('刷新委托列表异常:', error);
        this.error = error.message || '刷新委托列表异常';
      } finally {
        this.loading = false;
      }
    },
    
    async loadMore() {
      if (!this.isConnected || this.loading || !this.hasMore) return;
      
      this.loading = true;
      this.page += 1;
      
      try {
        if (this.activeTab === 'today') {
          await this.fetchTodayOrders(true);
        } else {
          await this.fetchHistoryOrders(true);
        }
      } catch (error) {
        console.error('加载更多委托异常:', error);
        this.page -= 1; // 加载失败,恢复页码
      } finally {
        this.loading = false;
      }
    },
    
    async fetchTodayOrders(append = false) {
      const params = {
        start_date: this.today,
        end_date: this.today
      };
      
      const result = await tradingService.getOrders(params);
      
      if (result && result.success) {
        const orders = result.data || [];
        
        if (append) {
          this.todayOrders = [...this.todayOrders, ...orders];
        } else {
          this.todayOrders = orders;
        }
        
        // 判断是否还有更多数据
        this.hasMore = orders.length >= this.pageSize;
      } else {
        this.error = result.message || '获取当日委托失败';
      }
    },
    
    async fetchHistoryOrders(append = false) {
      // 获取过去30天的委托记录
      const end = new Date();
      const start = new Date();
      start.setDate(start.getDate() - 30);
      
      const params = {
        start_date: start.toISOString().split('T')[0],
        end_date: end.toISOString().split('T')[0]
      };
      
      const result = await tradingService.getOrders(params);
      
      if (result && result.success) {
        const orders = result.data || [];
        
        if (append) {
          this.historyOrders = [...this.historyOrders, ...orders];
        } else {
          this.historyOrders = orders;
        }
        
        // 判断是否还有更多数据
        this.hasMore = orders.length >= this.pageSize;
      } else {
        this.error = result.message || '获取历史委托失败';
      }
    },
    
    startAutoRefresh() {
      this.stopAutoRefresh();
      // 只有在显示当日委托时才自动刷新
      if (this.activeTab === 'today') {
        this.refreshTimer = setInterval(() => {
          this.fetchTodayOrders();
        }, 10000); // 每10秒刷新一次
      }
    },
    
    stopAutoRefresh() {
      if (this.refreshTimer) {
        clearInterval(this.refreshTimer);
        this.refreshTimer = null;
      }
    },
    
    async cancelOrder(order) {
      if (!this.isConnected || this.cancelling[order.order_id]) return;
      
      // 设置撤单中状态
      this.$set(this.cancelling, order.order_id, true);
      
      try {
        const result = await tradingService.cancelOrder(order.order_id);
        
        if (result && result.success) {
          uni.showToast({
            title: '撤单请求已提交',
            icon: 'success'
          });
          
          // 通知父组件撤单状态变化
          this.$emit('order-cancelled', { orderId: order.order_id });
          
          // 立即刷新委托列表
          setTimeout(() => {
            this.fetchTodayOrders();
          }, 1000);
        } else {
          uni.showToast({
            title: result.message || '撤单失败',
            icon: 'none'
          });
        }
      } catch (error) {
        console.error('撤单异常:', error);
        uni.showToast({
          title: error.message || '撤单异常',
          icon: 'none'
        });
      } finally {
        // 清除撤单中状态
        this.$set(this.cancelling, order.order_id, false);
      }
    },
    
    canCancel(status) {
      // 判断订单是否可以撤单
      const cancelableStatus = ['SUBMITTED', 'PARTIAL', 'QUEUED', 'PENDING'];
      return cancelableStatus.includes(status);
    },
    
    getStatusText(status) {
      const statusMap = {
        'SUBMITTED': '已提交',
        'QUEUED': '排队中',
        'PARTIAL': '部分成交',
        'FILLED': '全部成交',
        'CANCELLED': '已撤单',
        'REJECTED': '已拒绝',
        'EXPIRED': '已过期',
        'PENDING': '待处理'
      };
      
      return statusMap[status] || status;
    },
    
    getStatusClass(status) {
      const classMap = {
        'SUBMITTED': 'status-submitted',
        'QUEUED': 'status-queued',
        'PARTIAL': 'status-partial',
        'FILLED': 'status-filled',
        'CANCELLED': 'status-cancelled',
        'REJECTED': 'status-rejected',
        'EXPIRED': 'status-expired',
        'PENDING': 'status-pending'
      };
      
      return classMap[status] || '';
    },
    
    getDirectionText(direction) {
      return direction === 'BUY' ? '买入' : '卖出';
    },
    
    getDirectionClass(direction) {
      return direction === 'BUY' ? 'direction-buy' : 'direction-sell';
    },
    
    formatMoney(value) {
      if (value === null || value === undefined) return '0.00';
      return Number(value).toFixed(2);
    },
    
    formatTime(timeStr) {
      if (!timeStr) return '';
      
      // 如果是ISO格式时间字符串,提取时间部分
      if (timeStr.includes('T')) {
        const date = new Date(timeStr);
        return date.toLocaleTimeString('zh-CN', { hour12: false });
      }
      
      return timeStr;
    }
  }
};
</script>

<style lang="scss">
.order-list {
  margin-top: 20rpx;
  
  .order-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20rpx;
    
    .section-title {
      font-size: 32rpx;
      font-weight: bold;
    }
  }
  
  .tab-bar {
    display: flex;
    margin-bottom: 20rpx;
    background: #fff;
    border-radius: 12rpx;
    overflow: hidden;
    box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.1);
    
    .tab-item {
      flex: 1;
      text-align: center;
      padding: 20rpx 0;
      font-size: 28rpx;
      color: #606266;
      position: relative;
      
      &.active {
        color: #409eff;
        font-weight: bold;
        
        &::after {
          content: '';
          position: absolute;
          bottom: 0;
          left: 50%;
          transform: translateX(-50%);
          width: 40%;
          height: 4rpx;
          background: #409eff;
          border-radius: 2rpx;
        }
      }
    }
  }
  
  .loading-box,
  .empty-box,
  .error-box {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 60rpx 0;
    background: #fff;
    border-radius: 12rpx;
    box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.1);
  }
  
  .empty-image {
    width: 200rpx;
    margin-bottom: 20rpx;
  }
  
  .empty-text,
  .error-text {
    color: #909399;
    font-size: 28rpx;
    margin-bottom: 20rpx;
  }
  
  .order-table {
    .order-item {
      background: #fff;
      border-radius: 12rpx;
      margin-bottom: 20rpx;
      overflow: hidden;
      box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.1);
      
      .order-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 20rpx;
        border-bottom: 1px solid #ebeef5;
        margin-bottom: 0;
        
        .stock-info {
          .stock-name {
            font-size: 30rpx;
            font-weight: bold;
          }
          
          .stock-code {
            font-size: 24rpx;
            color: #909399;
            margin-left: 10rpx;
          }
        }
        
        .order-status {
          font-size: 26rpx;
          padding: 4rpx 10rpx;
          border-radius: 6rpx;
          
          &.status-submitted {
            background: #e8f4ff;
            color: #409eff;
          }
          
          &.status-queued {
            background: #f0f9eb;
            color: #67c23a;
          }
          
          &.status-partial {
            background: #fdf6ec;
            color: #e6a23c;
          }
          
          &.status-filled {
            background: #f0f9eb;
            color: #67c23a;
          }
          
          &.status-cancelled {
            background: #f4f4f5;
            color: #909399;
          }
          
          &.status-rejected,
          &.status-expired {
            background: #fef0f0;
            color: #f56c6c;
          }
          
          &.status-pending {
            background: #e8f4ff;
            color: #409eff;
          }
        }
      }
      
      .order-body {
        padding: 20rpx;
        
        .data-row {
          display: flex;
          margin-bottom: 15rpx;
          
          &:last-child {
            margin-bottom: 0;
          }
        }
        
        .data-col {
          flex: 1;
          display: flex;
          flex-direction: column;
          
          .data-label {
            font-size: 24rpx;
            color: #909399;
            margin-bottom: 5rpx;
          }
          
          .data-value {
            font-size: 28rpx;
            font-weight: bold;
            
            &.direction-buy {
              color: #f56c6c;
            }
            
            &.direction-sell {
              color: #67c23a;
            }
          }
        }
        
        .order-message {
          margin-top: 15rpx;
          background: #f8f8f8;
          padding: 10rpx;
          border-radius: 6rpx;
          
          .message-text {
            font-size: 24rpx;
            color: #909399;
          }
        }
      }
    }
  }
  
  .load-more {
    margin-top: 20rpx;
    margin-bottom: 20rpx;
  }
}
</style> 
