<template>
  <view class="broker-connection">
    <view class="connection-status" :class="connectionStatus">
      <text class="status-icon">{{ connectedIcon }}</text>
      <text class="status-text">{{ statusText }}</text>
    </view>
    
    <uni-forms ref="form" :model="formData" validateTrigger="bind">
      <!-- 券商选择已删除 - 直接使用Agent智能交易 -->
      
      <uni-forms-item label="账号" name="account_id" v-if="!isConnected">
        <uni-easyinput 
          v-model="formData.account_id" 
          placeholder="请输入账号"
          :disabled="isConnecting || isConnected"
        />
      </uni-forms-item>
      
      <uni-forms-item label="密码" name="account_pwd" v-if="!isConnected">
        <uni-easyinput 
          v-model="formData.account_pwd" 
          type="password"
          placeholder="请输入密码"
          :disabled="isConnecting || isConnected"
        />
      </uni-forms-item>
      
      <uni-forms-item label="验证码" name="verification_code" v-if="!isConnected && formData.broker_type === 'THS_DONGWU'">
        <uni-easyinput 
          v-model="formData.verification_code" 
          placeholder="请输入验证码(如需要)"
          :disabled="isConnecting || isConnected"
        />
      </uni-forms-item>
      
      <view class="advanced-options" v-if="showAdvanced && !isConnected">
        <uni-forms-item label="服务器IP" name="server_ip">
          <uni-easyinput 
            v-model="formData.server_ip" 
            placeholder="请输入服务器IP"
            :disabled="isConnecting || isConnected"
          />
        </uni-forms-item>
        
        <uni-forms-item label="服务器端口" name="server_port">
          <uni-easyinput 
            v-model="formData.server_port" 
            placeholder="请输入服务器端口"
            :disabled="isConnecting || isConnected"
            type="number"
          />
        </uni-forms-item>
        
        <uni-forms-item label="同花顺路径" name="ths_path" v-if="formData.broker_type === 'THS_DONGWU'">
          <uni-easyinput 
            v-model="formData.ths_path" 
            placeholder="同花顺安装路径,例如:C:/同花顺"
            :disabled="isConnecting || isConnected"
          />
        </uni-forms-item>
      </view>
      
      <view class="action-row">
        <button 
          class="action-btn advanced-btn" 
          type="default" 
          size="mini"
          @click="toggleAdvanced"
          v-if="!isConnected"
        >
          {{ showAdvanced ? '隐藏高级选项' : '显示高级选项' }}
        </button>
        
        <button 
          class="action-btn" 
          :type="isConnected ? 'warn' : 'primary'" 
          size="mini"
          @click="handleConnection"
          :loading="isConnecting"
          :disabled="isConnecting"
        >
          {{ isConnected ? '断开连接' : '连接' }}
        </button>
      </view>
    </uni-forms>
    
    <view class="account-info" v-if="isConnected && accountInfo">
      <view class="section-title">账户信息</view>
      <view class="info-row">
        <text class="info-label">账户ID:</text>
        <text class="info-value">{{ accountInfo.account_id }}</text>
      </view>
      <view class="info-row">
        <text class="info-label">总资产:</text>
        <text class="info-value">{{ formatMoney(accountInfo.total_assets) }}</text>
      </view>
      <view class="info-row">
        <text class="info-label">可用:</text>
        <text class="info-value">{{ formatMoney(accountInfo.available) }}</text>
      </view>
      <view class="info-row">
        <text class="info-label">市值:</text>
        <text class="info-value">{{ formatMoney(accountInfo.market_value) }}</text>
      </view>
      <view class="info-row">
        <text class="info-label">冻结:</text>
        <text class="info-value">{{ formatMoney(accountInfo.frozen) }}</text>
      </view>
    </view>
  </view>
</template>

<script>
import tradingService from '@/services/tradingService.js';
import uniForms from '@dcloudio/uni-ui/lib/uni-forms/uni-forms.vue';
import uniFormsItem from '@dcloudio/uni-ui/lib/uni-forms-item/uni-forms-item.vue';
import uniDataSelect from '@dcloudio/uni-ui/lib/uni-data-select/uni-data-select.vue';
import uniEasyinput from '@dcloudio/uni-ui/lib/uni-easyinput/uni-easyinput.vue';

export default {
  name: 'BrokerConnection',
  components: {
    uniForms,
    uniFormsItem,
    uniDataSelect,
    uniEasyinput
  },
  data() {
    return {
      isConnected: false,
      isConnecting: false,
      connectionError: null,
      showAdvanced: false,
      accountInfo: null,
      formData: {
        account_id: '',
        account_pwd: '',
        verification_code: '',
        ths_path: ''
      }
    };
  },
  computed: {
    // 券商选择功能已删除
    connectionStatus() {
      if (this.isConnecting) return 'connecting';
      if (this.isConnected) return 'connected';
      if (this.connectionError) return 'error';
      return 'disconnected';
    },
    statusText() {
      if (this.isConnecting) return '连接中...';
      if (this.isConnected) return '已连接';
      if (this.connectionError) return `连接错误: ${this.connectionError}`;
      return '未连接';
    },
    connectedIcon() {
      if (this.isConnecting) return '🔄';
      if (this.isConnected) return '✅';
      if (this.connectionError) return '❌';
      return '⚠️';
    }
  },
  mounted() {
    // 券商列表功能已删除，无需初始化
  },
  methods: {
    // 券商列表功能已删除

    
    toggleAdvanced() {
      this.showAdvanced = !this.showAdvanced;
    },
    
    async handleConnection() {
      if (this.isConnected) {
        await this.disconnect();
      } else {
        await this.connect();
      }
    },
    
    async connect() {
      try {
        this.isConnecting = true;
        this.connectionError = null;
        
        const params = {};
        for (const [key, value] of Object.entries(this.formData)) {
          if (value !== null && value !== undefined && value !== '') {
            params[key] = value;
          }
        }
        
        const result = await tradingService.connect(params);
        
        if (result && result.success) {
          this.isConnected = true;
          uni.showToast({
            title: '连接成功',
            icon: 'success'
          });
          
          await this.fetchAccountInfo();
          
          this.$emit('connection-change', { connected: true, broker: this.formData.broker_type });
        } else {
          this.connectionError = result.message || '未知错误';
          uni.showToast({
            title: `连接失败: ${this.connectionError}`,
            icon: 'none'
          });
        }
      } catch (error) {
        console.error('连接异常:', error);
        this.connectionError = error.message || '未知异常';
        uni.showToast({
          title: `连接异常: ${this.connectionError}`,
          icon: 'none'
        });
      } finally {
        this.isConnecting = false;
      }
    },
    
    async disconnect() {
      try {
        this.isConnecting = true;
        
        const result = await tradingService.disconnect();
        
        if (result && result.success) {
          this.isConnected = false;
          this.accountInfo = null;
          uni.showToast({
            title: '已断开连接',
            icon: 'success'
          });
          
          this.$emit('connection-change', { connected: false });
        } else {
          uni.showToast({
            title: '断开连接失败',
            icon: 'none'
          });
        }
      } catch (error) {
        console.error('断开连接异常:', error);
        uni.showToast({
          title: '断开连接异常',
          icon: 'none'
        });
      } finally {
        this.isConnecting = false;
      }
    },
    
    async fetchAccountInfo() {
      try {
        // 调用后端API获取真实的交易软件数据
        const response = await uni.request({
          url: `${this.getApiBaseUrl()}/api/agent-trading/fund`,
          method: 'GET'
        });

        if (response.statusCode === 200 && response.data.status === 'success') {
          const accountData = response.data.data;
          this.accountInfo = {
            account_id: '东吴秀才',
            total_assets: accountData.total_assets || 0,
            available: accountData.available_cash || 0,
            market_value: accountData.market_value || 0,
            frozen: accountData.frozen_amount || 0
          };

          console.log('✅ 成功获取真实交易软件数据:', accountData);
        } else {
          console.warn('API调用失败，无法获取实时数据');
          this.accountInfo = {
            account_id: '东吴秀才',
            total_assets: 0,
            available: 0,
            market_value: 0,
            frozen: 0
          };
        }
      } catch (error) {
        console.error('获取真实账户数据异常:', error);
        this.accountInfo = {
          account_id: '东吴秀才',
          total_assets: 0,
          available: 0,
          market_value: 0,
          frozen: 0
        };
      }
    },

    /**
     * 获取API基础URL
     */
    getApiBaseUrl() {
      // 根据环境返回不同的API地址
      if (process.env.NODE_ENV === 'development') {
        return 'http://localhost:8000';
      } else {
        return 'https://aigupiao.me';
      }
    },
    
    formatMoney(value) {
      if (value === null || value === undefined) return '0.00';
      return Number(value).toFixed(2);
    }
  }
};
</script>

<style lang="scss">
.broker-connection {
  padding: 20rpx;
  background-color: #fff;
  border-radius: 12rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.1);
  
  .connection-status {
    margin-bottom: 20rpx;
    padding: 20rpx;
    border-radius: 8rpx;
    display: flex;
    align-items: center;
    
    &.connected {
      background-color: #e1f3d8;
      color: #67c23a;
    }
    
    &.connecting {
      background-color: #e8f4ff;
      color: #409eff;
    }
    
    &.disconnected {
      background-color: #f4f4f5;
      color: #909399;
    }
    
    &.error {
      background-color: #fef0f0;
      color: #f56c6c;
    }
    
    .status-icon {
      margin-right: 10rpx;
      font-size: 40rpx;
    }
    
    .status-text {
      font-size: 28rpx;
    }
  }
  
  .action-row {
    display: flex;
    justify-content: flex-end;
    margin-top: 30rpx;
    margin-bottom: 20rpx;
    
    .action-btn {
      margin-left: 20rpx;
    }
    
    .advanced-btn {
      margin-right: auto;
    }
  }
  
  .account-info {
    margin-top: 30rpx;
    padding: 20rpx;
    border-top: 1px solid #ebeef5;
    
    .section-title {
      font-size: 30rpx;
      font-weight: bold;
      margin-bottom: 20rpx;
    }
    
    .info-row {
      display: flex;
      padding: 10rpx 0;
      
      .info-label {
        width: 180rpx;
        color: #606266;
      }
      
      .info-value {
        flex: 1;
        font-weight: bold;
      }
    }
  }
}
</style> 
