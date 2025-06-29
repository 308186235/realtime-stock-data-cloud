<template>
    <view class="container">
        <view class="header">
            <view class="back-button" @click="navigateBack">
                <text class="back-icon">&#xe607;</text>
            </view>
            <text class="title">涨停双阴买入法</text>
        </view>
        
        <view class="strategy-description card">
            <text class="section-title">策略说明</text>
            <text class="description-text">涨停双阴买入法是一种适用于股票市场的交易策略,主要识别涨停后连续两个阴线的形态,这通常预示着主力机构在洗盘后可能有较大概率的上涨行情。</text>
            
            <view class="formula-box">
                <text class="formula-title">策略公式</text>
                <view class="formula-content">
                    <text class="formula-line">升势 = MAX(C, 10) > REF(MAX(C, 10), 1)</text>
                    <text class="formula-line">阴K = C > REF(C, 1) * 1.01</text>
                    <text class="formula-line">双阴 = COUNT(C < REF(C, 1), 2) > 2</text>
                    <text class="formula-line">强势 = MAX(C, 0) < REF(MIN(C, 0), 1)</text>
                    <text class="formula-line">缩量 = V < REF(V, 1) * REF(V, 2)</text>
                    <text class="formula-line highlight">NG: 升势 AND 双阴 AND 强势 AND 缩量 AND NOT(阴K)</text>
                </view>
            </view>
        </view>
        
        <view class="strategy-logic card">
            <text class="section-title">策略逻辑</text>
            <view class="logic-step">
                <text class="step-number">1</text>
                <text class="step-description">识别涨停信号:股票出现涨停或接近涨停的大阳线</text>
            </view>
            <view class="logic-step">
                <text class="step-number">2</text>
                <text class="step-description">确认双阴形态:涨停后连续出现两个阴线</text>
            </view>
            <view class="logic-step">
                <text class="step-number">3</text>
                <text class="step-description">验证缩量条件:双阴期间成交量逐步减少</text>
            </view>
            <view class="logic-step">
                <text class="step-number">4</text>
                <text class="step-description">检查强势标志:双阴期间股价未跌破重要支撑位</text>
            </view>
            <view class="logic-step">
                <text class="step-number">5</text>
                <text class="step-description">确认买入时机:满足以上所有条件后可考虑买入</text>
            </view>
        </view>
        
        <view class="pattern-visual card">
            <text class="section-title">形态示意图</text>
            <view class="chart-placeholder">
                <image class="pattern-image" src="/static/images/limit-up-double-negative.png" mode="aspectFit"></image>
            </view>
            <text class="pattern-desc">涨停双阴买入法典型形态图示</text>
        </view>
        
        <view class="advantage-risks card">
            <text class="section-title">优势与风险</text>
            <view class="list-container">
                <text class="list-title advantage">优势场景</text>
                <view class="list-item" v-for="(item, index) in advantageousScenarios" :key="'adv-'+index">
                    <text class="item-icon advantage">✓</text>
                    <text class="item-text">{{item}}</text>
                </view>
            </view>
            
            <view class="list-container">
                <text class="list-title risk">风险提示</text>
                <view class="list-item" v-for="(item, index) in riskWarnings" :key="'risk-'+index">
                    <text class="item-icon risk">!</text>
                    <text class="item-text">{{item}}</text>
                </view>
            </view>
        </view>
        
        <view class="source-code card">
            <text class="section-title">策略源码</text>
            <view class="code-block">
                <text class="code-line">// 涨停双阴买入法公式</text>
                <text class="code-line">升势 = MAX(C, 10) > REF(MAX(C, 10), 1);</text>
                <text class="code-line">阴K = C > REF(C, 1) * 1.01;</text>
                <text class="code-line">双阴 = COUNT(C < REF(C, 1), 2) > 2;</text>
                <text class="code-line">强势 = MAX(C, 0) < REF(MIN(C, 0), 1);</text>
                <text class="code-line">缩量 = V < REF(V, 1) * REF(V, 2);</text>
                <text class="code-line">NG = 升势 AND 双阴 AND 强势 AND 缩量 AND NOT(阴K);</text>
            </view>
        </view>
        
        <view class="back-test-results card">
            <text class="section-title">回测结果</text>
            <view class="result-item">
                <text class="result-label">年化收益率</text>
                <text class="result-value success">+18.5%</text>
            </view>
            <view class="result-item">
                <text class="result-label">胜率</text>
                <text class="result-value">65.2%</text>
            </view>
            <view class="result-item">
                <text class="result-label">夏普比率</text>
                <text class="result-value">1.36</text>
            </view>
            <view class="result-item">
                <text class="result-label">最大回撤</text>
                <text class="result-value danger">-12.3%</text>
            </view>
            <view class="result-item">
                <text class="result-label">收益回撤比</text>
                <text class="result-value">1.5</text>
            </view>
        </view>
        
        <view class="example-stocks card">
            <text class="section-title">近期符合条件个股</text>
            <view class="stock-list">
                <view class="stock-item" v-for="(stock, index) in matchingStocks" :key="index">
                    <view class="stock-info">
                        <text class="stock-code">{{stock.code}}</text>
                        <text class="stock-name">{{stock.name}}</text>
                    </view>
                    <view class="stock-match">
                        <text class="match-score" :class="getScoreClass(stock.matchScore)">匹配度: {{stock.matchScore}}%</text>
                        <text class="match-date">{{stock.signalDate}}</text>
                    </view>
                </view>
            </view>
        </view>
    </view>
</template>

<script>
export default {
    data() {
        return {
            // 优势场景
            advantageousScenarios: [
                "涨停后缩量调整的股票",
                "有主力控盘特征的个股",
                "基本面良好但短期调整的股票",
                "板块轮动中的强势股"
            ],
            
            // 风险提示
            riskWarnings: [
                "大盘处于明显下跌趋势时慎用",
                "个股基本面出现重大不利变化时不宜使用",
                "连续跌停后反弹不适用此策略",
                "成交量异常放大时需谨慎判断"
            ],
            
            // 近期符合条件个股(示例数据)
            matchingStocks: [
                {
                    code: "000001",
                    name: "平安银行",
                    matchScore: 92,
                    signalDate: "2023-05-06"
                },
                {
                    code: "600519",
                    name: "贵州茅台",
                    matchScore: 85,
                    signalDate: "2023-05-10"
                },
                {
                    code: "300750",
                    name: "宁德时代",
                    matchScore: 78,
                    signalDate: "2023-05-12"
                },
                {
                    code: "002415",
                    name: "海康威视",
                    matchScore: 65,
                    signalDate: "2023-05-15"
                }
            ]
        }
    },
    methods: {
        // 返回上一页
        navigateBack() {
            uni.navigateBack();
        },
        
        // 根据匹配分数返回对应的样式类
        getScoreClass(score) {
            if (score >= 80) return 'high-score';
            if (score >= 60) return 'medium-score';
            return 'low-score';
        }
    }
}
</script>

<style>
.container {
    padding: 30rpx;
    background-color: #f5f5f5;
}

.header {
    display: flex;
    flex-direction: row;
    align-items: center;
    margin-bottom: 30rpx;
}

.back-button {
    width: 60rpx;
    height: 60rpx;
    display: flex;
    justify-content: center;
    align-items: center;
    margin-right: 20rpx;
}

.back-icon {
    font-family: "iconfont";
    font-size: 40rpx;
    color: #333;
}

.title {
    font-size: 36rpx;
    font-weight: bold;
    color: #333;
}

.card {
    background-color: #fff;
    border-radius: 16rpx;
    padding: 24rpx;
    margin-bottom: 30rpx;
    box-shadow: 0 2rpx 10rpx rgba(0,0,0,0.05);
}

.section-title {
    font-size: 32rpx;
    font-weight: bold;
    color: #333;
    margin-bottom: 20rpx;
    display: block;
}

.description-text {
    font-size: 28rpx;
    color: #666;
    line-height: 1.5;
    margin-bottom: 20rpx;
}

.formula-box {
    background-color: #f7f9fc;
    border-radius: 12rpx;
    padding: 20rpx;
    margin-top: 20rpx;
}

.formula-title {
    font-size: 28rpx;
    font-weight: bold;
    color: #333;
    margin-bottom: 16rpx;
    display: block;
}

.formula-content {
    display: flex;
    flex-direction: column;
}

.formula-line {
    font-size: 26rpx;
    color: #555;
    font-family: monospace;
    margin-bottom: 8rpx;
}

.formula-line.highlight {
    color: #1989fa;
    font-weight: bold;
}

.logic-step {
    display: flex;
    flex-direction: row;
    align-items: center;
    margin-bottom: 16rpx;
}

.step-number {
    width: 40rpx;
    height: 40rpx;
    border-radius: 20rpx;
    background-color: #1989fa;
    color: #fff;
    font-size: 26rpx;
    font-weight: bold;
    display: flex;
    justify-content: center;
    align-items: center;
    margin-right: 16rpx;
}

.step-description {
    font-size: 28rpx;
    color: #555;
    flex: 1;
}

.pattern-visual {
    display: flex;
    flex-direction: column;
    align-items: center;
}

.chart-placeholder {
    width: 100%;
    height: 400rpx;
    background-color: #f7f9fc;
    display: flex;
    justify-content: center;
    align-items: center;
    border-radius: 12rpx;
    margin-bottom: 20rpx;
}

.pattern-image {
    width: 90%;
    height: 90%;
}

.pattern-desc {
    font-size: 26rpx;
    color: #999;
}

.list-container {
    margin-bottom: 30rpx;
}

.list-title {
    font-size: 30rpx;
    font-weight: bold;
    margin-bottom: 16rpx;
    display: block;
}

.list-title.advantage {
    color: #52c41a;
}

.list-title.risk {
    color: #f5222d;
}

.list-item {
    display: flex;
    flex-direction: row;
    align-items: center;
    margin-bottom: 12rpx;
}

.item-icon {
    width: 40rpx;
    height: 40rpx;
    border-radius: 20rpx;
    display: flex;
    justify-content: center;
    align-items: center;
    margin-right: 16rpx;
    font-size: 24rpx;
    font-weight: bold;
    color: #fff;
}

.item-icon.advantage {
    background-color: #52c41a;
}

.item-icon.risk {
    background-color: #f5222d;
}

.item-text {
    font-size: 28rpx;
    color: #555;
    flex: 1;
}

.code-block {
    background-color: #f7f9fc;
    border-radius: 12rpx;
    padding: 20rpx;
    margin-top: 16rpx;
}

.code-line {
    font-size: 26rpx;
    color: #555;
    font-family: monospace;
    margin-bottom: 8rpx;
}

.result-item {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
    padding: 16rpx 0;
    border-bottom: 1px solid #f0f0f0;
}

.result-label {
    font-size: 28rpx;
    color: #666;
}

.result-value {
    font-size: 28rpx;
    font-weight: bold;
    color: #333;
}

.result-value.success {
    color: #f5222d;
}

.result-value.danger {
    color: #52c41a;
}

.stock-list {
    margin-top: 16rpx;
}

.stock-item {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
    padding: 16rpx 0;
    border-bottom: 1px solid #f0f0f0;
}

.stock-info {
    display: flex;
    flex-direction: column;
}

.stock-code {
    font-size: 28rpx;
    font-weight: bold;
    color: #333;
}

.stock-name {
    font-size: 24rpx;
    color: #666;
}

.stock-match {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
}

.match-score {
    font-size: 28rpx;
    font-weight: bold;
}

.match-score.high-score {
    color: #f5222d;
}

.match-score.medium-score {
    color: #faad14;
}

.match-score.low-score {
    color: #52c41a;
}

.match-date {
    font-size: 24rpx;
    color: #999;
}
</style> 
