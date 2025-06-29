<template>
  <view class="t0pool-settings-container">
    <view class="settings-header">
      <text class="settings-title">T+0交易池更新设置</text>
      <view class="status-badge" :class="{
        'active': updateConfig.isAutoUpdateEnabled, 
        'inactive': !updateConfig.isAutoUpdateEnabled
      }">
        {{ updateConfig.isAutoUpdateEnabled ? '自动更新中' : '未启用自动更新' }}
      </view>
    </view>
    
    <view class="settings-body">
      <uni-forms :model="configForm" label-position="top">
        <!-- 自动更新开关 -->
        <view class="form-row">
          <text class="form-label">自动更新:</text>
          <switch :checked="configForm.autoUpdateEnabled" @change="onAutoUpdateChange" color="#007aff" />
        </view>
        
        <!-- 常规更新间隔 -->
        <uni-forms-item label="常规更新间隔(分钟)">
          <slider 
            :min="5" 
            :max="60" 
            :step="5"
            :value="configForm.regularInterval" 
            show-value
            @change="onRegularIntervalChange"
          />
        </uni-forms-item>
        
        <!-- 尾盘扫描间隔 -->
        <uni-forms-item label="尾盘扫描间隔(分钟)">
          <slider 
            :min="1" 
            :max="15" 
            :step="1"
            :value="configForm.eodScanInterval" 
            show-value
            @change="onEodScanIntervalChange"
          />
        </uni-forms-item>
        
        <!-- 尾盘模式开始时间 -->
        <uni-forms-item label="尾盘模式开始时间">
          <uni-datetime-picker
            type="time"
            v-model="configForm.eodModeStartTime"
            @change="onEodTimeChange"
          />
        </uni-forms-item>
      </uni-forms>
      
      <button class="save-btn" type="primary" @click="saveSettings">保存设置</button>
    </view>
    
    <view class="current-status">
      <view class="status-row">
        <text class="status-label">当前模式:</text>
        <text class="status-value" :class="{'eod-mode': updateConfig.isInEodMode}">
          {{ updateConfig.isInEodMode ? '尾盘扫描模式' : '常规更新模式' }}
        </text>
      </view>
      
      <view class="status-row">
        <text class="status-label">上次更新:</text>
        <text class="status-value">{{ lastUpdateTime }}</text>
      </view>
      
      <view class="status-row">
        <text class="status-label">下次更新:</text>
        <text class="status-value">{{ nextUpdateTime }}</text>
      </view>
    </view>
    
    <view class="eod-rules-desc">
      <view class="desc-title">尾盘模式说明:</view>
      <view class="desc-content">
        <text class="desc-item">• 尾盘模式(EOD)从设定的开始时间到收盘(15:00)期间启用</text>
        <text class="desc-item">• 尾盘模式会使用更短的扫描间隔,以捕捉更多交易机会</text>
        <text class="desc-item">• 在尾盘模式下,系统会使用更敏感的筛选条件,优先考虑日内波动较大的股票</text>
        <text class="desc-item">• 建议将尾盘模式开始时间设置在14:00-14:30之间,以便充分捕捉尾盘行情</text>
      </view>
    </view>
    
    <view class="manual-update">
      <button class="update-now-btn" type="default" @click="updateNow">立即更新交易池</button>
    </view>
  </view>
</template>

<script>
import agentTradingService from '../../services/agentTradingService.js';

export default {
  name: "T0PoolSettings",
  data() {
    return {
      updateConfig: {
        regularInterval: 30,
        eodScanInterval: 5,
        eodModeStartTime: '14:30:00',
        autoUpdateEnabled: true,
        isInEodMode: false,
        isWithinTradingHours: false,
        lastUpdateTime: null
      },
      configForm: {
        regularInterval: 30,
        eodScanInterval: 5,
        eodModeStartTime: '14:30',
        autoUpdateEnabled: true
      },
      statusTimer: null,
      lastUpdateTimeValue: null,
      nextUpdateTimeValue: null
    }
  },
  
  computed: {
    lastUpdateTime() {
      if (!this.lastUpdateTimeValue) return '未更新';
      
      const date = new Date(this.lastUpdateTimeValue);
      return date.toLocaleTimeString();
    },
    
    nextUpdateTime() {
      if (!this.nextUpdateTimeValue) return '未知';
      
      const date = new Date(this.nextUpdateTimeValue);
      return date.toLocaleTimeString();
    }
  },
  
  async created() {
    try {
      // 获取当前T+0池更新配置
      const config = await agentTradingService.getT0PoolUpdateConfig();
      this.updateConfig = config;
      
      // 更新表单数据
      this.configForm.regularInterval = config.regularInterval;
      this.configForm.eodScanInterval = config.eodScanInterval;
      this.configForm.eodModeStartTime = config.eodModeStartTime.substring(0, 5); // 只保留HH:MM部分
      this.configForm.autoUpdateEnabled = config.isAutoUpdateEnabled;
      
      // 设置上次更新时间
      this.lastUpdateTimeValue = config.lastUpdateTime;
      
      // 计算下次更新时间
      this.calculateNextUpdateTime();
      
      // 启动状态定时器
      this.startStatusTimer();
      
      // 注册T+0池更新事件监听
      window.addEventListener('t0pool-updated', this.handleT0PoolUpdate);
    } catch (e) {
      console.error('加载T+0池更新配置失败:', e);
      uni.showToast({
        title: '加载配置失败',
        icon: 'none'
      });
    }
  },
  
  beforeDestroy() {
    // 清除定时器
    if (this.statusTimer) {
      clearInterval(this.statusTimer);
    }
    
    // 移除事件监听
    window.removeEventListener('t0pool-updated', this.handleT0PoolUpdate);
  },
  
  methods: {
    // 启动状态更新定时器
    startStatusTimer() {
      this.statusTimer = setInterval(() => {
        // 检查当前是否处于尾盘模式
        const now = new Date();
        const currentTime = now.toTimeString().substring(0, 8);
        
        this.updateConfig.isInEodMode = currentTime >= this.updateConfig.eodModeStartTime && 
                                      currentTime <= '15:00:00';
                                      
        // 检查是否在交易时间内
        this.updateConfig.isWithinTradingHours = currentTime >= '09:30:00' && 
                                              currentTime <= '15:00:00';
                                              
        // 更新下次更新时间
        this.calculateNextUpdateTime();
      }, 10000); // 每10秒更新一次状态
    },
    
    // 计算下次更新时间
    calculateNextUpdateTime() {
      if (!this.updateConfig.isAutoUpdateEnabled) {
        this.nextUpdateTimeValue = null;
        return;
      }
      
      const now = new Date();
      const updateInterval = this.updateConfig.isInEodMode ? 
        this.updateConfig.eodScanInterval : 
        this.updateConfig.regularInterval;
        
      // 如果有上次更新时间,基于此计算下次更新
      if (this.lastUpdateTimeValue) {
        const lastUpdate = new Date(this.lastUpdateTimeValue);
        const nextUpdate = new Date(lastUpdate.getTime() + updateInterval * 60 * 1000);
        
        // 如果下次更新时间已经过去,则基于当前时间计算
        if (nextUpdate <= now) {
          this.nextUpdateTimeValue = new Date(now.getTime() + updateInterval * 60 * 1000);
        } else {
          this.nextUpdateTimeValue = nextUpdate;
        }
      } else {
        // 没有上次更新时间,基于当前时间计算
        this.nextUpdateTimeValue = new Date(now.getTime() + updateInterval * 60 * 1000);
      }
    },
    
    // T+0池更新事件处理
    handleT0PoolUpdate(event) {
      const updateData = event.detail;
      this.lastUpdateTimeValue = updateData.updateTime;
      this.calculateNextUpdateTime();
      
      // 显示更新通知
      uni.showToast({
        title: `交易池已更新: ${updateData.isEodMode ? '尾盘模式' : '常规模式'}`,
        icon: 'success'
      });
    },
    
    // 表单事件处理
    onAutoUpdateChange(e) {
      this.configForm.autoUpdateEnabled = e.target.value;
    },
    
    onRegularIntervalChange(e) {
      this.configForm.regularInterval = e.detail.value;
    },
    
    onEodScanIntervalChange(e) {
      this.configForm.eodScanInterval = e.detail.value;
    },
    
    onEodTimeChange(time) {
      this.configForm.eodModeStartTime = time;
    },
    
    // 保存设置
    async saveSettings() {
      try {
        // 构建配置对象
        const config = {
          regularInterval: Number(this.configForm.regularInterval),
          eodScanInterval: Number(this.configForm.eodScanInterval),
          eodModeStartTime: this.configForm.eodModeStartTime + ':00', // 添加秒
          autoUpdateEnabled: this.configForm.autoUpdateEnabled
        };
        
        // 更新配置
        const result = await agentTradingService.configureT0PoolUpdate(config);
        
        if (result) {
          this.updateConfig = result;
          
          uni.showToast({
            title: '设置已保存',
            icon: 'success'
          });
          
          // 如果启用了自动更新,重新计算下次更新时间
          if (config.autoUpdateEnabled) {
            this.calculateNextUpdateTime();
          }
        } else {
          uni.showToast({
            title: '保存设置失败',
            icon: 'none'
          });
        }
      } catch (e) {
        console.error('保存T+0池更新配置失败:', e);
        uni.showToast({
          title: '保存配置失败',
          icon: 'none'
        });
      }
    },
    
    // 立即更新
    async updateNow() {
      try {
        uni.showLoading({
          title: '更新中...'
        });
        
        // 调用后端更新T+0池
        await agentTradingService.updateT0StocksPool();
        
        // 更新状态
        this.lastUpdateTimeValue = new Date();
        this.calculateNextUpdateTime();
        
        uni.hideLoading();
        uni.showToast({
          title: '交易池已更新',
          icon: 'success'
        });
      } catch (e) {
        console.error('手动更新T+0池失败:', e);
        uni.hideLoading();
        uni.showToast({
          title: '更新失败',
          icon: 'none'
        });
      }
    }
  }
}
</script>

<style scoped>
.t0pool-settings-container {
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 16px;
  margin: 10px 0;
}

.settings-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.settings-title {
  font-size: 18px;
  font-weight: bold;
}

.status-badge {
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 12px;
  color: #ffffff;
}

.active {
  background-color: #19be6b;
}

.inactive {
  background-color: #909399;
}

.settings-body {
  margin-bottom: 20px;
}

.form-row {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
}

.form-label {
  flex: 1;
  font-size: 14px;
}

.save-btn {
  margin-top: 10px;
  width: 100%;
}

.current-status {
  background-color: #f8f8f8;
  border-radius: 6px;
  padding: 12px;
  margin-bottom: 20px;
}

.status-row {
  display: flex;
  margin-bottom: 8px;
}

.status-label {
  width: 80px;
  font-size: 14px;
  color: #606266;
}

.status-value {
  font-size: 14px;
  font-weight: 500;
}

.eod-mode {
  color: #e6a23c;
  font-weight: bold;
}

.eod-rules-desc {
  border: 1px dashed #dcdfe6;
  border-radius: 6px;
  padding: 12px;
  margin-bottom: 20px;
}

.desc-title {
  font-size: 15px;
  font-weight: bold;
  margin-bottom: 8px;
}

.desc-content {
  font-size: 13px;
  color: #606266;
}

.desc-item {
  display: block;
  margin-bottom: 6px;
  line-height: 1.4;
}

.manual-update {
  display: flex;
  justify-content: center;
}

.update-now-btn {
  width: 80%;
}
</style> 
