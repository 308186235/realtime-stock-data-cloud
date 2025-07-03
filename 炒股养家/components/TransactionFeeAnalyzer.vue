<template>
  <view class="fee-analyzer-container">
    <view class="analyzer-header">
      <text class="analyzer-title">交易费用分析</text>
      <view class="analyzer-actions">
        <view class="time-range">
          <picker mode="date" :value="startDate" @change="onStartDateChange">
            <text class="date-text">{{ startDate }}</text>
          </picker>
          <text class="date-separator">至</text>
          <picker mode="date" :value="endDate" @change="onEndDateChange">
            <text class="date-text">{{ endDate }}</text>
          </picker>
        </view>
        <button class="analyze-btn" @click="loadData" size="mini" type="primary">分析</button>
      </view>
    </view>
    
    <view v-if="loading" class="loading-container">
      <uni-load-more status="loading" :iconSize="18" iconColor="#999"></uni-load-more>
    </view>
    
    <view v-else-if="error" class="error-container">
      <text class="error-text">{{ error }}</text>
      <button class="retry-btn" size="mini" type="default" @click="loadData">重试</button>
    </view>
    
    <view v-else class="analyzer-content">
      <!-- 费用总览 -->
      <view class="fee-summary-card">
        <view class="summary-title">费用总览</view>
        <view class="summary-items">
          <view class="summary-item">
            <text class="item-label">总交易额</text>
            <text class="item-value">{{ formatAmount(feeSummary.totalTradeAmount) }}元</text>
          </view>
          <view class="summary-item">
            <text class="item-label">总费用</text>
            <text class="item-value">{{ formatAmount(feeSummary.totalFees) }}元</text>
          </view>
          <view class="summary-item">
            <text class="item-label">印花税</text>
            <text class="item-value">{{ formatAmount(feeSummary.totalStampDuty) }}元</text>
          </view>
          <view class="summary-item">
            <text class="item-label">佣金</text>
            <text class="item-value">{{ formatAmount(feeSummary.totalCommission) }}元</text>
          </view>
          <view class="summary-item">
            <text class="item-label">过户费</text>
            <text class="item-value">{{ formatAmount(feeSummary.totalTransferFee) }}元</text>
          </view>
        </view>
      </view>
      
      <!-- 交易费用明细 -->
      <view class="fee-details-card" v-if="tradeDetails.length > 0">
        <view class="details-title">交易费用明细</view>
        
        <view class="table-header">
          <text class="header-cell date">日期</text>
          <text class="header-cell stock">股票</text>
          <text class="header-cell direction">方向</text>
          <text class="header-cell price">价格</text>
          <text class="header-cell volume">数量</text>
          <text class="header-cell fee">费用</text>
        </view>
        
        <scroll-view class="table-content" scroll-y>
          <view 
            v-for="(trade, index) in tradeDetails" 
            :key="index" 
            class="table-row"
            :class="{ 'even-row': index % 2 === 1 }"
            @click="showTradeDetail(trade)"
          >
            <text class="row-cell date">{{ formatTradeDate(trade.tradeTime) }}</text>
            <text class="row-cell stock">{{ trade.name }}</text>
            <text class="row-cell direction" :class="trade.direction === 'BUY' ? 'buy-text' : 'sell-text'">
              {{ trade.direction === 'BUY' ? '买入' : '卖出' }}
            </text>
            <text class="row-cell price">{{ trade.price }}</text>
            <text class="row-cell volume">{{ trade.volume }}</text>
            <text class="row-cell fee">{{ formatAmount(trade.fees.totalFees) }}</text>
          </view>
        </scroll-view>
      </view>
      
      <view v-else class="empty-data">
        <text class="empty-text">暂无交易记录</text>
      </view>
    </view>
    
    <!-- 交易详情弹窗 -->
    <uni-popup ref="tradeDetailPopup" type="center">
      <view class="trade-detail-popup">
        <view class="popup-header">
          <text class="popup-title">交易费用详情</text>
          <view class="close-btn" @click="closePopup">×</view>
        </view>
        
        <view class="popup-content" v-if="selectedTrade">
          <view class="detail-row">
            <text class="detail-label">交易时间</text>
            <text class="detail-value">{{ formatTradeDateTime(selectedTrade.tradeTime) }}</text>
          </view>
          
          <view class="detail-row">
            <text class="detail-label">股票</text>
            <text class="detail-value">{{ selectedTrade.name }} ({{ selectedTrade.symbol }})</text>
          </view>
          
          <view class="detail-row">
            <text class="detail-label">交易类型</text>
            <text class="detail-value" :class="selectedTrade.direction === 'BUY' ? 'buy-text' : 'sell-text'">
              {{ selectedTrade.direction === 'BUY' ? '买入' : '卖出' }}
            </text>
          </view>
          
          <view class="detail-row">
            <text class="detail-label">成交价格</text>
            <text class="detail-value">{{ selectedTrade.price }}元</text>
          </view>
          
          <view class="detail-row">
            <text class="detail-label">成交数量</text>
            <text class="detail-value">{{ selectedTrade.volume }}股</text>
          </view>
          
          <view class="detail-row">
            <text class="detail-label">交易金额</text>
            <text class="detail-value">{{ formatAmount(selectedTrade.price * selectedTrade.volume) }}元</text>
          </view>
          
          <view class="divider"></view>
          
          <view class="detail-row">
            <text class="detail-label">总费用</text>
            <text class="detail-value fee-text">{{ formatAmount(selectedTrade.fees.totalFees) }}元</text>
          </view>
          
          <view class="detail-row" v-if="selectedTrade.fees.stampDuty > 0">
            <text class="detail-label">印花税</text>
            <text class="detail-value">{{ formatAmount(selectedTrade.fees.stampDuty) }}元</text>
          </view>
          
          <view class="detail-row">
            <text class="detail-label">佣金</text>
            <text class="detail-value">{{ formatAmount(selectedTrade.fees.commission) }}元</text>
          </view>
          
          <view class="detail-row" v-if="selectedTrade.fees.transferFee > 0">
            <text class="detail-label">过户费</text>
            <text class="detail-value">{{ formatAmount(selectedTrade.fees.transferFee) }}元</text>
          </view>
          
          <view class="detail-row" v-if="selectedTrade.balanceChange">
            <text class="detail-label">账户余额变化</text>
            <text class="detail-value" :class="selectedTrade.balanceChange > 0 ? 'positive-amount' : 'negative-amount'">
              {{ selectedTrade.balanceChange > 0 ? '+' : '' }}{{ formatAmount(selectedTrade.balanceChange) }}元
            </text>
          </view>
        </view>
      </view>
    </uni-popup>
  </view>
</template>

<script>
import tradingService from '../services/tradingService.js';
import { calculateTransactionFees, estimateTransactionFees } from '../utils/feeCalculator.js';
import uniLoadMore from '@dcloudio/uni-ui/lib/uni-load-more/uni-load-more.vue';
import uniPopup from '@dcloudio/uni-ui/lib/uni-popup/uni-popup.vue';

export default {
  name: 'TransactionFeeAnalyzer',
  components: {
    uniLoadMore,
    uniPopup
  },
  data() {
    // 设置默认日期为过去一个月
    const endDate = new Date();
    const startDate = new Date();
    startDate.setMonth(startDate.getMonth() - 1);
    
    return {
      loading: false,
      error: null,
      startDate: this.formatDate(startDate),
      endDate: this.formatDate(endDate),
      trades: [],
      balanceHistory: [],
      feeSummary: {
        totalTradeAmount: 0,
        totalFees: 0,
        totalStampDuty: 0,
        totalCommission: 0,
        totalTransferFee: 0
      },
      tradeDetails: [],
      selectedTrade: null
    };
  },
  mounted() {
    this.loadData();
  },
  methods: {
    async loadData() {
      this.loading = true;
      this.error = null;
      
      try {
        // 获取交易记录
        const tradesResult = await tradingService.getTrades({
          start_date: this.startDate,
          end_date: this.endDate
        });
        
        if (!tradesResult.success) {
          throw new Error(tradesResult.message || '获取交易记录失败');
        }
        
        this.trades = tradesResult.data || [];
        
        // 获取账户余额历史
        const balanceHistoryResult = await this.getBalanceHistory();
        this.balanceHistory = balanceHistoryResult.data || [];
        
        // 分析费用
        this.analyzeFees();
      } catch (error) {
        console.error('加载数据失败:', error);
        this.error = error.message || '加载数据失败';
      } finally {
        this.loading = false;
      }
    },
    
    // 获取余额历史变化记录 - 实际应用中需要服务端支持此API
    async getBalanceHistory() {
      // 开发环境下要求真实数据
      if (process.env.NODE_ENV === 'development') {
        // 🚨 禁用模拟数据 - 要求真实余额历史数据
        console.error('[真实数据要求] 拒绝要求真实数据');
        throw new Error('❌ 系统要求真实余额历史数据，拒绝要求真实数据源。');
      }
      
      // 实际应用中应该调用API获取余额历史
      try {
        const response = await uni.request({
          url: `${tradingService.API_PREFIX}/balance/history`,
          method: 'GET',
          data: {
            start_date: this.startDate,
            end_date: this.endDate
          }
        });
        
        if (response.statusCode === 200) {
          return response.data;
        } else {
          throw new Error(`获取余额历史失败: ${response.statusCode}`);
        }
      } catch (error) {
        console.error('获取余额历史异常:', error);
        // 出错时返回空数组,继续使用估算费用
        return { success: true, data: [] };
      }
    },
    
    // 分析费用
    analyzeFees() {
      // 重置费用统计
      this.feeSummary = {
        totalTradeAmount: 0,
        totalFees: 0,
        totalStampDuty: 0,
        totalCommission: 0,
        totalTransferFee: 0
      };
      
      // 处理交易明细和费用
      this.tradeDetails = this.trades.map(trade => {
        const isBuy = trade.direction === 'BUY';
        const tradeAmount = trade.price * trade.volume;
        
        // 查找对应的余额变化记录
        const balanceRecord = this.findBalanceRecordForTrade(trade);
        
        let fees;
        if (balanceRecord) {
          // 如果找到余额变化记录,使用实际余额变化计算费用
          fees = calculateTransactionFees(trade, balanceRecord.balance);
        } else {
          // 否则使用估算费用
          fees = estimateTransactionFees(trade.direction, trade.price, trade.volume);
        }
        
        // 累加总费用
        this.feeSummary.totalTradeAmount += tradeAmount;
        this.feeSummary.totalFees += fees.totalFees;
        this.feeSummary.totalStampDuty += fees.stampDuty;
        this.feeSummary.totalCommission += fees.commission;
        this.feeSummary.totalTransferFee += fees.transferFee;
        
        // 返回处理后的交易明细
        return {
          ...trade,
          fees,
          balanceChange: balanceRecord ? balanceRecord.balance : null
        };
      });
    },
    
    // 查找交易对应的余额变化记录
    findBalanceRecordForTrade(trade) {
      if (!this.balanceHistory || this.balanceHistory.length === 0) return null;
      
      const tradeTime = new Date(trade.trade_time || trade.tradeTime).getTime();
      
      // 查找时间最接近的余额变化记录
      return this.balanceHistory.find(record => {
        return record.tradeId === trade.trade_id || 
               (Math.abs(record.time - tradeTime) < 60000 && record.type === trade.direction); // 1分钟内
      });
    },
    
    // 显示交易详情
    showTradeDetail(trade) {
      this.selectedTrade = trade;
      this.$refs.tradeDetailPopup.open();
    },
    
    // 关闭弹窗
    closePopup() {
      this.$refs.tradeDetailPopup.close();
    },
    
    // 格式化日期 (YYYY-MM-DD)
    formatDate(date) {
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      return `${year}-${month}-${day}`;
    },
    
    // 格式化交易日期 (MM-DD)
    formatTradeDate(dateStr) {
      const date = new Date(dateStr);
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      return `${month}-${day}`;
    },
    
    // 格式化交易日期时间 (YYYY-MM-DD HH:MM)
    formatTradeDateTime(dateStr) {
      const date = new Date(dateStr);
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      const hours = String(date.getHours()).padStart(2, '0');
      const minutes = String(date.getMinutes()).padStart(2, '0');
      return `${year}-${month}-${day} ${hours}:${minutes}`;
    },
    
    // 格式化金额
    formatAmount(amount) {
      if (amount === undefined || amount === null) return '0.00';
      return parseFloat(amount).toFixed(2);
    },
    
    // 起始日期变更
    onStartDateChange(e) {
      this.startDate = e.detail.value;
    },
    
    // 结束日期变更
    onEndDateChange(e) {
      this.endDate = e.detail.value;
    }
  }
};
</script>

<style lang="scss" scoped>
.fee-analyzer-container {
  background-color: #fff;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 1px 6px rgba(0, 0, 0, 0.1);
  margin: 10px;
}

.analyzer-header {
  margin-bottom: 15px;
  
  .analyzer-title {
    font-size: 16px;
    font-weight: bold;
    color: #333;
    margin-bottom: 10px;
  }
  
  .analyzer-actions {
    display: flex;
    justify-content: space-between;
    align-items: center;
    
    .time-range {
      display: flex;
      align-items: center;
      font-size: 14px;
      color: #333;
      
      .date-text {
        background-color: #f5f5f5;
        padding: 4px 8px;
        border-radius: 4px;
      }
      
      .date-separator {
        margin: 0 5px;
        color: #666;
      }
    }
    
    .analyze-btn {
      font-size: 14px;
      margin-left: 10px;
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

.fee-summary-card {
  background-color: #f9f9f9;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 15px;
  
  .summary-title {
    font-size: 15px;
    font-weight: bold;
    color: #333;
    margin-bottom: 10px;
  }
  
  .summary-items {
    display: flex;
    flex-wrap: wrap;
    
    .summary-item {
      width: 50%;
      margin-bottom: 10px;
      
      .item-label {
        font-size: 13px;
        color: #666;
        margin-bottom: 4px;
        display: block;
      }
      
      .item-value {
        font-size: 15px;
        color: #333;
        font-weight: 500;
      }
    }
  }
}

.fee-details-card {
  .details-title {
    font-size: 15px;
    font-weight: bold;
    color: #333;
    margin-bottom: 10px;
  }
  
  .table-header {
    display: flex;
    background-color: #f5f5f5;
    padding: 10px 0;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    
    .header-cell {
      font-size: 13px;
      color: #666;
      font-weight: 500;
      text-align: center;
    }
  }
  
  .table-content {
    max-height: 300px;
    
    .table-row {
      display: flex;
      padding: 10px 0;
      border-bottom: 1px solid #f0f0f0;
      
      &.even-row {
        background-color: #fafafa;
      }
      
      .row-cell {
        font-size: 13px;
        color: #333;
        text-align: center;
      }
    }
  }
  
  .header-cell, .row-cell {
    &.date { width: 15%; }
    &.stock { width: 25%; }
    &.direction { width: 15%; }
    &.price { width: 15%; }
    &.volume { width: 15%; }
    &.fee { width: 15%; }
  }
}

.buy-text {
  color: #f56c6c;
}

.sell-text {
  color: #67c23a;
}

.fee-text {
  color: #e6a23c;
}

.positive-amount {
  color: #67c23a;
}

.negative-amount {
  color: #f56c6c;
}

.empty-data {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 40px 0;
  
  .empty-text {
    font-size: 14px;
    color: #999;
  }
}

.trade-detail-popup {
  background-color: #fff;
  border-radius: 10px;
  width: 80vw;
  max-width: 600px;
  padding: 15px;
  
  .popup-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
    
    .popup-title {
      font-size: 16px;
      font-weight: bold;
      color: #333;
    }
    
    .close-btn {
      font-size: 22px;
      color: #999;
      padding: 5px;
    }
  }
  
  .popup-content {
    .detail-row {
      display: flex;
      justify-content: space-between;
      margin-bottom: 10px;
      
      .detail-label {
        font-size: 14px;
        color: #666;
      }
      
      .detail-value {
        font-size: 14px;
        color: #333;
        font-weight: 500;
      }
    }
    
    .divider {
      height: 1px;
      background-color: #f0f0f0;
      margin: 10px 0;
    }
  }
}
</style> 
