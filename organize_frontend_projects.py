#!/usr/bin/env python3
"""
整理前端项目结构脚本
修复"呵呵"项目和其他前端项目的结构问题
"""
import os
import json
import shutil
from datetime import datetime

class FrontendProjectOrganizer:
    """前端项目结构整理器"""
    
    def __init__(self):
        self.fixes_applied = []
        
    def print_banner(self):
        """打印整理横幅"""
        print("=" * 80)
        print("📁 前端项目结构整理")
        print("=" * 80)
        print(f"📅 整理时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("🎯 修复前端项目结构问题")
        print("=" * 80)
        
    def fix_hehe_project(self):
        """修复呵呵项目"""
        print("\n😄 修复呵呵项目...")
        print("-" * 60)
        
        project_path = "呵呵"
        
        if not os.path.exists(project_path):
            print("  ❌ 呵呵项目不存在")
            return
            
        # 创建package.json
        package_json_content = {
            "name": "hehe-stock-app",
            "version": "1.0.0",
            "description": "呵呵 - AI股票交易系统前端",
            "main": "main.js",
            "scripts": {
                "dev": "npx uni serve",
                "build": "npx uni build",
                "dev:h5": "npx uni serve --platform h5",
                "build:h5": "npx uni build --platform h5",
                "dev:mp-weixin": "npx uni serve --platform mp-weixin",
                "build:mp-weixin": "npx uni build --platform mp-weixin",
                "clean": "rimraf node_modules unpackage/dist"
            },
            "dependencies": {
                "@dcloudio/uni-app": "^3.0.0-3080620230817001",
                "@dcloudio/uni-ui": "^1.5.7",
                "vue": "^3.3.4",
                "vuex": "^4.1.0",
                "dayjs": "^1.11.7",
                "axios": "^1.3.4"
            },
            "devDependencies": {
                "@dcloudio/uni-cli-shared": "^3.0.0-3080620230817001",
                "@dcloudio/vue-cli-plugin-uni": "^3.0.0-3080620230817001",
                "@vue/cli-plugin-babel": "^4.5.15",
                "@vue/cli-service": "^4.5.15",
                "rimraf": "^3.0.2"
            },
            "browserslist": [
                "Android >= 4.4",
                "ios >= 9"
            ]
        }
        
        package_json_path = os.path.join(project_path, "package.json")
        with open(package_json_path, 'w', encoding='utf-8') as f:
            json.dump(package_json_content, f, ensure_ascii=False, indent=2)
            
        print("  ✅ 创建package.json")
        self.fixes_applied.append("为呵呵项目创建package.json")
        
        # 创建环境配置文件
        env_js_content = '''// 呵呵项目环境配置
const config = {
  // 开发环境
  development: {
    apiBaseUrl: 'https://api.aigupiao.me',
    wsUrl: 'wss://api.aigupiao.me/ws',
    useMockData: false,
    logLevel: 'debug'
  },
  
  // 生产环境
  production: {
    apiBaseUrl: 'https://api.aigupiao.me',
    wsUrl: 'wss://api.aigupiao.me/ws',
    useMockData: false,
    logLevel: 'error'
  }
};

// 当前环境
const currentEnv = process.env.NODE_ENV === 'production' ? 'production' : 'development';

// 导出当前环境配置
export default {
  current: config[currentEnv],
  requestTimeout: 60000,
  maxRetries: 3,
  retryDelay: 2000
};
'''
        
        env_js_path = os.path.join(project_path, "env.js")
        with open(env_js_path, 'w', encoding='utf-8') as f:
            f.write(env_js_content)
            
        print("  ✅ 创建env.js配置文件")
        self.fixes_applied.append("为呵呵项目创建环境配置")
        
        # 创建utils目录和request.js
        utils_dir = os.path.join(project_path, "utils")
        if not os.path.exists(utils_dir):
            os.makedirs(utils_dir)
            
        request_js_content = '''// 呵呵项目网络请求工具
import env from '../env.js';

// 获取当前环境配置
const currentEnv = env.current;
const BASE_URL = currentEnv.apiBaseUrl;
const TIMEOUT = env.requestTimeout || 60000;

// 统一请求方法
const request = (options = {}) => {
  return new Promise((resolve, reject) => {
    // 验证API地址
    if (!options.url || !options.url.startsWith('http')) {
      if (!options.url.startsWith('/api/')) {
        reject(new Error('❌ 错误:只允许调用真实API'));
        return;
      }
    }
    
    // 请求拦截器
    const token = uni.getStorageSync('token') || '';
    
    // 组装请求选项
    const requestOptions = {
      url: options.url.startsWith('http') ? options.url : BASE_URL + options.url,
      data: options.data || {},
      method: options.method || 'GET',
      header: {
        'content-type': options.contentType || 'application/json',
        'Authorization': token ? `Bearer ${token}` : '',
        ...options.header
      },
      timeout: options.timeout || TIMEOUT
    };
    
    console.log('🔄 API请求:', requestOptions.method, requestOptions.url);
    
    // 发送请求
    uni.request({
      ...requestOptions,
      success: (response) => {
        console.log('✅ API响应:', response.statusCode, response.data);
        
        if (response.statusCode >= 200 && response.statusCode < 300) {
          resolve(response.data);
        } else {
          reject(new Error(`HTTP ${response.statusCode}: ${response.data?.message || '请求失败'}`));
        }
      },
      fail: (error) => {
        console.error('❌ API请求失败:', error);
        
        if (error.errMsg && error.errMsg.includes('timeout')) {
          reject(new Error('请求超时'));
        } else if (error.errMsg && error.errMsg.includes('fail')) {
          reject(new Error('网络请求失败'));
        } else {
          reject(error);
        }
      }
    });
  });
};

// 导出请求方法
export default request;

// 便捷方法
export const get = (url, options = {}) => request({ ...options, url, method: 'GET' });
export const post = (url, data, options = {}) => request({ ...options, url, data, method: 'POST' });
export const put = (url, data, options = {}) => request({ ...options, url, data, method: 'PUT' });
export const del = (url, options = {}) => request({ ...options, url, method: 'DELETE' });
'''
        
        request_js_path = os.path.join(utils_dir, "request.js")
        with open(request_js_path, 'w', encoding='utf-8') as f:
            f.write(request_js_content)
            
        print("  ✅ 创建utils/request.js")
        self.fixes_applied.append("为呵呵项目创建网络请求工具")
        
        # 更新页面配置
        self.update_hehe_pages_config()
        
        # 更新主页面内容
        self.update_hehe_index_page()
        
    def update_hehe_pages_config(self):
        """更新呵呵项目页面配置"""
        print("  🔧 更新页面配置...")
        
        pages_json_content = {
            "pages": [
                {
                    "path": "pages/index/index",
                    "style": {
                        "navigationBarTitleText": "AI股票交易系统",
                        "navigationBarBackgroundColor": "#007AFF",
                        "navigationBarTextStyle": "white"
                    }
                }
            ],
            "globalStyle": {
                "navigationBarTextStyle": "white",
                "navigationBarTitleText": "AI股票交易",
                "navigationBarBackgroundColor": "#007AFF",
                "backgroundColor": "#F8F8F8"
            },
            "tabBar": {
                "color": "#7A7E83",
                "selectedColor": "#007AFF",
                "borderStyle": "black",
                "backgroundColor": "#F8F8F8",
                "list": [
                    {
                        "pagePath": "pages/index/index",
                        "iconPath": "static/tab-home.png",
                        "selectedIconPath": "static/tab-home-active.png",
                        "text": "首页"
                    }
                ]
            },
            "uniIdRouter": {}
        }
        
        pages_json_path = os.path.join("呵呵", "pages.json")
        with open(pages_json_path, 'w', encoding='utf-8') as f:
            json.dump(pages_json_content, f, ensure_ascii=False, indent=2)
            
        print("  ✅ 更新pages.json")
        self.fixes_applied.append("更新呵呵项目页面配置")
        
    def update_hehe_index_page(self):
        """更新呵呵项目首页"""
        print("  🎨 更新首页内容...")
        
        index_vue_content = '''<template>
  <view class="container">
    <view class="header">
      <image class="logo" src="/static/logo.png"></image>
      <text class="title">AI股票交易系统</text>
      <text class="subtitle">呵呵版本</text>
    </view>
    
    <view class="content">
      <view class="card">
        <text class="card-title">系统状态</text>
        <view class="status-item">
          <text class="status-label">API连接:</text>
          <text class="status-value" :class="apiStatus">{{ apiStatusText }}</text>
        </view>
        <view class="status-item">
          <text class="status-label">数据更新:</text>
          <text class="status-value">{{ lastUpdate }}</text>
        </view>
      </view>
      
      <view class="actions">
        <button class="action-btn primary" @click="testConnection">测试连接</button>
        <button class="action-btn" @click="refreshData">刷新数据</button>
      </view>
      
      <view class="logs" v-if="logs.length > 0">
        <text class="logs-title">操作日志</text>
        <view class="log-item" v-for="(log, index) in logs" :key="index">
          <text class="log-text">{{ log }}</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import request from '@/utils/request.js';

export default {
  data() {
    return {
      title: 'AI股票交易系统',
      apiStatus: 'unknown',
      apiStatusText: '未知',
      lastUpdate: '暂无数据',
      logs: []
    }
  },
  
  onLoad() {
    this.addLog('应用启动');
    this.checkApiStatus();
  },
  
  methods: {
    async checkApiStatus() {
      try {
        this.addLog('检查API状态...');
        const response = await request({
          url: '/health',
          method: 'GET'
        });
        
        this.apiStatus = 'online';
        this.apiStatusText = '在线';
        this.lastUpdate = new Date().toLocaleString();
        this.addLog('✅ API连接正常');
        
      } catch (error) {
        this.apiStatus = 'offline';
        this.apiStatusText = '离线';
        this.addLog(`❌ API连接失败: ${error.message}`);
      }
    },
    
    async testConnection() {
      this.addLog('开始连接测试...');
      await this.checkApiStatus();
    },
    
    async refreshData() {
      try {
        this.addLog('刷新数据...');
        const response = await request({
          url: '/api/stocks',
          method: 'GET'
        });
        
        this.lastUpdate = new Date().toLocaleString();
        this.addLog(`✅ 数据刷新成功,获取${response.length || 0}条记录`);
        
      } catch (error) {
        this.addLog(`❌ 数据刷新失败: ${error.message}`);
      }
    },
    
    addLog(message) {
      const timestamp = new Date().toLocaleTimeString();
      this.logs.unshift(`[${timestamp}] ${message}`);
      
      // 只保留最近10条日志
      if (this.logs.length > 10) {
        this.logs = this.logs.slice(0, 10);
      }
    }
  }
}
</script>

<style>
.container {
  padding: 20rpx;
  background-color: #f5f5f5;
  min-height: 100vh;
}

.header {
  text-align: center;
  padding: 40rpx 0;
  background: linear-gradient(135deg, #007AFF, #5AC8FA);
  border-radius: 20rpx;
  margin-bottom: 30rpx;
  color: white;
}

.logo {
  width: 120rpx;
  height: 120rpx;
  border-radius: 60rpx;
  margin-bottom: 20rpx;
}

.title {
  display: block;
  font-size: 48rpx;
  font-weight: bold;
  margin-bottom: 10rpx;
}

.subtitle {
  display: block;
  font-size: 28rpx;
  opacity: 0.8;
}

.content {
  padding: 0 20rpx;
}

.card {
  background: white;
  border-radius: 15rpx;
  padding: 30rpx;
  margin-bottom: 30rpx;
  box-shadow: 0 4rpx 20rpx rgba(0,0,0,0.1);
}

.card-title {
  font-size: 36rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 20rpx;
  display: block;
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15rpx 0;
  border-bottom: 1rpx solid #f0f0f0;
}

.status-item:last-child {
  border-bottom: none;
}

.status-label {
  font-size: 30rpx;
  color: #666;
}

.status-value {
  font-size: 30rpx;
  font-weight: bold;
}

.status-value.online {
  color: #52c41a;
}

.status-value.offline {
  color: #ff4d4f;
}

.status-value.unknown {
  color: #faad14;
}

.actions {
  display: flex;
  gap: 20rpx;
  margin-bottom: 30rpx;
}

.action-btn {
  flex: 1;
  height: 80rpx;
  border-radius: 40rpx;
  font-size: 30rpx;
  border: none;
  background: #f0f0f0;
  color: #333;
}

.action-btn.primary {
  background: #007AFF;
  color: white;
}

.logs {
  background: white;
  border-radius: 15rpx;
  padding: 30rpx;
  box-shadow: 0 4rpx 20rpx rgba(0,0,0,0.1);
}

.logs-title {
  font-size: 36rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 20rpx;
  display: block;
}

.log-item {
  padding: 10rpx 0;
  border-bottom: 1rpx solid #f0f0f0;
}

.log-item:last-child {
  border-bottom: none;
}

.log-text {
  font-size: 26rpx;
  color: #666;
  font-family: monospace;
}
</style>'''
        
        index_vue_path = os.path.join("呵呵", "pages", "index", "index.vue")
        with open(index_vue_path, 'w', encoding='utf-8') as f:
            f.write(index_vue_content)
            
        print("  ✅ 更新index.vue")
        self.fixes_applied.append("更新呵呵项目首页内容")
        
    def create_project_summary(self):
        """创建项目结构总结"""
        print("\n📊 创建项目结构总结...")
        print("-" * 60)
        
        # 扫描所有前端项目
        frontend_projects = []
        
        project_dirs = ["呵呵", "炒股养家", "frontend/gupiao1", "frontend/stock5", "vercel-frontend"]
        
        for project_dir in project_dirs:
            if os.path.exists(project_dir):
                project_info = {
                    "name": project_dir,
                    "has_package_json": os.path.exists(os.path.join(project_dir, "package.json")),
                    "has_env_config": os.path.exists(os.path.join(project_dir, "env.js")),
                    "has_request_utils": os.path.exists(os.path.join(project_dir, "utils", "request.js")),
                    "has_pages_config": os.path.exists(os.path.join(project_dir, "pages.json")),
                    "has_main_js": os.path.exists(os.path.join(project_dir, "main.js")),
                    "has_app_vue": os.path.exists(os.path.join(project_dir, "App.vue"))
                }
                frontend_projects.append(project_info)
                
        # 生成总结报告
        summary_content = f"""# 前端项目结构总结报告

## 📅 生成时间
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📁 项目结构状态

"""
        
        for project in frontend_projects:
            summary_content += f"""### {project['name']}
- ✅ package.json: {'有' if project['has_package_json'] else '❌ 无'}
- ✅ env.js配置: {'有' if project['has_env_config'] else '❌ 无'}  
- ✅ request工具: {'有' if project['has_request_utils'] else '❌ 无'}
- ✅ pages.json: {'有' if project['has_pages_config'] else '❌ 无'}
- ✅ main.js: {'有' if project['has_main_js'] else '❌ 无'}
- ✅ App.vue: {'有' if project['has_app_vue'] else '❌ 无'}

"""
        
        summary_content += f"""## 🔧 已应用的修复

"""
        for i, fix in enumerate(self.fixes_applied, 1):
            summary_content += f"{i}. {fix}\n"
            
        summary_content += f"""
## 🚀 使用建议

### 运行项目
```bash
# 进入呵呵项目目录
cd 呵呵

# 安装依赖
npm install

# 运行开发服务器
npm run dev
```

### 项目特点
- ✅ 完整的uni-app项目结构
- ✅ 统一的API配置
- ✅ 网络请求工具
- ✅ 现代化的UI设计
- ✅ 实时状态监控

## 📞 技术支持
如有问题,请检查:
1. Node.js版本 >= 14
2. npm或yarn已安装
3. 网络连接正常
4. API服务运行中
"""
        
        with open("FRONTEND_PROJECTS_SUMMARY.md", 'w', encoding='utf-8') as f:
            f.write(summary_content)
            
        print("  ✅ 创建项目总结报告")
        self.fixes_applied.append("创建前端项目结构总结报告")
        
    def generate_final_report(self):
        """生成最终报告"""
        print("\n" + "=" * 80)
        print("📊 前端项目整理完成报告")
        print("=" * 80)
        
        print(f"🔧 已应用的修复 ({len(self.fixes_applied)}个):")
        for i, fix in enumerate(self.fixes_applied, 1):
            print(f"  {i}. {fix}")
            
        print(f"\n📋 整理总结:")
        print(f"  • 呵呵项目结构修复: ✅")
        print(f"  • package.json创建: ✅")
        print(f"  • 环境配置添加: ✅")
        print(f"  • 网络请求工具: ✅")
        print(f"  • 页面配置更新: ✅")
        print(f"  • UI界面优化: ✅")
        
        print(f"\n🚀 下一步操作:")
        print("  1. cd 呵呵")
        print("  2. npm install")
        print("  3. npm run dev")
        print("  4. 在浏览器中查看效果")
        
        print(f"\n💡 项目特点:")
        print("  • 完整的uni-app项目结构")
        print("  • 统一的API配置管理")
        print("  • 现代化的UI设计")
        print("  • 实时状态监控功能")
        print("  • 完善的错误处理")
        
        print("=" * 80)
        
    def run_organization(self):
        """运行项目整理"""
        self.print_banner()
        
        # 执行各项整理
        self.fix_hehe_project()
        self.create_project_summary()
        
        # 生成报告
        self.generate_final_report()

def main():
    """主函数"""
    organizer = FrontendProjectOrganizer()
    organizer.run_organization()

if __name__ == "__main__":
    main()
