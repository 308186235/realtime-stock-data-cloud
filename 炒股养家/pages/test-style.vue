<template>
    <view class="container" :class="themeClass">
        <view class="header">
            <view class="title">样式测试页面</view>
            <view class="subtitle">用于测试和预览UI组件样式</view>
        </view>
        
        <!-- 基础样式测试 -->
        <view class="card">
            <view class="card-title">按钮样式</view>
            <view class="button-container">
                <button class="btn primary">主要按钮</button>
                <button class="btn secondary">次要按钮</button>
                <button class="btn outline">边框按钮</button>
                <button class="btn text">文本按钮</button>
            </view>
        </view>
        
        <!-- 颜色样式测试 -->
        <view class="card">
            <view class="card-title">颜色样式</view>
            <view class="color-grid">
                <view class="color-item">
                    <view class="color-block primary-bg"></view>
                    <text class="color-name">主色调</text>
                </view>
                <view class="color-item">
                    <view class="color-block success-bg"></view>
                    <text class="color-name">成功色</text>
                </view>
                <view class="color-item">
                    <view class="color-block warning-bg"></view>
                    <text class="color-name">警告色</text>
                </view>
                <view class="color-item">
                    <view class="color-block danger-bg"></view>
                    <text class="color-name">危险色</text>
                </view>
                <view class="color-item">
                    <view class="color-block info-bg"></view>
                    <text class="color-name">信息色</text>
                </view>
            </view>
        </view>
        
        <!-- 表单样式测试 -->
        <view class="card">
            <view class="card-title">表单样式</view>
            <view class="form-container">
                <view class="form-item">
                    <text class="form-label">输入框</text>
                    <input type="text" placeholder="请输入内容" class="form-input" />
                </view>
                <view class="form-item">
                    <text class="form-label">选择器</text>
                    <picker @change="onPickerChange" :value="pickerIndex" :range="pickerItems">
                        <view class="picker-value">{{pickerItems[pickerIndex]}}</view>
                    </picker>
                </view>
                <view class="form-item">
                    <text class="form-label">开关</text>
                    <switch :checked="switchValue" @change="onSwitchChange" color="#4c8dff" />
                </view>
                <view class="form-item">
                    <text class="form-label">滑块</text>
                    <slider :value="sliderValue" @change="onSliderChange" show-value />
                </view>
            </view>
        </view>
        
        <!-- 主题切换 -->
        <view class="card">
            <view class="card-title">主题切换</view>
            <view class="theme-switcher">
                <view class="theme-option" :class="{'active': themeClass === 'light-theme'}" @click="changeTheme('light')">
                    <text>浅色主题</text>
                </view>
                <view class="theme-option" :class="{'active': themeClass === 'dark-theme'}" @click="changeTheme('dark')">
                    <text>深色主题</text>
                </view>
            </view>
        </view>
    </view>
</template>

<script>
export default {
    data() {
        return {
            themeClass: 'dark-theme', // 默认深色主题
            pickerItems: ['选项1', '选项2', '选项3', '选项4'],
            pickerIndex: 0,
            switchValue: true,
            sliderValue: 50
        };
    },
    
    onLoad() {
        // 加载系统主题设置
        this.detectSystemTheme();
    },
    
    methods: {
        // 检测系统主题
        detectSystemTheme() {
            // 先从本地存储获取用户之前的主题设置
            try {
                const savedTheme = uni.getStorageSync('appTheme');
                if (savedTheme) {
                    this.themeClass = savedTheme === 'dark' ? 'dark-theme' : 'light-theme';
                    return;
                }
            } catch (e) {
                console.log('获取存储的主题失败', e);
            }
            
            // 检测系统主题
            uni.getSystemInfo({
                success: (res) => {
                    // 根据系统明暗主题设置主题
                    if (res.theme) {
                        this.themeClass = res.theme === 'dark' ? 'dark-theme' : 'light-theme';
                    } else if (res.osTheme) {
                        this.themeClass = res.osTheme === 'dark' ? 'dark-theme' : 'light-theme';
                    } else {
                        // 默认设置为深色主题
                        this.themeClass = 'dark-theme';
                    }
                },
                fail: () => {
                    // 默认为深色主题
                    this.themeClass = 'dark-theme';
                }
            });
        },
        
        // 更改主题
        changeTheme(theme) {
            this.themeClass = theme === 'dark' ? 'dark-theme' : 'light-theme';
            
            // 保存主题设置到本地存储
            try {
                uni.setStorageSync('appTheme', theme);
            } catch (e) {
                console.log('保存主题设置失败', e);
            }
        },
        
        // 选择器变化
        onPickerChange(e) {
            this.pickerIndex = e.detail.value;
        },
        
        // 开关变化
        onSwitchChange(e) {
            this.switchValue = e.detail.value;
        },
        
        // 滑块变化
        onSliderChange(e) {
            this.sliderValue = e.detail.value;
        }
    }
};
</script>

<style>
.container {
    padding: 30rpx;
    min-height: 100vh;
}

/* 主题样式 */
.dark-theme {
    background-color: #141414;
    color: #e0e0e0;
}

.light-theme {
    background-color: #f5f5f5;
    color: #333333;
}

.dark-theme .card {
    background-color: #222222;
    border-radius: 12rpx;
    box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.3);
    margin-bottom: 20rpx;
}

.light-theme .card {
    background-color: #ffffff;
    border-radius: 12rpx;
    box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.05);
    margin-bottom: 20rpx;
}

/* 头部样式 */
.header {
    margin-bottom: 20rpx;
}

.title {
    font-size: 40rpx;
    font-weight: bold;
    margin-bottom: 10rpx;
}

.subtitle {
    font-size: 26rpx;
    color: #999;
}

/* 卡片样式 */
.card {
    padding: 20rpx;
    margin-bottom: 20rpx;
}

.card-title {
    font-size: 32rpx;
    font-weight: bold;
    margin-bottom: 20rpx;
}

/* 按钮样式 */
.button-container {
    display: flex;
    flex-wrap: wrap;
    margin: 0 -10rpx;
}

.btn {
    margin: 10rpx;
    padding: 20rpx 30rpx;
    border-radius: 8rpx;
    font-size: 28rpx;
    min-width: 200rpx;
    text-align: center;
}

.primary {
    background-color: #4c8dff;
    color: #fff;
}

.secondary {
    background-color: #555;
    color: #fff;
}

.dark-theme .outline {
    background-color: transparent;
    color: #fff;
    border: 1px solid #555;
}

.light-theme .outline {
    background-color: transparent;
    color: #333;
    border: 1px solid #ddd;
}

.text {
    background-color: transparent;
    color: #4c8dff;
    padding-left: 0;
    padding-right: 0;
}

/* 颜色样式 */
.color-grid {
    display: flex;
    flex-wrap: wrap;
    margin: 0 -10rpx;
}

.color-item {
    width: 20%;
    padding: 10rpx;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    align-items: center;
}

.color-block {
    width: 100rpx;
    height: 100rpx;
    border-radius: 8rpx;
    margin-bottom: 10rpx;
}

.color-name {
    font-size: 24rpx;
    color: #999;
}

.primary-bg {
    background-color: #4c8dff;
}

.success-bg {
    background-color: #52c41a;
}

.warning-bg {
    background-color: #faad14;
}

.danger-bg {
    background-color: #f5222d;
}

.info-bg {
    background-color: #1890ff;
}

/* 表单样式 */
.form-container {
    padding: 10rpx;
}

.form-item {
    margin-bottom: 20rpx;
}

.form-label {
    display: block;
    font-size: 26rpx;
    margin-bottom: 10rpx;
}

.form-input {
    height: 80rpx;
    border-radius: 8rpx;
    padding: 0 20rpx;
    font-size: 28rpx;
    width: 100%;
    box-sizing: border-box;
}

.dark-theme .form-input {
    background-color: #333;
    color: #fff;
    border: 1px solid #444;
}

.light-theme .form-input {
    background-color: #f5f5f5;
    color: #333;
    border: 1px solid #ddd;
}

.picker-value {
    height: 80rpx;
    line-height: 80rpx;
    padding: 0 20rpx;
    font-size: 28rpx;
    border-radius: 8rpx;
}

.dark-theme .picker-value {
    background-color: #333;
    color: #fff;
    border: 1px solid #444;
}

.light-theme .picker-value {
    background-color: #f5f5f5;
    color: #333;
    border: 1px solid #ddd;
}

/* 主题切换 */
.theme-switcher {
    display: flex;
    justify-content: center;
}

.theme-option {
    padding: 20rpx 40rpx;
    margin: 0 10rpx;
    border-radius: 8rpx;
    font-size: 28rpx;
    cursor: pointer;
}

.dark-theme .theme-option {
    background-color: #333;
}

.light-theme .theme-option {
    background-color: #f0f0f0;
}

.theme-option.active {
    background-color: #4c8dff;
    color: #fff;
}
</style>
