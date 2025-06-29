<template>
    <view :class="['container', isDarkMode ? 'dark-theme' : 'light-theme']">
        <view class="header">
            <view class="title">市场追踪</view>
            <view class="subtitle">前端界面已移除,后端服务仍在运行</view>
        </view>
        
        <!-- 功能已整合提示 -->
        <view class="unavailable-notice">
            <view class="notice-icon"></view>
            <text class="notice-text">市场追踪功能已集成到Agent分析模块</text>
            <text class="notice-subtext">所有市场数据分析功能已集成到Agent分析页面中,后端数据采集和分析服务正常运行</text>
            <text class="notice-detail">后端市场追踪服务继续进行数据采集,趋势分析和决策生成,这些数据被Agent决策Agent交易系统使用</text>
            <button class="redirect-btn" @click="redirectToAI">前往Agent分析</button>
        </view>
    </view>
</template>

<script>
export default {
    data() {
        return {
            isDarkMode: false
        }
    },
    onLoad() {
        // 获取当前主题设置
        const app = getApp();
        this.isDarkMode = app.globalData.isDarkMode;
        
        // 自动跳转到Agent分析页面(延迟3秒)
        setTimeout(() => {
            this.redirectToAI();
        }, 3000);
    },
    onShow() {
        // 每次显示页面时检查当前主题
        const app = getApp();
        this.isDarkMode = app.globalData.isDarkMode;
    },
    methods: {
        // 重定向到Agent分析页面
        redirectToAI() {
            uni.switchTab({
                url: '/pages/agent-analysis/index'
            });
        }
    }
}
</script>

<style>
/* 基础容器样式 */
.container {
    padding: 30rpx;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}

/* 主题样式 */
.dark-theme {
    background-color: #141414;
    color: #ffffff;
}

.light-theme {
    background-color: #f5f5f5;
    color: #333333;
}

/* 头部样式 */
.header {
    margin-bottom: 30rpx;
    text-align: center;
}

.title {
    font-size: 40rpx;
    font-weight: bold;
    margin-bottom: 10rpx;
}

.subtitle {
    font-size: 26rpx;
    opacity: 0.7;
}

/* 不可用提示样式 */
.unavailable-notice {
    width: 100%;
    max-width: 600rpx;
    padding: 60rpx 40rpx;
    background-color: rgba(255, 255, 255, 0.1);
    border-radius: 20rpx;
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
}

.notice-icon {
    width: 120rpx;
    height: 120rpx;
    margin-bottom: 30rpx;
    background-color: rgba(255, 255, 255, 0.15);
    border-radius: 50%;
}

.notice-text {
    font-size: 36rpx;
    font-weight: bold;
    margin-bottom: 20rpx;
}

.notice-subtext {
    font-size: 28rpx;
    opacity: 0.8;
    margin-bottom: 20rpx;
}

.notice-detail {
    font-size: 24rpx;
    opacity: 0.6;
    margin-bottom: 40rpx;
    line-height: 1.5;
}

.redirect-btn {
    padding: 20rpx 60rpx;
    border-radius: 10rpx;
    background-color: #4c8dff;
    color: white;
    font-size: 30rpx;
}

.dark-theme .redirect-btn {
    background-color: #4c8dff;
}

.light-theme .redirect-btn {
    background-color: #3478f6;
}
</style> 
