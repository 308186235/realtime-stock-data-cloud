<template>
  <view class="account-info-container">
    <view class="account-info-header">
      <text class="account-title">东吴秀才账户信息</text>
      <view class="refresh-btn" @click="refreshAccountInfo">
        <text class="iconfont icon-refresh"></text>
      </view>
    </view>
    
    <view v-if="loading" class="loading-container">
      <uni-load-more status="loading" :iconSize="18" iconColor="#999"></uni-load-more>
    </view>
    
    <view v-else-if="error" class="error-container">
      <text class="error-text">{{ error }}</text>
      <button class="retry-btn" size="mini" type="default" @click="refreshAccountInfo">重试</button>
    </view>
    
    <view v-else-if="accountInfo" class="account-data">
      <view class="info-row">
        <view class="info-label">账户类型</view>
        <view class="info-value">{{ accountInfo.account_type || '东吴秀才' }}</view>
      </view>
      
      <view class="info-row">
        <view class="info-label">总资产</view>
        <view class="info-value amount">{{ formatAmount(accountInfo.total_assets) }}</view>
      </view>
      
      <view class="info-row">
        <view class="info-label">可用资金</view>
        <view class="info-value amount">{{ formatAmount(accountInfo.available) }}</view>
      </view>
      
      <view class="info-row">
        <view class="info-label">持仓市值</view>
        <view class="info-value amount">{{ formatAmount(accountInfo.market_value) }}</view>
      </view>
      
      <view class="info-row">
        <view class="info-label">冻结资金</view>
        <view class="info-value amount">{{ formatAmount(accountInfo.frozen) }}</view>
      </view>
      
      <view class="info-note">
        <text class="note-text">数据来源: {{ accountInfo.data_source || '虚拟账户数据库' }}</text>
        <text class="update-time" v-if="lastUpdateTime">{{ lastUpdateTime }}</text>
      </view>
    </view>
  </view>
</template>

<script>
import tradingService from '../services/tradingService.js';
import uniLoadMore from '@dcloudio/uni-ui/lib/uni-load-more/uni-load-more.vue';

export default {
  name: 'DongwuAccountInfo',
  components: {
    uniLoadMore
  },
  data() {
    return {
      accountInfo: null,
      loading: true,
      error: null,
      lastUpdateTime: null
    };
  },
  created() {
    this.getAccountInfo();
  },
  methods: {
    async getAccountInfo() {
      this.loading = true;
      this.error = null;

      try {
        // 调用后端API获取真实的交易软件数据
        const response = await uni.request({
          url: `${this.getApiBaseUrl()}/api/agent-trading/fund`,
          method: 'GET'
        });

        if (response.statusCode === 200 && response.data.status === 'success') {
          const accountData = response.data.data;
          this.accountInfo = {
            account_type: '东吴秀才',
            total_assets: accountData.total_assets || 0,
            available: accountData.available_cash || 0,
            market_value: accountData.market_value || 0,
            frozen: accountData.frozen_amount || 0,
            data_source: '交易软件实时数据'
          };
          this.lastUpdateTime = this.formatUpdateTime();

          console.log('✅ 成功获取真实交易软件数据:', accountData);
        } else {
          // 如果API调用失败，使用备用数据
          console.warn('API调用失败，使用备用数据');
          this.accountInfo = {
            account_type: '东吴秀才',
            total_assets: 0,
            available: 0,
            market_value: 0,
            frozen: 0,
            data_source: '数据获取失败'
          };
          this.error = '无法获取实时数据';
        }
      } catch (error) {
        console.error('获取真实账户数据失败:', error);
        // 网络异常时的备用数据
        this.accountInfo = {
          account_type: '东吴秀才',
          total_assets: 0,
          available: 0,
          market_value: 0,
          frozen: 0,
          data_source: '网络异常'
        };
        this.error = '网络连接异常，请检查后端服务';
      } finally {
        this.loading = false;
      }
    },

    /**
     * 获取API基础URL
     */
    getApiBaseUrl() {
      // 优先使用本地服务器，如果不可用再使用远程服务器
      return 'http://localhost:8000';
    },
    
    refreshAccountInfo() {
      this.getAccountInfo();
    },
    
    formatAmount(amount) {
      if (amount === undefined || amount === null) return '0.00';
      return amount.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    },
    
    formatUpdateTime() {
      const now = new Date();
      const hours = now.getHours().toString().padStart(2, '0');
      const minutes = now.getMinutes().toString().padStart(2, '0');
      const seconds = now.getSeconds().toString().padStart(2, '0');
      return `更新时间: ${hours}:${minutes}:${seconds}`;
    },

    /**
     * 获取数据来源显示文本
     */
    getDataSourceDisplay(dataSource) {
      const sourceMap = {
        'trading_software': '交易软件',
        'trading_software_sync': '交易软件同步',
        'real': '真实交易',
        'manual_create': '手动创建',
        'default_create': '默认创建'
      };
      return sourceMap[dataSource] || '虚拟账户数据库';
    }
  }
};
</script>

<style lang="scss" scoped>
.account-info-container {
  background-color: #fff;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 1px 6px rgba(0, 0, 0, 0.1);
  margin: 10px;
}

.account-info-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  
  .account-title {
    font-size: 16px;
    font-weight: bold;
    color: #333;
  }
  
  .refresh-btn {
    padding: 5px;
    
    .iconfont {
      font-size: 18px;
      color: #666;
    }
  }
}

.loading-container {
  display: flex;
  justify-content: center;
  padding: 20px 0;
}

.error-container {
  padding: 15px 0;
  text-align: center;
  
  .error-text {
    color: #ff5252;
    margin-bottom: 10px;
    font-size: 14px;
  }
  
  .retry-btn {
    margin-top: 10px;
    font-size: 14px;
  }
}

.account-data {
  .info-row {
    display: flex;
    justify-content: space-between;
    margin-bottom: 12px;
    
    .info-label {
      color: #666;
      font-size: 14px;
    }
    
    .info-value {
      font-size: 14px;
      color: #333;
      font-weight: 500;
      
      &.amount {
        color: #1976d2;
      }
    }
  }
  
  .info-note {
    display: flex;
    justify-content: space-between;
    margin-top: 15px;
    border-top: 1px solid #eee;
    padding-top: 10px;
    
    .note-text {
      font-size: 12px;
      color: #999;
    }
    
    .update-time {
      font-size: 12px;
      color: #999;
    }
  }
}
</style> 
