<template>
  <view class="bottom-nav">
    <view 
      v-for="(item, index) in navItems" 
      :key="index" 
      class="nav-item" 
      :class="{ active: activeTab === item.key }"
      @click="switchTab(item.key)"
    >
      <view :class="['nav-icon', item.iconClass]"></view>
      <text class="nav-text">{{ item.text }}</text>
    </view>
  </view>
</template>

<script>
import { navigateTo, switchTab } from './router/mainNav.js';

export default {
  props: {
    activeTab: {
      type: String,
      default: 'home'
    }
  },
  data() {
    return {
      navItems: [
        { key: 'aiTrading', text: 'Agent交易', iconClass: 'ai-icon' },
        { key: 'home', text: '首页', iconClass: 'home-icon' },
        { key: 'stock', text: '选股', iconClass: 'stock-icon' },
        { key: 'trade', text: '交易', iconClass: 'trade-icon' },
        { key: 'portfolio', text: '持仓', iconClass: 'portfolio-icon' },
      ]
    }
  },
  methods: {
    switchTab(key) {
      this.$emit('tab-changed', key);
      
      // 使用统一的导航方法
      if (key === this.activeTab) return; // 避免重复点击当前标签
      
      try {
        switchTab(key);
      } catch (error) {
        console.error('导航失败:', error);
        navigateTo(key);
      }
    }
  }
}
</script>

<style>
.bottom-nav {
  display: flex;
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 110rpx;
  background-color: #222;
  border-top: 1rpx solid #333;
  z-index: 100;
}

.nav-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 6rpx 0;
}

.nav-icon {
  width: 50rpx;
  height: 50rpx;
  margin-bottom: 6rpx;
  opacity: 0.6;
}

.active .nav-icon {
  opacity: 1;
}

.ai-icon {
  background: url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0id2hpdGUiIGQ9Ik0xMiwxQzEwLjg5LDEgMTAsMS45IDEwLDNDMTAsNC4xIDEwLjg5LDUgMTIsNUMxMy4xLDUgMTQsNC4xIDE0LDNDMTQsMS45IDEzLjEsMSAxMiwxTTE0LDkuNUMxNCw2LjQ2IDExLjYyLDQgOC41LDRDNS4zOCw0IDMsNi40NiAzLDkuNUMzLDExLjY5IDQuNjcsMTMuNjEgNywxNC4yMVYyMEg5VjE2SDE0VjIwSDE2VjEzLjVIMTRWOS41TTIxLjUsMTJIMTguNVYxMC41SDE3LjVWMTJIMTYuNVYxM0gxNy41VjE0LjVIMTguNVYxM0gyMS41TDI1LDkuNUgxNS41VjExSDIwLjUiLz48L3N2Zz4=') no-repeat center;
  background-size: contain;
}

.home-icon {
  background: url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0id2hpdGUiIGQ9Ik0xMCwyMFYxNEgxNFYyMEgxOVYxMkgyMkwxMiwzTDIsMTJINVYyMEgxMFoiLz48L3N2Zz4=') no-repeat center;
  background-size: contain;
}

.stock-icon {
  background: url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0id2hpdGUiIGQ9Ik0yMywxMi4yQzIzLDExLjcgMjIuNywxMS4yOSAyMi4yLDExLjA5QzIyLjcsMTAuODkgMjMsMTAuNSAyMywxMEMyMyw5LjMgMjIuMyw4LjY5IDIxLjM0LDguNDFDMjEuODEsOC4xMyAyMiw3LjcgMjIsNy4yQzIyLDUuODggMTYuODcsNSAxMCw1QzMuMTMsNSAtMiw1Ljg4IC0yLDcuMkMtMiw3LjcgLTEuODEsOC4xMyAtMS4zNCw4LjQxQy0yLjMsOC42OSAtMyw5LjMgLTMsMTBDLTMsMTAuNSAtMi43LDEwLjg5IC0yLjIsMTEuMDlDLTIuNywxMS4yOSAtMywxMS43IC0zLDEyLjJDLTMsMTIuNyAtMi43LDEzLjExIC0yLjIsMTMuMzFDLTIuNywxMy41MSAtMywxMy45IC0zLDE0LjRDLTMsMTUuNzIgMi4xMywxNi42IDksMTYuNkMxMS42LDE2LjYgMTQuMSwxNi40MiAxNS44MywxNi4xN0MxNS45NCwxNy41IDE3LjE1LDE4LjYgMTguNjcsMTguNkMyMC4yNywxOC42IDIxLjU3LDE3LjQ4IDIxLjU3LDE2LjFWMTRDMjEuNTcsMTMuOCAyMS41LDEzLjYyIDIxLjQsMTMuNDVDMjEuNjksMTMuMzIgMjIsMTMuMTUgMjIsMTIuOFYxMi40QzIyLDEyLjIyIDIxLjg4LDEyLjA2IDIxLjcxLDExLjkyQzIyLjQ1LDExLjcgMjMsMTEuMjEgMjMsMTAuNkMyMywxMC40IDIyLjk2LDEwLjIxIDIyLjg3LDEwLjAzQzIzLDkuODMgMjMsOS42MSAyMyw5LjRNMTAuOCwxMC40QzYuNTYsMTAuNCAzLjIsOS45IDMuMiw5LjRDMy4yLDguOSA2LjYzLDguNDEgMTAuOCw4LjQxQzE1LDguNDEgMTguNCw4LjkgMTguNCw5LjRDMTguNCw5LjkgMTUsMTAuNCAxMC44LDEwLjRNMTAuOCwxMy40QzYuNTYsMTMuNCAzLjIsMTIuOSAzLjIsMTIuNEMzLjIsMTEuOSA2LjYzLDExLjQgMTAuOCwxMS40QzE1LDExLjQgMTguNCwxMS45IDE4LjQsMTIuNEMxOC40LDEyLjkgMTUsMTMuNCAxMC44LDEzLjRNMTAuOCwxNS45QzYuNTYsMTUuOSAzLjIsMTUuNDEgMy4yLDE0LjlDMy4yLDE0LjQgNi42MywxMy45MSAxMC44LDEzLjkxQzExLjcyLDEzLjkxIDEyLjYyLDEzLjk0IDEzLjUsMTRDMTMuNTYsMTQuNzUgMTQsMTUuNDIgMTQuNywxNS44MUMxMy40LDE1Ljg3IDEyLjEsMTUuOSAxMC44LDE1LjkNDMuMTcsMTIuNSA2LjUsMTIgMTAuNSwxMkMxNC41LDEyIDE3LjgzLDEyLjUgMTcuODMsMTNDMTcuODMsMTMuNSAxNC41LDE0IDEwLjUsMTRNMTAuNSwxMS4wMUM2LjUsMTEuMDEgMy4xNywxMC41MSAzLjE3LDEwLjAxQzMuMTcsOS41IDYuNSw5IDEwLjUsOUMxNC41LDkgMTcuODMsOS41IDE3LjgzLDEwLjAxQzE3LjgzLDEwLjUxIDE0LjUsMTEuMDEgMTAuNSwxMS4wMSIvPjwvc3ZnPg==') no-repeat center;
  background-size: contain;
}

.trade-icon {
  background: url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0id2hpdGUiIGQ9Ik0zLDEzSDVWMThIM1YxM00xOSwxM0gyMVYxOEgxOVYxM001LDNIMTlWMTFIMjFWM0MyMSwyLjQ1IDIwLjU1LDIgMjAsMkgyQzEuNDUsMiAxLDIuNDUgMSwzVjExSDNWM003LDlIOVYMTJIN1Y5TTExLDIySDE4QzE4LjU1LDIyIDE5LDIxLjU1IDE5LDIxVjE5SDExVjIyTTExLDZIMTNWN0gxMVY2TTE1LDZIMTdWN0gxNVY2TTE1LDhIMTdWOUgxNVY4TTExLDhIMTNWOUgxMVY4TTExLDEwSDEzVjExSDExVjEwTTExLDEySDE4VjEzSDE1VjE0SDExVjEyTTE1LDEwSDE3VjExSDE1VjEwWiIvPjwvc3ZnPg==') no-repeat center;
  background-size: contain;
}

.portfolio-icon {
  background: url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0id2hpdGUiIGQ9Ik0yMCw4SDE3LjE5QzE2LjkzLDYuOTQgMTYuMzYsNiAxNS42OSw2SDEyLjVDMTEuODMsNiAxMS4zLDYuOTQgMTEuMDUsOEg4Yy0xLjEsMC0yLDAuOS0yLDJ2MTBjMCwxLjEgMC45LDIgMiwyaDE0YzEuMSwwIDItMC45IDItMnYtMTBDMjIsOC45IDIxLjEsOCAyMCw4IE0xNS43NSw4LjBjLTAuMDYsMC4yIC0wLjEzLDAuNDEgLTAuMTYsMC43aDIuNzZjLTAuMDMtMC4yOSAtMC4xLTAuNSAtMC4xNi0wLjdIMTUuNzVaIi8+PC9zdmc+') no-repeat center;
  background-size: contain;
}

.nav-text {
  font-size: 22rpx;
  color: #ccc;
}

.active .nav-text {
  color: #fff;
}

.active {
  color: #1989fa;
}
</style> 
