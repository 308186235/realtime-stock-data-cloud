<template>
  <view>
    <page-header title="T交易策略" :showBack="true" />
    
    <t-trading-page />
    
    <tab-bar :active="3" />
  </view>
</template>

<script>
import PageHeader from '@/components/page-header/page-header.vue'
import TabBar from '@/components/tab-bar/tab-bar.vue'
import TTradingPage from '@/t_trading_page.vue'

export default {
  components: {
    PageHeader,
    TabBar,
    TTradingPage
  },
  data() {
    return {}
  },
  onLoad() {
    uni.setNavigationBarTitle({
      title: 'T交易策略'
    })
  },
  methods: {}
}
</script>

<style lang="scss">
page {
  background-color: #f5f7fa;
}
</style> 
