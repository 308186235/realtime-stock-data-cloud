<template>
    <view class="container">
        <view class="header">
            <text class="title">交易设置</text>
            <text class="subtitle">自定义您的交易参数和风控规则</text>
        </view>
        
        <!-- 交易参数设置 -->
        <view class="section">
            <view class="section-header">
                <text class="section-title">交易参数</text>
            </view>
            
            <view class="form-group">
                <view class="form-item">
                    <text class="label">单笔最大交易额</text>
                    <view class="input-with-unit">
                        <input type="digit" v-model="maxTradeAmount" class="input" />
                        <text class="unit">元</text>
                    </view>
                </view>
                
                <view class="form-item">
                    <text class="label">默认买入数量</text>
                    <view class="input-with-unit">
                        <input type="number" v-model="defaultBuyQuantity" class="input" />
                        <text class="unit">股</text>
                    </view>
                </view>
                
                <view class="form-item">
                    <text class="label">委托价格偏好</text>
                    <picker @change="changePricePreference" :value="pricePreferenceIndex" :range="pricePreferences">
                        <view class="picker">
                            {{ pricePreferences[pricePreferenceIndex] }}
                        </view>
                    </picker>
                </view>
                
                <view class="form-item">
                    <text class="label">交易确认</text>
                    <switch :checked="confirmBeforeTrade" @change="toggleConfirmBeforeTrade" color="#1989fa" />
                </view>
            </view>
        </view>
        
        <!-- 风险控制设置 -->
        <view class="section">
            <view class="section-header">
                <text class="section-title">风险控制</text>
            </view>
            
            <view class="form-group">
                <view class="form-item">
                    <text class="label">单股持仓上限</text>
                    <view class="input-with-unit">
                        <input type="digit" v-model="maxPositionPerStock" class="input" />
                        <text class="unit">%</text>
                    </view>
                </view>
                
                <view class="form-item">
                    <text class="label">止损阈值</text>
                    <view class="input-with-unit">
                        <input type="digit" v-model="stopLossThreshold" class="input" />
                        <text class="unit">%</text>
                    </view>
                </view>
                
                <view class="form-item">
                    <text class="label">止盈阈值</text>
                    <view class="input-with-unit">
                        <input type="digit" v-model="takeProfitThreshold" class="input" />
                        <text class="unit">%</text>
                    </view>
                </view>
                
                <view class="form-item">
                    <text class="label">自动止损</text>
                    <switch :checked="autoStopLoss" @change="toggleAutoStopLoss" color="#1989fa" />
                </view>
                
                <view class="form-item">
                    <text class="label">自动止盈</text>
                    <switch :checked="autoTakeProfit" @change="toggleAutoTakeProfit" color="#1989fa" />
                </view>
            </view>
        </view>
        
        <!-- 通知设置 -->
        <view class="section">
            <view class="section-header">
                <text class="section-title">通知设置</text>
            </view>
            
            <view class="form-group">
                <view class="form-item">
                    <text class="label">交易执行通知</text>
                    <switch :checked="tradeNotifications" @change="toggleTradeNotifications" color="#1989fa" />
                </view>
                
                <view class="form-item">
                    <text class="label">价格预警通知</text>
                    <switch :checked="priceAlerts" @change="togglePriceAlerts" color="#1989fa" />
                </view>
                
                <view class="form-item">
                    <text class="label">风险预警通知</text>
                    <switch :checked="riskAlerts" @change="toggleRiskAlerts" color="#1989fa" />
                </view>
            </view>
        </view>
        
        <!-- 保存按钮 -->
        <view class="action-buttons">
            <button class="save-btn" @click="saveSettings">保存设置</button>
            <button class="reset-btn" @click="resetSettings">重置默认</button>
        </view>
    </view>
</template>

<script>
export default {
    data() {
        return {
            // 交易参数
            maxTradeAmount: '10000',
            defaultBuyQuantity: '100',
            pricePreferences: ['市价委托', '限价委托', '最优五档'],
            pricePreferenceIndex: 0,
            confirmBeforeTrade: true,
            
            // 风险控制
            maxPositionPerStock: '20',
            stopLossThreshold: '5',
            takeProfitThreshold: '15',
            autoStopLoss: true,
            autoTakeProfit: true,
            
            // 通知设置
            tradeNotifications: true,
            priceAlerts: true,
            riskAlerts: true
        }
    },
    methods: {
        // 交易参数方法
        changePricePreference(e) {
            this.pricePreferenceIndex = e.detail.value
        },
        
        toggleConfirmBeforeTrade(e) {
            this.confirmBeforeTrade = e.detail.value
        },
        
        // 风险控制方法
        toggleAutoStopLoss(e) {
            this.autoStopLoss = e.detail.value
        },
        
        toggleAutoTakeProfit(e) {
            this.autoTakeProfit = e.detail.value
        },
        
        // 通知设置方法
        toggleTradeNotifications(e) {
            this.tradeNotifications = e.detail.value
        },
        
        togglePriceAlerts(e) {
            this.priceAlerts = e.detail.value
        },
        
        toggleRiskAlerts(e) {
            this.riskAlerts = e.detail.value
        },
        
        // 保存设置
        saveSettings() {
            // 保存到本地存储
            uni.setStorageSync('tradeSettings', {
                maxTradeAmount: this.maxTradeAmount,
                defaultBuyQuantity: this.defaultBuyQuantity,
                pricePreferenceIndex: this.pricePreferenceIndex,
                confirmBeforeTrade: this.confirmBeforeTrade,
                maxPositionPerStock: this.maxPositionPerStock,
                stopLossThreshold: this.stopLossThreshold,
                takeProfitThreshold: this.takeProfitThreshold,
                autoStopLoss: this.autoStopLoss,
                autoTakeProfit: this.autoTakeProfit,
                tradeNotifications: this.tradeNotifications,
                priceAlerts: this.priceAlerts,
                riskAlerts: this.riskAlerts
            })
            
            // 显示成功提示
            uni.showToast({
                title: '设置已保存',
                icon: 'success'
            })
        },
        
        // 重置默认设置
        resetSettings() {
            uni.showModal({
                title: '确认重置',
                content: '确定要将所有设置恢复为默认值吗?',
                success: (res) => {
                    if (res.confirm) {
                        // 重置为默认值
                        this.maxTradeAmount = '10000'
                        this.defaultBuyQuantity = '100'
                        this.pricePreferenceIndex = 0
                        this.confirmBeforeTrade = true
                        this.maxPositionPerStock = '20'
                        this.stopLossThreshold = '5'
                        this.takeProfitThreshold = '15'
                        this.autoStopLoss = true
                        this.autoTakeProfit = true
                        this.tradeNotifications = true
                        this.priceAlerts = true
                        this.riskAlerts = true
                        
                        // 显示成功提示
                        uni.showToast({
                            title: '已重置为默认设置',
                            icon: 'success'
                        })
                    }
                }
            })
        }
    },
    onLoad() {
        // 从本地存储加载设置
        const savedSettings = uni.getStorageSync('tradeSettings')
        if (savedSettings) {
            Object.keys(savedSettings).forEach(key => {
                if (this[key] !== undefined) {
                    this[key] = savedSettings[key]
                }
            })
        }
    }
}
</script>

<style>
.container {
    padding: 30rpx;
}

.header {
    margin-bottom: 40rpx;
}

.title {
    font-size: 36rpx;
    font-weight: bold;
    margin-bottom: 10rpx;
}

.subtitle {
    font-size: 24rpx;
    color: #666;
}

.section {
    margin-bottom: 30rpx;
    background-color: #fff;
    border-radius: 12rpx;
    padding: 20rpx;
    box-shadow: 0 2rpx 10rpx rgba(0,0,0,0.05);
}

.section-header {
    padding-bottom: 15rpx;
    border-bottom: 1rpx solid #f0f0f0;
    margin-bottom: 20rpx;
}

.section-title {
    font-size: 28rpx;
    font-weight: bold;
}

.form-group {
    padding: 10rpx 0;
}

.form-item {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
    padding: 20rpx 0;
    border-bottom: 1rpx solid #f5f5f5;
}

.form-item:last-child {
    border-bottom: none;
}

.label {
    font-size: 28rpx;
    color: #333;
}

.input-with-unit {
    display: flex;
    flex-direction: row;
    align-items: center;
    width: 200rpx;
}

.input {
    flex: 1;
    text-align: right;
    height: 60rpx;
    font-size: 28rpx;
}

.unit {
    margin-left: 10rpx;
    color: #666;
    font-size: 24rpx;
}

.picker {
    font-size: 28rpx;
    color: #1989fa;
    text-align: right;
    width: 200rpx;
}

.action-buttons {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    margin-top: 40rpx;
    margin-bottom: 60rpx;
}

.save-btn {
    flex: 1;
    margin: 0 10rpx;
    background-color: #1989fa;
    color: white;
    font-size: 28rpx;
}

.reset-btn {
    flex: 1;
    margin: 0 10rpx;
    background-color: #f8f8f8;
    color: #333;
    font-size: 28rpx;
    border: 1rpx solid #ddd;
}
</style> 
