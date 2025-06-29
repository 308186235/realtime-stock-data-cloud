<template>
  <view class="dark-container" style="background-color: #141414; color: #e0e0e0; padding: 15px;">
    <view class="header" style="margin-bottom: 20px; text-align: center;">
      <text class="title" style="font-size: 20px; font-weight: bold; color: #fff;">深色主题测试</text>
    </view>
    
    <view class="dark-section" style="margin-bottom: 20px; background-color: #1e1e1e; border-radius: 10px; padding: 15px; box-shadow: 0 2px 8px rgba(0,0,0,0.3);">
      <view class="section-header" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; border-bottom: 1px solid #333; padding-bottom: 10px;">
        <text class="section-title" style="font-size: 18px; font-weight: bold; color: #fff;">市场指数测试</text>
        <view class="refresh-button" @tap="refreshPage" style="font-size: 14px; color: #4c8dff; padding: 5px 10px; background-color: #2a2a2a; border-radius: 15px;">刷新</view>
      </view>
      
      <view class="market-grid" style="display: flex; flex-wrap: wrap; margin: 0 -5px;">
        <!-- 测试卡片 1 -->
        <view class="market-card" style="width: calc(50% - 10px); margin: 5px; background-color: #262626; border-radius: 5px; overflow: hidden; box-shadow: 0 1px 5px rgba(0,0,0,0.2);">
          <view class="market-card-header" style="background-color: #333; padding: 8px 12px; display: flex; justify-content: space-between; align-items: center;">
            <text class="index-code" style="font-size: 12px; color: #999;">sh000001</text>
            <text class="index-name" style="font-size: 14px; color: #ddd; font-weight: bold;">上证指数</text>
          </view>
          <view class="market-card-body" style="padding: 12px; text-align: center;">
            <view class="index-value" style="font-size: 26px; font-weight: bold; margin-bottom: 5px; color: #fff; font-family: DIN, Arial, sans-serif;">3,258.63</view>
            <view class="index-change up" style="font-size: 16px; font-weight: bold; font-family: DIN, Arial, sans-serif; color: #ff4d4f;">+0.56%</view>
          </view>
        </view>
        
        <!-- 测试卡片 2 -->
        <view class="market-card" style="width: calc(50% - 10px); margin: 5px; background-color: #262626; border-radius: 5px; overflow: hidden; box-shadow: 0 1px 5px rgba(0,0,0,0.2);">
          <view class="market-card-header" style="background-color: #333; padding: 8px 12px; display: flex; justify-content: space-between; align-items: center;">
            <text class="index-code" style="font-size: 12px; color: #999;">sz399001</text>
            <text class="index-name" style="font-size: 14px; color: #ddd; font-weight: bold;">深证成指</text>
          </view>
          <view class="market-card-body" style="padding: 12px; text-align: center;">
            <view class="index-value" style="font-size: 26px; font-weight: bold; margin-bottom: 5px; color: #fff; font-family: DIN, Arial, sans-serif;">10,825.93</view>
            <view class="index-change down" style="font-size: 16px; font-weight: bold; font-family: DIN, Arial, sans-serif; color: #52c41a;">-0.23%</view>
          </view>
        </view>
      </view>
      
      <view class="data-time" style="text-align: right; color: #888; font-size: 12px; margin-top: 10px; padding-right: 10px;">
        测试时间: {{ currentTime }}
      </view>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      currentTime: this.formatDateTime(new Date())
    }
  },
  onLoad() {
    // 方案一:尝试直接操作页面样式
    const pageStyle = uni.createSelectorQuery().selectAll('.dark-container').boundingClientRect();
    console.log('检查页面样式:', pageStyle);
    
    // 方案二:尝试插入全局样式
    const style = document.createElement('style');
    style.type = 'text/css';
    style.innerHTML = `
      body, page { 
        background-color: #141414 !important;
        color: #e0e0e0 !important;
      }
    `;
    document.head.appendChild(style);
  },
  methods: {
    refreshPage() {
      this.currentTime = this.formatDateTime(new Date());
      uni.showToast({
        title: '页面已刷新',
        icon: 'success'
      });
    },
    formatDateTime(date) {
      return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}:${String(date.getSeconds()).padStart(2, '0')}`;
    }
  }
}
</script>

<style scoped>
/* 这种scoped样式会确保仅应用于当前组件 */
.dark-container {
  background-color: #141414 !important;
  color: #e0e0e0 !important;
}

.dark-section {
  background-color: #1e1e1e !important;
  box-shadow: 0 2px 8px rgba(0,0,0,0.3) !important;
}

/* 为了防止样式被覆盖,我们使用特殊的选择器 */
.dark-container >>> .title {
  color: #fff !important;
}

.dark-container >>> .section-title {
  color: #fff !important;
}

.dark-container >>> .market-card {
  background-color: #262626 !important;
}

.dark-container >>> .market-card-header {
  background-color: #333 !important;
}

.dark-container >>> .up {
  color: #ff4d4f !important;
}

.dark-container >>> .down {
  color: #52c41a !important;
}
</style>

<!-- 全局样式,强制覆盖 -->
<style>
page {
  background-color: #141414 !important;
}

/* 如果uni-app使用了某些全局类,我们可以直接覆盖它们 */
.uni-page-head {
  background-color: #141414 !important;
}

.uni-page-head-bd {
  color: #fff !important;
}

.uni-page-body {
  background-color: #141414 !important;
}
</style> 
