// 简化版市场追踪页面
<template>
  <view class="container">
    <view class="header">
      <text class="title">市场追踪</text>
    </view>
    
    <view class="content">
      <text>测试页面</text>
      <button @tap="testAction">测试按钮</button>
    </view>
  </view>
</template>

<script>
export default {
  data: function() {
    return {
      testData: 'test'
    }
  },
  methods: {
    testAction: function() {
      uni.showToast({
        title: '测试成功',
        icon: 'success'
      });
    }
  }
}
</script>

<style>
.container {
  padding: 20px;
}
.header {
  margin-bottom: 20px;
}
.title {
  font-size: 20px;
  font-weight: bold;
}
.content {
  background-color: #f5f5f5;
  padding: 15px;
  border-radius: 5px;
}
</style>
