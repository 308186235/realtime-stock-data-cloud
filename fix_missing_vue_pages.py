#!/usr/bin/env python3
"""
修复缺失的Vue页面文件
"""

import os
import shutil
from pathlib import Path

class VuePagesFixer:
    """Vue页面修复器"""
    
    def __init__(self):
        self.frontend_repo = "stock-trading-frontend"
        self.backup_dir = "repo_fix_backup_20250706_173119/frontend_backup"
        
    def fix_missing_pages(self):
        """修复缺失的页面文件"""
        print("🔧 修复缺失的Vue页面文件...")
        print("=" * 50)
        
        # 复制index页面
        self._copy_index_page()
        
        # 创建其他基础页面
        self._create_basic_pages()
        
        print("✅ Vue页面文件修复完成")
    
    def _copy_index_page(self):
        """复制index页面"""
        print("📄 复制index页面...")
        
        src_file = f"{self.backup_dir}/pages/index/index.vue"
        dst_dir = f"{self.frontend_repo}/pages/index"
        dst_file = f"{dst_dir}/index.vue"
        
        # 创建目录
        os.makedirs(dst_dir, exist_ok=True)
        
        if os.path.exists(src_file):
            shutil.copy2(src_file, dst_file)
            print(f"  ✅ 复制: {src_file} → {dst_file}")
        else:
            print(f"  ⚠️ 源文件不存在: {src_file}")
            # 创建基础index页面
            self._create_basic_index_page(dst_file)
    
    def _create_basic_index_page(self, file_path):
        """创建基础index页面"""
        content = '''<template>
    <view class="container">
        <view class="header">
            <text class="title">股票交易系统</text>
            <text class="subtitle">实时行情 · 智能交易</text>
        </view>
        
        <view class="stats-grid">
            <view class="stat-card">
                <text class="stat-value">{{ totalValue }}</text>
                <text class="stat-label">总资产</text>
            </view>
            <view class="stat-card">
                <text class="stat-value" :class="profitClass">{{ todayProfit }}</text>
                <text class="stat-label">今日盈亏</text>
            </view>
        </view>
        
        <view class="quick-actions">
            <view class="action-btn" @tap="goToTrading">
                <text class="action-icon">📈</text>
                <text class="action-text">交易</text>
            </view>
            <view class="action-btn" @tap="goToPortfolio">
                <text class="action-icon">💼</text>
                <text class="action-text">持仓</text>
            </view>
            <view class="action-btn" @tap="goToMarket">
                <text class="action-icon">📊</text>
                <text class="action-text">行情</text>
            </view>
        </view>
    </view>
</template>

<script>
export default {
    data() {
        return {
            totalValue: '¥0.00',
            todayProfit: '+¥0.00'
        }
    },
    computed: {
        profitClass() {
            return this.todayProfit.startsWith('+') ? 'profit' : 'loss'
        }
    },
    methods: {
        goToTrading() {
            uni.navigateTo({
                url: '/pages/trade/trade'
            })
        },
        goToPortfolio() {
            uni.navigateTo({
                url: '/pages/portfolio/portfolio'
            })
        },
        goToMarket() {
            uni.navigateTo({
                url: '/pages/market-tracking/market-tracking'
            })
        }
    }
}
</script>

<style scoped>
.container {
    padding: 20rpx;
    background-color: #f5f5f5;
    min-height: 100vh;
}

.header {
    text-align: center;
    margin-bottom: 40rpx;
}

.title {
    font-size: 48rpx;
    font-weight: bold;
    color: #333;
    display: block;
}

.subtitle {
    font-size: 28rpx;
    color: #666;
    margin-top: 10rpx;
    display: block;
}

.stats-grid {
    display: flex;
    gap: 20rpx;
    margin-bottom: 40rpx;
}

.stat-card {
    flex: 1;
    background: white;
    padding: 30rpx;
    border-radius: 16rpx;
    text-align: center;
    box-shadow: 0 4rpx 12rpx rgba(0,0,0,0.1);
}

.stat-value {
    font-size: 36rpx;
    font-weight: bold;
    color: #333;
    display: block;
}

.stat-value.profit {
    color: #ff4757;
}

.stat-value.loss {
    color: #2ed573;
}

.stat-label {
    font-size: 24rpx;
    color: #666;
    margin-top: 10rpx;
    display: block;
}

.quick-actions {
    display: flex;
    gap: 20rpx;
    flex-wrap: wrap;
}

.action-btn {
    flex: 1;
    min-width: 200rpx;
    background: white;
    padding: 40rpx 20rpx;
    border-radius: 16rpx;
    text-align: center;
    box-shadow: 0 4rpx 12rpx rgba(0,0,0,0.1);
}

.action-icon {
    font-size: 48rpx;
    display: block;
    margin-bottom: 10rpx;
}

.action-text {
    font-size: 28rpx;
    color: #333;
    display: block;
}
</style>'''
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"  ✅ 创建基础index页面: {file_path}")
    
    def _create_basic_pages(self):
        """创建其他基础页面"""
        print("📄 创建其他基础页面...")
        
        pages = [
            ('trade', '交易'),
            ('portfolio', '持仓'),
            ('market-tracking', '行情'),
            ('settings', '设置')
        ]
        
        for page_name, page_title in pages:
            self._create_basic_page(page_name, page_title)
    
    def _create_basic_page(self, page_name, page_title):
        """创建基础页面"""
        dst_dir = f"{self.frontend_repo}/pages/{page_name}"
        dst_file = f"{dst_dir}/{page_name}.vue"
        
        # 创建目录
        os.makedirs(dst_dir, exist_ok=True)
        
        content = f'''<template>
    <view class="container">
        <view class="header">
            <text class="title">{page_title}</text>
        </view>
        
        <view class="content">
            <text class="placeholder">功能开发中...</text>
        </view>
    </view>
</template>

<script>
export default {{
    data() {{
        return {{
            
        }}
    }},
    methods: {{
        
    }}
}}
</script>

<style scoped>
.container {{
    padding: 20rpx;
    background-color: #f5f5f5;
    min-height: 100vh;
}}

.header {{
    text-align: center;
    margin-bottom: 40rpx;
}}

.title {{
    font-size: 48rpx;
    font-weight: bold;
    color: #333;
}}

.content {{
    background: white;
    padding: 40rpx;
    border-radius: 16rpx;
    text-align: center;
}}

.placeholder {{
    font-size: 32rpx;
    color: #666;
}}
</style>'''
        
        with open(dst_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"  ✅ 创建页面: {dst_file}")
    
    def update_pages_json(self):
        """更新pages.json配置"""
        print("📄 更新pages.json配置...")
        
        pages_config = {
            "pages": [
                {
                    "path": "pages/index/index",
                    "style": {
                        "navigationBarTitleText": "股票交易系统"
                    }
                },
                {
                    "path": "pages/trade/trade",
                    "style": {
                        "navigationBarTitleText": "交易"
                    }
                },
                {
                    "path": "pages/portfolio/portfolio",
                    "style": {
                        "navigationBarTitleText": "持仓"
                    }
                },
                {
                    "path": "pages/market-tracking/market-tracking",
                    "style": {
                        "navigationBarTitleText": "行情"
                    }
                },
                {
                    "path": "pages/settings/settings",
                    "style": {
                        "navigationBarTitleText": "设置"
                    }
                }
            ],
            "globalStyle": {
                "navigationBarTextStyle": "black",
                "navigationBarTitleText": "股票交易系统",
                "navigationBarBackgroundColor": "#F8F8F8",
                "backgroundColor": "#F8F8F8"
            },
            "tabBar": {
                "color": "#7A7E83",
                "selectedColor": "#3cc51f",
                "borderStyle": "black",
                "backgroundColor": "#ffffff",
                "list": [
                    {
                        "pagePath": "pages/index/index",
                        "iconPath": "static/tabbar/home.png",
                        "selectedIconPath": "static/tabbar/home_active.png",
                        "text": "首页"
                    },
                    {
                        "pagePath": "pages/trade/trade",
                        "iconPath": "static/tabbar/trade.png",
                        "selectedIconPath": "static/tabbar/trade_active.png",
                        "text": "交易"
                    },
                    {
                        "pagePath": "pages/portfolio/portfolio",
                        "iconPath": "static/tabbar/portfolio.png",
                        "selectedIconPath": "static/tabbar/portfolio_active.png",
                        "text": "持仓"
                    },
                    {
                        "pagePath": "pages/settings/settings",
                        "iconPath": "static/tabbar/settings.png",
                        "selectedIconPath": "static/tabbar/settings_active.png",
                        "text": "设置"
                    }
                ]
            }
        }
        
        import json
        pages_json_path = f"{self.frontend_repo}/pages.json"
        with open(pages_json_path, 'w', encoding='utf-8') as f:
            json.dump(pages_config, f, indent=2, ensure_ascii=False)
        
        print(f"  ✅ 更新: {pages_json_path}")
    
    def run_fix(self):
        """运行修复"""
        print("🚀 开始修复Vue页面文件...")
        print("=" * 60)
        
        # 修复缺失的页面
        self.fix_missing_pages()
        
        # 更新pages.json
        self.update_pages_json()
        
        print(f"\n🎉 Vue页面文件修复完成!")
        print("\n📋 下一步:")
        print("1. 提交并推送到GitHub")
        print("2. 测试uni-app项目编译")
        print("3. 验证页面可以正常显示")

if __name__ == "__main__":
    fixer = VuePagesFixer()
    fixer.run_fix()
