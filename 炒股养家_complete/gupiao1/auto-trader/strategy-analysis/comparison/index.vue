<template>
    <view class="container">
        <view class="header">
            <text class="title">策略效果对比</text>
            <text class="subtitle">多种交易策略的绩效分析与对比</text>
        </view>
        
        <!-- 策略概览 -->
        <view class="section">
            <view class="section-header">
                <text class="section-title">策略概览</text>
                <picker @change="changePeriod" :value="periodIndex" :range="periods">
                    <view class="picker">{{ periods[periodIndex] }}</view>
                </picker>
            </view>
            
            <view class="strategy-overview">
                <view class="strategy-card" v-for="(strategy, index) in strategies" :key="index" @click="selectStrategy(index)">
                    <view class="strategy-header">
                        <text class="strategy-name">{{ strategy.name }}</text>
                        <text :class="['strategy-return', strategy.return >= 0 ? 'profit' : 'loss']">
                            {{ strategy.return >= 0 ? '+' : '' }}{{ strategy.return }}%
                        </text>
                    </view>
                    <view class="progress-container">
                        <progress class="strategy-progress" :percent="getProgressPercent(strategy.return)" :activeColor="getReturnColor(strategy.return)" backgroundColor="#f0f0f0" stroke-width="4"></progress>
                    </view>
                    <view class="strategy-metrics">
                        <view class="metric-item">
                            <text class="metric-label">胜率</text>
                            <text class="metric-value">{{ strategy.winRate }}%</text>
                        </view>
                        <view class="metric-item">
                            <text class="metric-label">最大回撤</text>
                            <text class="metric-value">{{ strategy.maxDrawdown }}%</text>
                        </view>
                        <view class="metric-item">
                            <text class="metric-label">夏普比率</text>
                            <text class="metric-value">{{ strategy.sharpeRatio }}</text>
                        </view>
                    </view>
                </view>
            </view>
        </view>
        
        <!-- 策略详细对比 -->
        <view class="section">
            <view class="section-header">
                <text class="section-title">详细对比</text>
                <text class="refresh-btn" @click="refreshComparison">刷新</text>
            </view>
            
            <view class="comparison-chart">
                <canvas canvas-id="performanceChart" class="chart-canvas" :canvas-width="300" :canvas-height="200"></canvas>
            </view>
            
            <view class="chart-legend">
                <view class="legend-item" v-for="(strategy, index) in strategies" :key="index" @click="toggleStrategyVisibility(index)">
                    <view class="legend-color" :style="{backgroundColor: strategyColors[index]}"></view>
                    <text class="legend-name" :class="{disabled: !strategy.visible}">{{ strategy.name }}</text>
                </view>
            </view>
        </view>
        
        <!-- 策略详情 -->
        <view class="section" v-if="selectedStrategy !== null">
            <view class="section-header">
                <text class="section-title">{{ strategies[selectedStrategy].name }} 详情</text>
            </view>
            
            <view class="strategy-details">
                <view class="detail-row">
                    <text class="detail-label">策略描述</text>
                    <text class="detail-value">{{ strategies[selectedStrategy].description }}</text>
                </view>
                
                <view class="detail-row">
                    <text class="detail-label">适用市场</text>
                    <text class="detail-value">{{ strategies[selectedStrategy].suitableMarket }}</text>
                </view>
                
                <view class="detail-row">
                    <text class="detail-label">风险等级</text>
                    <view class="risk-level">
                        <view class="risk-dot" v-for="i in 5" :key="i" :class="{active: i <= strategies[selectedStrategy].riskLevel}"></view>
                    </view>
                </view>
                
                <view class="detail-row">
                    <text class="detail-label">交易频率</text>
                    <text class="detail-value">{{ getFrequencyText(strategies[selectedStrategy].frequency) }}</text>
                </view>
                
                <view class="detail-row">
                    <text class="detail-label">历史交易</text>
                    <text class="detail-value">{{ strategies[selectedStrategy].tradingHistory }} 笔</text>
                </view>
            </view>
            
            <!-- 月度表现 -->
            <view class="monthly-performance">
                <text class="monthly-title">月度表现</text>
                <view class="monthly-chart">
                    <canvas canvas-id="monthlyChart" class="chart-canvas" :canvas-width="300" :canvas-height="150"></canvas>
                </view>
            </view>
        </view>
        
        <!-- 策略参数设置 -->
        <view class="section" v-if="selectedStrategy !== null">
            <view class="section-header">
                <text class="section-title">参数设置</text>
            </view>
            
            <view class="params-form">
                <view class="param-item" v-for="(param, index) in strategies[selectedStrategy].parameters" :key="index">
                    <text class="param-label">{{ param.name }}</text>
                    <view class="param-input">
                        <slider :value="param.value" :min="param.min" :max="param.max" :step="param.step" @change="updateParam(index, $event)" show-value></slider>
                    </view>
                </view>
                
                <button class="apply-btn" @click="applyParameters">应用参数</button>
            </view>
        </view>
    </view>
</template>

<script>
export default {
    data() {
        return {
            // 时间周期
            periods: ['近一月', '近三月', '近半年', '近一年'],
            periodIndex: 2,
            
            // 选中的策略
            selectedStrategy: null,
            
            // 策略颜色
            strategyColors: ['#f5222d', '#1989fa', '#52c41a', '#faad14', '#722ed1'],
            
            // 策略数据
            strategies: [
                {
                    name: '动量策略',
                    return: 12.5,
                    winRate: 68,
                    maxDrawdown: 8.3,
                    sharpeRatio: 1.8,
                    description: '基于价格动量的趋势跟踪策略,通过捕捉股票价格的持续上涨或下跌趋势获利。',
                    suitableMarket: '趋势明显的单边市场',
                    riskLevel: 3,
                    frequency: 'medium',
                    tradingHistory: 156,
                    visible: true,
                    parameters: [
                        {
                            name: '动量周期(天)',
                            value: 20,
                            min: 5,
                            max: 60,
                            step: 1
                        },
                        {
                            name: '信号阈值(%)',
                            value: 5,
                            min: 1,
                            max: 10,
                            step: 0.5
                        },
                        {
                            name: '止损比例(%)',
                            value: 7,
                            min: 3,
                            max: 15,
                            step: 1
                        }
                    ],
                    performanceData: [0, 2.3, 4.1, 3.8, 5.2, 7.5, 6.8, 9.2, 10.5, 9.8, 11.2, 12.5]
                },
                {
                    name: '均值回归',
                    return: 8.2,
                    winRate: 72,
                    maxDrawdown: 5.6,
                    sharpeRatio: 1.5,
                    description: '基于价格均值回归原理的策略,当价格偏离均值过大时进行反向操作。',
                    suitableMarket: '震荡市场',
                    riskLevel: 2,
                    frequency: 'high',
                    tradingHistory: 235,
                    visible: true,
                    parameters: [
                        {
                            name: '均值周期(天)',
                            value: 30,
                            min: 10,
                            max: 60,
                            step: 1
                        },
                        {
                            name: '偏离阈值(%)',
                            value: 8,
                            min: 3,
                            max: 15,
                            step: 0.5
                        },
                        {
                            name: '持仓周期(天)',
                            value: 5,
                            min: 1,
                            max: 20,
                            step: 1
                        }
                    ],
                    performanceData: [0, 1.5, 2.8, 2.2, 3.6, 4.5, 5.1, 4.8, 6.2, 7.0, 7.5, 8.2]
                },
                {
                    name: '区块链监控',
                    return: 15.1,
                    winRate: 65,
                    maxDrawdown: 12.5,
                    sharpeRatio: 2.1,
                    description: '通过监控区块链交易数据和网络活跃度,捕捉加密货币市场的投资机会。',
                    suitableMarket: '数字货币市场',
                    riskLevel: 5,
                    frequency: 'high',
                    tradingHistory: 98,
                    visible: true,
                    parameters: [
                        {
                            name: '监控周期(小时)',
                            value: 12,
                            min: 1,
                            max: 48,
                            step: 1
                        },
                        {
                            name: '活跃度阈值',
                            value: 65,
                            min: 30,
                            max: 90,
                            step: 5
                        },
                        {
                            name: '止盈比例(%)',
                            value: 20,
                            min: 5,
                            max: 50,
                            step: 5
                        }
                    ],
                    performanceData: [0, 3.5, 2.8, 5.2, 7.6, 6.5, 9.1, 10.8, 12.2, 11.5, 13.8, 15.1]
                },
                {
                    name: '价值投资',
                    return: 6.8,
                    winRate: 80,
                    maxDrawdown: 4.2,
                    sharpeRatio: 1.2,
                    description: '基于企业基本面分析的长期投资策略,寻找被低估的优质企业进行投资。',
                    suitableMarket: '价值型市场',
                    riskLevel: 1,
                    frequency: 'low',
                    tradingHistory: 42,
                    visible: true,
                    parameters: [
                        {
                            name: 'PE阈值',
                            value: 15,
                            min: 5,
                            max: 30,
                            step: 1
                        },
                        {
                            name: 'PB阈值',
                            value: 1.5,
                            min: 0.5,
                            max: 3,
                            step: 0.1
                        },
                        {
                            name: '持有周期(月)',
                            value: 6,
                            min: 1,
                            max: 12,
                            step: 1
                        }
                    ],
                    performanceData: [0, 0.8, 1.5, 2.2, 2.8, 3.5, 4.1, 4.8, 5.2, 5.8, 6.3, 6.8]
                }
            ]
        }
    },
    methods: {
        // 切换时间周期
        changePeriod(e) {
            this.periodIndex = e.detail.value
            this.refreshComparison()
        },
        
        // 选择策略
        selectStrategy(index) {
            this.selectedStrategy = index
            
            // 绘制月度表现图表
            setTimeout(() => {
                this.drawMonthlyChart()
            }, 300)
        },
        
        // 获取进度条百分比
        getProgressPercent(returnValue) {
            // 将收益率映射到0-100的范围,最大考虑20%收益
            const percent = (returnValue + 10) * 5
            return Math.min(Math.max(percent, 0), 100)
        },
        
        // 获取收益率颜色
        getReturnColor(returnValue) {
            if (returnValue >= 10) return '#f5222d'
            if (returnValue >= 5) return '#fa8c16'
            if (returnValue >= 0) return '#52c41a'
            return '#1989fa'
        },
        
        // 获取交易频率文本
        getFrequencyText(frequency) {
            const frequencies = {
                'low': '低频(每月数次)',
                'medium': '中频(每周数次)',
                'high': '高频(每日多次)'
            }
            return frequencies[frequency] || '未知'
        },
        
        // 刷新对比
        refreshComparison() {
            // 根据选择的时间周期调整数据
            const periodFactors = [0.3, 0.6, 1.0, 1.8]
            const factor = periodFactors[this.periodIndex]
            
            // 模拟更新数据
            this.strategies.forEach(strategy => {
                strategy.return = (Math.random() * 10 + 5) * factor
                strategy.return = parseFloat(strategy.return.toFixed(1))
                strategy.winRate = Math.floor(Math.random() * 20) + 60
                strategy.maxDrawdown = parseFloat((Math.random() * 8 + 3).toFixed(1))
                strategy.sharpeRatio = parseFloat((Math.random() * 1.5 + 0.8).toFixed(1))
                
                // 生成新的绩效数据
                const newData = [0]
                let lastValue = 0
                for (let i = 1; i < 12; i++) {
                    const change = (Math.random() * 3 - 0.5) * factor
                    lastValue += change
                    newData.push(parseFloat(lastValue.toFixed(1)))
                }
                // 确保最后一个值等于总收益率
                newData[11] = strategy.return
                strategy.performanceData = newData
            })
            
            // 重新绘制图表
            this.drawPerformanceChart()
            
            uni.showToast({
                title: '数据已更新',
                icon: 'success'
            })
        },
        
        // 切换策略可见性
        toggleStrategyVisibility(index) {
            this.strategies[index].visible = !this.strategies[index].visible
            this.drawPerformanceChart()
        },
        
        // 更新策略参数
        updateParam(paramIndex, event) {
            const strategyIndex = this.selectedStrategy
            this.strategies[strategyIndex].parameters[paramIndex].value = event.detail.value
        },
        
        // 应用参数
        applyParameters() {
            // 模拟参数应用效果
            const strategyIndex = this.selectedStrategy
            
            // 随机调整收益率,模拟参数变化效果
            const changePercent = (Math.random() * 6 - 3) / 100
            const originalReturn = this.strategies[strategyIndex].return
            const newReturn = originalReturn * (1 + changePercent)
            this.strategies[strategyIndex].return = parseFloat(newReturn.toFixed(1))
            
            // 更新绩效数据
            const factor = newReturn / originalReturn
            this.strategies[strategyIndex].performanceData = this.strategies[strategyIndex].performanceData.map(
                (value, index) => index === 0 ? 0 : parseFloat((value * factor).toFixed(1))
            )
            
            // 重新绘制图表
            this.drawPerformanceChart()
            this.drawMonthlyChart()
            
            uni.showToast({
                title: '参数已应用',
                icon: 'success'
            })
        },
        
        // 绘制绩效对比图表
        drawPerformanceChart() {
            const ctx = uni.createCanvasContext('performanceChart', this)
            
            // 设置willReadFrequently属性
            ctx.willReadFrequently = true
            
            const width = 300
            const height = 200
            
            // 清空画布
            ctx.clearRect(0, 0, width, height)
            
            // 绘制背景
            ctx.setFillStyle('#f8f8f8')
            ctx.fillRect(0, 0, width, height)
            
            // 绘制坐标轴
            ctx.beginPath()
            ctx.setStrokeStyle('#ddd')
            ctx.setLineWidth(1)
            
            // X轴
            ctx.moveTo(40, height - 30)
            ctx.lineTo(width - 20, height - 30)
            
            // Y轴
            ctx.moveTo(40, 20)
            ctx.lineTo(40, height - 30)
            ctx.stroke()
            
            // 绘制网格线
            ctx.beginPath()
            ctx.setStrokeStyle('#f0f0f0')
            ctx.setLineWidth(1)
            
            // 水平网格线
            for (let i = 1; i <= 5; i++) {
                const y = 20 + (i - 1) * ((height - 50) / 5)
                ctx.moveTo(40, y)
                ctx.lineTo(width - 20, y)
            }
            
            // 垂直网格线
            for (let i = 1; i <= 6; i++) {
                const x = 40 + i * ((width - 60) / 6)
                ctx.moveTo(x, 20)
                ctx.lineTo(x, height - 30)
            }
            ctx.stroke()
            
            // 绘制X轴标签
            ctx.setFillStyle('#999')
            ctx.setFontSize(10)
            const months = ['1月', '3月', '6月', '9月', '12月']
            for (let i = 0; i < months.length; i++) {
                const x = 40 + (i + 1) * ((width - 60) / 6)
                ctx.fillText(months[i], x - 10, height - 15)
            }
            
            // 找出最大收益率,用于缩放Y轴
            let maxReturn = 0
            this.strategies.forEach(strategy => {
                if (strategy.visible) {
                    const strategyMax = Math.max(...strategy.performanceData)
                    maxReturn = Math.max(maxReturn, strategyMax)
                }
            })
            maxReturn = Math.ceil(maxReturn / 5) * 5 // 向上取整到5的倍数
            
            // 绘制Y轴标签
            for (let i = 0; i <= 5; i++) {
                const y = height - 30 - i * ((height - 50) / 5)
                const value = (i * maxReturn / 5).toFixed(0) + '%'
                ctx.fillText(value, 5, y + 3)
            }
            
            // 绘制每个策略的曲线
            this.strategies.forEach((strategy, index) => {
                if (!strategy.visible) return
                
                ctx.beginPath()
                ctx.setStrokeStyle(this.strategyColors[index])
                ctx.setLineWidth(2)
                
                const dataPoints = strategy.performanceData
                const xStep = (width - 60) / (dataPoints.length - 1)
                
                for (let i = 0; i < dataPoints.length; i++) {
                    const x = 40 + i * xStep
                    const y = height - 30 - (dataPoints[i] / maxReturn) * (height - 50)
                    
                    if (i === 0) {
                        ctx.moveTo(x, y)
                    } else {
                        ctx.lineTo(x, y)
                    }
                }
                ctx.stroke()
            })
            
            // 绘制图表标题
            ctx.setFillStyle('#333')
            ctx.setFontSize(12)
            ctx.fillText('策略收益率对比 (%)', width / 2 - 50, 15)
            
            // 提交绘制
            ctx.draw()
        },
        
        // 绘制月度表现图表
        drawMonthlyChart() {
            if (this.selectedStrategy === null) return
            
            const ctx = uni.createCanvasContext('monthlyChart', this)
            
            // 设置willReadFrequently属性
            ctx.willReadFrequently = true
            
            const width = 300
            const height = 150
            
            // 清空画布
            ctx.clearRect(0, 0, width, height)
            
            // 绘制背景
            ctx.setFillStyle('#f8f8f8')
            ctx.fillRect(0, 0, width, height)
            
            // 生成月度数据 (模拟)
            const monthlyData = []
            for (let i = 0; i < 12; i++) {
                monthlyData.push((Math.random() * 6 - 2).toFixed(1))
            }
            
            // 绘制柱状图
            const barWidth = 16
            const spacing = 8
            const startX = 40
            
            for (let i = 0; i < 12; i++) {
                const value = parseFloat(monthlyData[i])
                const x = startX + i * (barWidth + spacing)
                
                // 确定柱子高度和位置
                const barHeight = Math.abs(value) * 10
                const y = value >= 0 ? height - 30 - barHeight : height - 30
                
                // 设置颜色
                ctx.setFillStyle(value >= 0 ? '#f5222d' : '#52c41a')
                
                // 绘制柱子
                ctx.fillRect(x, y, barWidth, barHeight)
                
                // 绘制数值
                ctx.setFillStyle('#333')
                ctx.setFontSize(9)
                ctx.fillText(value + '%', x, value >= 0 ? y - 5 : y + barHeight + 10)
            }
            
            // 绘制X轴
            ctx.beginPath()
            ctx.setStrokeStyle('#ddd')
            ctx.setLineWidth(1)
            ctx.moveTo(30, height - 30)
            ctx.lineTo(width - 10, height - 30)
            ctx.stroke()
            
            // 绘制月份标签
            ctx.setFillStyle('#999')
            ctx.setFontSize(9)
            const months = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']
            
            for (let i = 0; i < 12; i++) {
                const x = startX + i * (barWidth + spacing) + barWidth / 2 - 5
                ctx.fillText(months[i], x, height - 15)
            }
            
            // 绘制图表标题
            ctx.setFillStyle('#333')
            ctx.setFontSize(12)
            ctx.fillText('月度收益率 (%)', width / 2 - 40, 15)
            
            // 提交绘制
            ctx.draw()
        }
    },
    onLoad() {
        // 初始化绘制图表
        setTimeout(() => {
            this.drawPerformanceChart();
        }, 300);
    }
}
</script>

<style>
.container {
    padding: 30rpx;
    background-color: #f5f5f5;
}

.header {
    margin-bottom: 40rpx;
    padding: 20rpx;
    background: linear-gradient(135deg, #1989fa, #0056b3);
    border-radius: 16rpx;
    color: #fff;
    box-shadow: 0 4rpx 12rpx rgba(25, 137, 250, 0.3);
}

.title {
    font-size: 40rpx;
    font-weight: bold;
    margin-bottom: 10rpx;
    display: block;
}

.subtitle {
    font-size: 24rpx;
    opacity: 0.9;
    display: block;
}

.section {
    margin-bottom: 30rpx;
    background-color: #fff;
    border-radius: 16rpx;
    padding: 24rpx;
    box-shadow: 0 2rpx 10rpx rgba(0,0,0,0.05);
}

.section-header {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20rpx;
    border-bottom: 1px solid #f0f0f0;
    padding-bottom: 16rpx;
}

.section-title {
    font-size: 32rpx;
    font-weight: bold;
    color: #333;
}

.picker, .refresh-btn {
    font-size: 24rpx;
    color: #1989fa;
    background-color: rgba(25, 137, 250, 0.1);
    padding: 6rpx 16rpx;
    border-radius: 30rpx;
}

/* 策略概览样式 */
.strategy-overview {
    display: flex;
    flex-direction: row;
    flex-wrap: wrap;
    justify-content: space-between;
}

.strategy-card {
    width: 48%;
    background-color: #f9f9f9;
    border-radius: 12rpx;
    padding: 20rpx;
    margin-bottom: 20rpx;
    box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.03);
}

.strategy-header {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15rpx;
}

.strategy-name {
    font-size: 28rpx;
    font-weight: bold;
    color: #333;
}

.strategy-return {
    font-size: 30rpx;
    font-weight: bold;
}

.progress-container {
    margin-bottom: 15rpx;
}

.strategy-progress {
    width: 100%;
    height: 8rpx;
    border-radius: 4rpx;
}

.strategy-metrics {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
}

.metric-item {
    flex: 1;
    align-items: center;
    text-align: center;
}

.metric-label {
    font-size: 22rpx;
    color: #666;
    margin-bottom: 5rpx;
    display: block;
}

.metric-value {
    font-size: 26rpx;
    font-weight: bold;
    color: #333;
    display: block;
}

.profit {
    color: #f5222d;
}

.loss {
    color: #52c41a;
}

/* 对比图表样式 */
.comparison-chart {
    height: 200px;
    margin-bottom: 20rpx;
    background-color: #f9f9f9;
    border-radius: 12rpx;
    padding: 10rpx;
}

.chart-canvas {
    width: 100%;
    height: 100%;
}

.chart-legend {
    display: flex;
    flex-direction: row;
    flex-wrap: wrap;
    justify-content: center;
    padding: 16rpx 0;
    background-color: #f9f9f9;
    border-radius: 8rpx;
}

.legend-item {
    display: flex;
    flex-direction: row;
    align-items: center;
    margin: 0 15rpx;
    padding: 8rpx 12rpx;
    background-color: #fff;
    border-radius: 30rpx;
}

.legend-color {
    width: 16rpx;
    height: 16rpx;
    border-radius: 8rpx;
    margin-right: 8rpx;
}

.legend-name {
    font-size: 22rpx;
    color: #333;
}

.legend-name.disabled {
    color: #999;
    text-decoration: line-through;
}

/* 策略详情样式 */
.strategy-details {
    margin-bottom: 20rpx;
    background-color: #f9f9f9;
    border-radius: 12rpx;
    padding: 20rpx;
}

.detail-row {
    display: flex;
    flex-direction: row;
    margin-bottom: 15rpx;
    padding-bottom: 10rpx;
    border-bottom: 1px solid #f0f0f0;
}

.detail-row:last-child {
    border-bottom: none;
    margin-bottom: 0;
    padding-bottom: 0;
}

.detail-label {
    width: 160rpx;
    font-size: 26rpx;
    color: #666;
}

.detail-value {
    flex: 1;
    font-size: 26rpx;
    color: #333;
    line-height: 1.5;
}

.risk-level {
    display: flex;
    flex-direction: row;
    align-items: center;
}

.risk-dot {
    width: 20rpx;
    height: 20rpx;
    border-radius: 10rpx;
    background-color: #f0f0f0;
    margin-right: 10rpx;
}

.risk-dot.active {
    background-color: #f5222d;
}

.monthly-performance {
    margin-top: 30rpx;
}

.monthly-title {
    font-size: 28rpx;
    font-weight: bold;
    margin-bottom: 15rpx;
    color: #333;
    padding-bottom: 10rpx;
    border-bottom: 1px solid #f0f0f0;
}

.monthly-chart {
    height: 150px;
    background-color: #f9f9f9;
    border-radius: 12rpx;
    padding: 10rpx;
}

/* 策略参数设置样式 */
.params-form {
    padding: 16rpx;
    background-color: #f9f9f9;
    border-radius: 12rpx;
}

.param-item {
    margin-bottom: 24rpx;
}

.param-label {
    font-size: 26rpx;
    color: #333;
    margin-bottom: 12rpx;
    display: block;
}

.param-input {
    padding: 0 10rpx;
}

.apply-btn {
    margin-top: 30rpx;
    background: linear-gradient(135deg, #1989fa, #0056b3);
    color: white;
    font-size: 28rpx;
    border-radius: 8rpx;
    padding: 16rpx 0;
}
</style> 
