<template>
  <view class="settings-popup">
    <view class="settings-header">
      <text class="settings-title">Agent智能交易设置</text>
      <text class="close-btn" @click="close">×</text>
    </view>
    
    <view class="settings-body">
      <view class="settings-form">
        <view class="form-item">
          <text class="item-label">策略选择</text>
          <view class="strategy-options">
            <view 
              v-for="(strategy, index) in strategies" 
              :key="index"
              class="strategy-option"
              :class="{ active: selectedStrategy === strategy.id }"
              @click="selectStrategy(strategy.id)"
            >
              <text class="strategy-name">{{ strategy.name }}</text>
              <text class="strategy-desc">{{ strategy.description }}</text>
            </view>
          </view>
        </view>
        
        <view class="form-item">
          <text class="item-label">最大持仓数量</text>
          <view class="slider-container">
            <slider 
              :value="maxPositions" 
              :min="1" 
              :max="10" 
              :step="1" 
              show-value 
              @change="onMaxPositionsChange"
              activeColor="#1989fa"
            />
          </view>
        </view>
        
        <view class="form-item">
          <text class="item-label">AI自动执行</text>
          <view class="auto-execute-container">
            <view class="auto-execute-toggle">
              <text class="setting-label">启用AI自动执行交易</text>
              <switch 
                :checked="autoExecute" 
                @change="onAutoExecuteChange"
                color="#1989fa"
                style="transform: scale(0.8);"
              />
            </view>
            <text class="auto-execute-desc">启用后,AI将自动执行交易决策,无需人工确认</text>
            
            <view class="auto-execute-options" v-if="autoExecute">
              <text class="setting-label">单笔交易金额上限</text>
              <view class="slider-container">
                <slider 
                  :min="1000" 
                  :max="50000" 
                  :step="1000" 
                  :value="maxTradeAmount" 
                  @change="onMaxTradeAmountChange"
                  activeColor="#1989fa"
                  show-value
                />
                <text class="slider-value">{{ formatMoney(maxTradeAmount) }}</text>
              </view>
              
              <view class="warning-box">
                <text class="warning-icon">⚠️</text>
                <text class="warning-text">AI自动执行将按照系统规则直接进行交易,请确保您了解相关风险</text>
              </view>
            </view>
          </view>
        </view>
        
        <view class="form-item">
          <text class="item-label">风险等级</text>
          <view class="risk-options">
            <view 
              class="risk-option" 
              :class="{ active: riskLevel === 'low' }"
              @click="setRiskLevel('low')"
            >
              <text class="risk-name">低风险</text>
              <text class="risk-desc">高置信度交易,每日1次</text>
            </view>
            <view 
              class="risk-option" 
              :class="{ active: riskLevel === 'medium' }"
              @click="setRiskLevel('medium')"
            >
              <text class="risk-name">中等风险</text>
              <text class="risk-desc">标准交易,每日2次</text>
            </view>
            <view 
              class="risk-option" 
              :class="{ active: riskLevel === 'high' }"
              @click="setRiskLevel('high')"
            >
              <text class="risk-name">高风险</text>
              <text class="risk-desc">积极交易,每日3次</text>
            </view>
          </view>
        </view>
        
        <view class="form-item">
          <text class="item-label">自动交易</text>
          <switch 
            :checked="autoTrade" 
            @change="onAutoTradeChange" 
            color="#1989fa"
            style="transform: scale(0.8);"
          />
        </view>
        
        <view class="form-item">
          <text class="item-label">通知提醒</text>
          <switch 
            :checked="notifications" 
            @change="onNotificationsChange" 
            color="#1989fa"
            style="transform: scale(0.8);"
          />
        </view>

        <view class="form-item">
          <text class="item-label">高级设置</text>
          <view class="collapsible" @click="toggleAdvancedSettings">
            <text class="collapsible-text">{{ showAdvancedSettings ? '收起' : '展开' }}高级设置</text>
            <text class="collapsible-icon">{{ showAdvancedSettings ? '▲' : '▼' }}</text>
          </view>
          
          <view v-if="showAdvancedSettings" class="advanced-settings">
            <!-- 多时间周期确认 -->
            <view class="advanced-setting-item">
              <text class="setting-label">多时间周期确认</text>
              <switch 
                :checked="advancedSettings.multiTimeframe" 
                @change="(e) => updateAdvancedSetting('multiTimeframe', e.detail.value)"
                color="#1989fa"
                style="transform: scale(0.8);"
              />
            </view>
            
            <!-- 市场环境过滤 -->
            <view class="advanced-setting-item">
              <text class="setting-label">市场环境过滤</text>
              <switch 
                :checked="advancedSettings.marketFilter" 
                @change="(e) => updateAdvancedSetting('marketFilter', e.detail.value)"
                color="#1989fa"
                style="transform: scale(0.8);"
              />
            </view>
            
            <!-- 异常成交量剔除 -->
            <view class="advanced-setting-item">
              <text class="setting-label">异常成交量剔除</text>
              <switch 
                :checked="advancedSettings.abnormalVolumeFilter" 
                @change="(e) => updateAdvancedSetting('abnormalVolumeFilter', e.detail.value)"
                color="#1989fa"
                style="transform: scale(0.8);"
              />
            </view>
            
            <!-- 交易时间过滤 -->
            <view class="advanced-setting-item">
              <text class="setting-label">交易时间过滤</text>
              <switch 
                :checked="advancedSettings.timeFilter" 
                @change="(e) => updateAdvancedSetting('timeFilter', e.detail.value)"
                color="#1989fa"
                style="transform: scale(0.8);"
              />
            </view>
            
            <!-- 金字塔加仓策略 -->
            <view class="advanced-setting-item">
              <text class="setting-label">金字塔加仓策略</text>
              <switch 
                :checked="advancedSettings.pyramidPosition" 
                @change="(e) => updateAdvancedSetting('pyramidPosition', e.detail.value)"
                color="#1989fa"
                style="transform: scale(0.8);"
              />
            </view>
            
            <!-- 指标协同确认 -->
            <view class="advanced-setting-item">
              <text class="setting-label">指标协同确认</text>
              <picker 
                :value="indicatorConfirmIndexMap[advancedSettings.indicatorConfirm]" 
                :range="indicatorConfirmOptions" 
                @change="onIndicatorConfirmChange"
              >
                <view class="picker-view">
                  <text class="picker-text">{{ indicatorConfirmOptions[indicatorConfirmIndexMap[advancedSettings.indicatorConfirm]] }}</text>
                  <text class="picker-icon">▼</text>
                </view>
              </picker>
            </view>
            
            <!-- 单笔仓位占比 -->
            <view class="advanced-setting-item">
              <text class="setting-label">单笔最大仓位比例</text>
              <view class="slider-container small-slider">
                <slider 
                  :value="advancedSettings.maxPositionRatio * 100" 
                  :min="5" 
                  :max="50" 
                  :step="5" 
                  show-value 
                  @change="onMaxPositionRatioChange"
                  activeColor="#1989fa"
                />
                <text class="slider-value">{{ advancedSettings.maxPositionRatio * 100 }}%</text>
              </view>
            </view>
          </view>
        </view>
      </view>
    </view>
    
    <view class="settings-footer">
      <button class="btn btn-cancel" @click="close">取消</button>
      <button class="btn btn-save" @click="saveSettings">保存设置</button>
    </view>
  </view>
</template>

<script>
import agentTradingService from '@/services/agentTradingService.js';

export default {
  name: 'AITradingSettings',
  data() {
    return {
      // 默认设置
      selectedStrategy: 'trend_following_v2',
      maxPositions: 5,
      riskLevel: 'medium',
      autoTrade: true,
      notifications: true,
      
      // 可选策略列表
      strategies: [
        { 
          id: 'trend_following_v2', 
          name: '趋势跟踪 v2', 
          description: '根据价格趋势进行交易,适合波动明显的股票' 
        },
        { 
          id: 'mean_reversion', 
          name: '均值回归', 
          description: '追踪价格回归均值的过程,适合稳定型股票' 
        },
        { 
          id: 'dual_thrust', 
          name: '双重突破', 
          description: '结合开盘区间突破和日内波动特征' 
        },
        { 
          id: 'volatility_breakout', 
          name: '波动率突破', 
          description: '利用波动率范围判断价格突破有效性' 
        },
        { 
          id: 'pattern_recognition', 
          name: '形态识别', 
          description: '识别K线形态并预测后续走势' 
        },
        { 
          id: 'yin_yang_double_yin', 
          name: '阴阳双阴战法', 
          description: '基于阴阳双阴K线形态进行交易,适合震荡行情' 
        },
        { 
          id: 'enhanced_yin_yang_double_yin', 
          name: '增强型阴阳双阴战法', 
          description: '多时间周期确认的阴阳双阴形态,整合支撑阻力位与成交量分析' 
        }
      ],
      
      // 高级设置
      showAdvancedSettings: false,
      advancedSettings: {
        multiTimeframe: true,       // 多时间周期确认
        marketFilter: true,         // 市场环境过滤
        abnormalVolumeFilter: true, // 异常成交量剔除
        timeFilter: true,           // 交易时间过滤
        pyramidPosition: false,     // 金字塔加仓策略
        indicatorConfirm: 'macd_kdj', // 指标协同确认
        maxPositionRatio: 0.2,      // 单笔最大仓位比例
      },
      
      // 指标协同确认选项
      indicatorConfirmOptions: ['MACD+KDJ', 'MACD+布林带', 'KDJ+布林带', '全部指标', '不使用指标'],
      indicatorConfirmIndexMap: {
        'macd_kdj': 0,
        'macd_boll': 1,
        'kdj_boll': 2,
        'all': 3,
        'none': 4
      },
      
      // 是否有更改
      hasChanges: false,
      isLoading: false,
      autoExecute: false,
      maxTradeAmount: 10000
    };
  },
  mounted() {
    this.loadSettings();
  },
  methods: {
    formatMoney(amount) {
      return '¥' + amount.toLocaleString('zh-CN');
    },
    
    // 高级设置开关
    toggleAdvancedSettings() {
      this.showAdvancedSettings = !this.showAdvancedSettings;
    },
    
    // 更新高级设置
    updateAdvancedSetting(key, value) {
      this.advancedSettings[key] = value;
      this.hasChanges = true;
    },
    
    // 指标协同确认选项变化
    onIndicatorConfirmChange(e) {
      const index = e.detail.value;
      const keys = Object.keys(this.indicatorConfirmIndexMap);
      const selectedKey = keys.find(key => this.indicatorConfirmIndexMap[key] === parseInt(index));
      
      if (selectedKey) {
        this.advancedSettings.indicatorConfirm = selectedKey;
        this.hasChanges = true;
      }
    },
    
    // 最大仓位比例变化
    onMaxPositionRatioChange(e) {
      this.advancedSettings.maxPositionRatio = e.detail.value / 100;
      this.hasChanges = true;
    },
    
    // 加载设置
    async loadSettings() {
      this.isLoading = true;
      
      try {
        // 先获取常规AI设置
        const result = await agentTradingService.getSettings();
        
        // 获取自动执行设置
        const executionSettings = await this.loadExecutionSettings();
        
        if (result.success && result.data) {
          this.selectedStrategy = result.data.strategy_id || 'trend_following_v2';
          this.maxPositions = result.data.max_positions || 5;
          this.riskLevel = result.data.risk_level || 'medium';
          this.autoTrade = result.data.auto_trade || true;
          this.notifications = result.data.notifications || true;
          
          // 高级设置
          if (result.data.advanced_settings) {
            this.advancedSettings = { ...this.advancedSettings, ...result.data.advanced_settings };
          }
        }
        
        // 应用自动执行设置
        if (executionSettings) {
          this.autoExecute = executionSettings.auto_execute || false;
          this.maxTradeAmount = executionSettings.max_trade_amount || 10000;
        }
        
        this.hasChanges = false;
      } catch (error) {
        console.error('加载AI设置失败:', error);
      } finally {
        this.isLoading = false;
      }
    },
    
    async loadExecutionSettings() {
      try {
        // 调用后端API获取自动执行设置
        const response = await uni.request({
          url: '/api/t-trading/ai-execution-settings',
          method: 'GET'
        });
        
        if (response && response.data) {
          return response.data;
        }
        return null;
      } catch (error) {
        console.error('加载AI自动执行设置失败:', error);
        return null;
      }
    },

    async saveSettings() {
      if (!this.hasChanges) {
        this.close();
        return;
      }
      
      this.isLoading = true;
      
      try {
        // 保存常规AI设置
        const settings = {
          strategy_id: this.selectedStrategy,
          max_positions: this.maxPositions,
          risk_level: this.riskLevel,
          auto_trade: this.autoTrade,
          notifications: this.notifications,
          advanced_settings: this.advancedSettings
        };
        
        const result = await agentTradingService.updateSettings(settings);
        
        // 保存自动执行设置
        await this.saveExecutionSettings();
        
        if (result && result.success) {
          uni.showToast({
            title: '设置已保存',
            icon: 'success'
          });
          
          // 重置更改标记
          this.hasChanges = false;
          
          // 关闭设置面板
          setTimeout(() => {
            this.close();
          }, 1500);
        } else {
          uni.showToast({
            title: result.message || '保存设置失败',
            icon: 'none'
          });
        }
      } catch (error) {
        console.error('保存AI设置失败:', error);
        uni.showToast({
          title: '保存设置失败',
          icon: 'none'
        });
      } finally {
        this.isLoading = false;
      }
    },
    
    async saveExecutionSettings() {
      try {
        // 调用后端API保存自动执行设置
        await uni.request({
          url: '/api/t-trading/update-ai-execution-settings',
          method: 'POST',
          data: {
            auto_execute: this.autoExecute,
            max_trade_amount: this.maxTradeAmount
          }
        });
        return true;
      } catch (error) {
        console.error('保存AI自动执行设置失败:', error);
        return false;
      }
    },
    
    // 选择策略
    selectStrategy(strategyId) {
      this.selectedStrategy = strategyId;
      this.hasChanges = true;
    },
    
    // 更改最大持仓数量
    onMaxPositionsChange(e) {
      this.maxPositions = e.detail.value;
      this.hasChanges = true;
    },
    
    // 设置风险等级
    setRiskLevel(level) {
      this.riskLevel = level;
      this.hasChanges = true;
    },
    
    // 更改自动交易开关
    onAutoTradeChange(e) {
      this.autoTrade = e.detail.value;
      this.hasChanges = true;
    },
    
    // 更改通知提醒开关
    onNotificationsChange(e) {
      this.notifications = e.detail.value;
      this.hasChanges = true;
    },
    
    // 更改AI自动执行开关
    onAutoExecuteChange(e) {
      this.autoExecute = e.detail.value;
      this.hasChanges = true;
    },
    
    // 更改单笔交易金额上限
    onMaxTradeAmountChange(e) {
      this.maxTradeAmount = e.detail.value;
      this.hasChanges = true;
    },
    
    // 关闭设置面板
    close() {
      if (this.hasChanges) {
        uni.showModal({
          title: '未保存的更改',
          content: '您有未保存的设置更改,确定要离开吗?',
          success: (res) => {
            if (res.confirm) {
              this.$emit('close');
            }
          }
        });
      } else {
        this.$emit('close');
      }
    }
  }
};
</script>

<style lang="scss">
.settings-popup {
  width: 650rpx;
  background-color: #222;
  border-radius: 16rpx;
  overflow: hidden;
  box-shadow: 0 5rpx 25rpx rgba(0, 0, 0, 0.2);
}

.settings-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 25rpx;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  
  .settings-title {
    font-size: 32rpx;
    font-weight: bold;
    color: #fff;
  }
  
  .close-btn {
    font-size: 40rpx;
    color: #999;
    padding: 10rpx;
  }
}

.settings-body {
  padding: 25rpx;
  max-height: 750rpx;
  overflow-y: auto;
}

.settings-form {
  .form-item {
    margin-bottom: 30rpx;
    
    .item-label {
      font-size: 28rpx;
      color: #ccc;
      margin-bottom: 15rpx;
      display: block;
    }
  }
  
  .strategy-options {
    display: flex;
    flex-direction: column;
    gap: 15rpx;
    
    .strategy-option {
      padding: 20rpx;
      border-radius: 12rpx;
      border: 1px solid rgba(255, 255, 255, 0.1);
      background-color: rgba(255, 255, 255, 0.05);
      
      &.active {
        border-color: #1989fa;
        background-color: rgba(25, 137, 250, 0.1);
      }
      
      .strategy-name {
        font-size: 28rpx;
        color: #fff;
        margin-bottom: 8rpx;
        display: block;
      }
      
      .strategy-desc {
        font-size: 24rpx;
        color: #999;
      }
    }
  }
  
  .slider-container {
    padding: 0 10rpx;
    
    &.small-slider {
      display: flex;
      align-items: center;
      
      .slider-value {
        font-size: 24rpx;
        color: #ccc;
        margin-left: 10rpx;
        width: 60rpx;
      }
    }
  }
  
  .risk-options {
    display: flex;
    justify-content: space-between;
    
    .risk-option {
      flex: 1;
      text-align: center;
      padding: 15rpx 0;
      background-color: rgba(255, 255, 255, 0.05);
      border: 1px solid rgba(255, 255, 255, 0.1);
      margin: 0 10rpx;
      border-radius: 8rpx;
      
      &:first-child {
        margin-left: 0;
      }
      
      &:last-child {
        margin-right: 0;
      }
      
      &.active {
        &:nth-child(1) {
          border-color: #52c41a;
          background-color: rgba(82, 196, 26, 0.1);
        }
        
        &:nth-child(2) {
          border-color: #faad14;
          background-color: rgba(250, 173, 20, 0.1);
        }
        
        &:nth-child(3) {
          border-color: #f5222d;
          background-color: rgba(245, 34, 45, 0.1);
        }
      }
      
      .risk-name {
        font-size: 26rpx;
        color: #fff;
      }
      
      .risk-desc {
        font-size: 24rpx;
        color: #999;
      }
    }
  }
  
  .collapsible {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 15rpx;
    background-color: rgba(255, 255, 255, 0.05);
    border-radius: 8rpx;
    margin-bottom: 15rpx;
    
    .collapsible-text {
      font-size: 26rpx;
      color: #1989fa;
    }
    
    .collapsible-icon {
      font-size: 24rpx;
      color: #1989fa;
    }
  }
  
  .advanced-settings {
    background-color: rgba(0, 0, 0, 0.2);
    border-radius: 8rpx;
    padding: 15rpx;
    
    .advanced-setting-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 12rpx 0;
      border-bottom: 1px solid rgba(255, 255, 255, 0.05);
      
      &:last-child {
        border-bottom: none;
      }
      
      .setting-label {
        font-size: 26rpx;
        color: #ccc;
      }
      
      .picker-view {
        display: flex;
        align-items: center;
        
        .picker-text {
          font-size: 26rpx;
          color: #1989fa;
          margin-right: 10rpx;
        }
        
        .picker-icon {
          font-size: 22rpx;
          color: #1989fa;
        }
      }
    }
  }
}

.settings-footer {
  display: flex;
  padding: 25rpx;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  
  .btn {
    flex: 1;
    padding: 20rpx 0;
    border-radius: 8rpx;
    font-size: 28rpx;
    text-align: center;
    
    &:first-child {
      margin-right: 15rpx;
    }
  }
  
  .btn-cancel {
    background-color: rgba(255, 255, 255, 0.1);
    color: #fff;
  }
  
  .btn-save {
    background-color: #1989fa;
    color: #fff;
  }
}

.auto-execute-container {
  display: flex;
  flex-direction: column;
  gap: 15rpx;
}

.auto-execute-toggle {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15rpx;
  background-color: rgba(255, 255, 255, 0.05);
  border-radius: 8rpx;
}

.auto-execute-desc {
  font-size: 24rpx;
  color: #999;
}

.auto-execute-options {
  display: flex;
  flex-direction: column;
  gap: 15rpx;
}

.warning-box {
  display: flex;
  align-items: center;
  padding: 15rpx;
  background-color: rgba(255, 255, 255, 0.05);
  border-radius: 8rpx;
  
  .warning-icon {
    font-size: 24rpx;
    color: #f5222d;
    margin-right: 10rpx;
  }
  
  .warning-text {
    font-size: 24rpx;
    color: #999;
  }
}
</style> 
