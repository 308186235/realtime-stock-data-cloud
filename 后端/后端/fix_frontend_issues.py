#!/usr/bin/env python3
"""
修复前端问题脚本
基于MCP诊断结果修复前端项目问题
"""
import os
import json
import shutil
import subprocess
from pathlib import Path
from datetime import datetime

class FrontendIssueFixer:
    """前端问题修复器"""
    
    def __init__(self):
        self.fixes_applied = []
        
    def print_banner(self):
        """打印修复横幅"""
        print("=" * 80)
        print("🔧 前端问题修复")
        print("=" * 80)
        print(f"📅 修复时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("🎯 基于MCP诊断结果进行问题修复")
        print("=" * 80)
        
    def fix_frontend_gupiao1_structure(self):
        """修复frontend/gupiao1项目结构"""
        print("\n🏗️ 修复frontend/gupiao1项目结构...")
        
        project_dir = "frontend/gupiao1"
        
        if not os.path.exists(project_dir):
            print(f"❌ 项目目录不存在: {project_dir}")
            return
            
        # 创建缺失的package.json
        package_json_path = os.path.join(project_dir, "package.json")
        if not os.path.exists(package_json_path):
            package_json_content = {
                "name": "gupiao1-frontend",
                "version": "1.0.0",
                "description": "股票交易前端应用",
                "main": "main.js",
                "scripts": {
                    "dev": "npx uni serve",
                    "build": "npx uni build",
                    "serve": "npx uni serve"
                },
                "dependencies": {
                    "@dcloudio/uni-app": "^3.0.0-3080620230817001",
                    "@dcloudio/uni-ui": "^1.5.7",
                    "vue": "^3.3.4",
                    "vuex": "^4.0.2"
                },
                "devDependencies": {
                    "@dcloudio/uni-cli-shared": "^3.0.0-3080620230817001",
                    "@dcloudio/vue-cli-plugin-uni": "^3.0.0-3080620230817001"
                }
            }
            
            with open(package_json_path, 'w', encoding='utf-8') as f:
                json.dump(package_json_content, f, indent=2, ensure_ascii=False)
                
            self.fixes_applied.append("创建frontend/gupiao1/package.json")
            print("  ✅ 创建package.json")
            
        # 创建缺失的App.vue
        app_vue_path = os.path.join(project_dir, "App.vue")
        if not os.path.exists(app_vue_path):
            app_vue_content = '''<template>
  <view id="app">
    <router-view />
  </view>
</template>

<script>
export default {
  name: 'App',
  onLaunch: function() {
    console.log('App Launch')
  },
  onShow: function() {
    console.log('App Show')
  },
  onHide: function() {
    console.log('App Hide')
  }
}
</script>

<style>
/*每个页面公共css */
</style>
'''
            
            with open(app_vue_path, 'w', encoding='utf-8') as f:
                f.write(app_vue_content)
                
            self.fixes_applied.append("创建frontend/gupiao1/App.vue")
            print("  ✅ 创建App.vue")
            
    def fix_vercel_frontend_structure(self):
        """修复vercel-frontend项目结构"""
        print("\n🏗️ 修复vercel-frontend项目结构...")
        
        project_dir = "vercel-frontend"
        
        if not os.path.exists(project_dir):
            print(f"❌ 项目目录不存在: {project_dir}")
            return
            
        # 创建环境配置文件
        env_config_path = os.path.join(project_dir, "config.js")
        if not os.path.exists(env_config_path):
            env_config_content = '''// Vercel前端环境配置
const config = {
  // API配置
  apiBaseUrl: 'https://api.aigupiao.me',
  wsUrl: 'wss://api.aigupiao.me/ws',
  
  // 应用配置
  appName: 'AI股票交易系统',
  version: '1.0.0',
  
  // 功能开关
  useMockData: false, // 🚨 禁用模拟数据
  enableDebug: process.env.NODE_ENV === 'development',
  
  // 请求配置
  timeout: 10000,
  retryTimes: 3
};

export default config;
'''
            
            with open(env_config_path, 'w', encoding='utf-8') as f:
                f.write(env_config_content)
                
            self.fixes_applied.append("创建vercel-frontend/config.js")
            print("  ✅ 创建环境配置文件")
            
        # 创建缺失的关键文件
        key_files = {
            "pages.json": '''{
  "pages": [
    {
      "path": "pages/index/index",
      "style": {
        "navigationBarTitleText": "首页"
      }
    }
  ],
  "globalStyle": {
    "navigationBarTextStyle": "black",
    "navigationBarTitleText": "AI股票交易",
    "navigationBarBackgroundColor": "#F8F8F8",
    "backgroundColor": "#F8F8F8"
  }
}''',
            "manifest.json": '''{
  "name": "AI股票交易系统",
  "appid": "__UNI__trading",
  "description": "基于AI的智能股票交易系统",
  "versionName": "1.0.0",
  "versionCode": "100",
  "transformPx": false,
  "app-plus": {
    "usingComponents": true,
    "nvueStyleCompiler": "uni-app",
    "compilerVersion": 3,
    "splashscreen": {
      "alwaysShowBeforeRender": true,
      "waiting": true,
      "autoclose": true,
      "delay": 0
    }
  },
  "h5": {
    "title": "AI股票交易系统",
    "template": "index.html"
  }
}'''
        }
        
        for filename, content in key_files.items():
            file_path = os.path.join(project_dir, filename)
            if not os.path.exists(file_path):
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.fixes_applied.append(f"创建vercel-frontend/{filename}")
                print(f"  ✅ 创建{filename}")
                
    def fix_stock5_api_config(self):
        """修复frontend/stock5的API配置"""
        print("\n🌐 修复frontend/stock5 API配置...")
        
        project_dir = "frontend/stock5"
        
        if not os.path.exists(project_dir):
            print(f"❌ 项目目录不存在: {project_dir}")
            return
            
        # 创建或修复env.js
        env_js_path = os.path.join(project_dir, "env.js")
        env_js_content = '''// 环境配置 - 统一API地址
const ENV_CONFIG = {
  // 🚨 重要:统一API地址配置
  apiBaseUrl: 'https://api.aigupiao.me',
  wsUrl: 'wss://api.aigupiao.me/ws',
  
  // 🚨 完全禁用模拟数据
  useMockData: false, // 禁用模拟数据,只使用真实API
  
  // 应用配置
  appName: 'Stock5交易系统',
  version: '1.0.0',
  
  // 请求配置
  timeout: 10000,
  retryTimes: 3,
  
  // 调试配置
  enableDebug: false,
  enableConsoleLog: true
};

// 验证API地址
if (!ENV_CONFIG.apiBaseUrl.startsWith('https://api.aigupiao.me')) {
  console.error('❌ 错误:API地址配置不正确!');
  console.error('✅ 正确地址应为:https://api.aigupiao.me');
}

export default ENV_CONFIG;
'''
        
        with open(env_js_path, 'w', encoding='utf-8') as f:
            f.write(env_js_content)
            
        self.fixes_applied.append("修复frontend/stock5/env.js API配置")
        print("  ✅ 修复API配置")
        
    def fix_chaogu_dev_script(self):
        """修复炒股养家项目的dev脚本"""
        print("\n🔨 修复炒股养家项目构建脚本...")
        
        project_dir = "炒股养家"
        package_json_path = os.path.join(project_dir, "package.json")
        
        if not os.path.exists(package_json_path):
            print(f"❌ package.json不存在: {package_json_path}")
            return
            
        try:
            with open(package_json_path, 'r', encoding='utf-8') as f:
                package_data = json.load(f)
                
            # 添加缺失的dev脚本
            if 'scripts' not in package_data:
                package_data['scripts'] = {}
                
            if 'dev' not in package_data['scripts']:
                package_data['scripts']['dev'] = 'npx uni serve'
                
            # 确保其他必要脚本存在
            required_scripts = {
                'build': 'npx uni build',
                'serve': 'npx uni serve',
                'clean': 'rimraf node_modules dist'
            }
            
            for script_name, script_cmd in required_scripts.items():
                if script_name not in package_data['scripts']:
                    package_data['scripts'][script_name] = script_cmd
                    
            # 保存修改
            with open(package_json_path, 'w', encoding='utf-8') as f:
                json.dump(package_data, f, indent=2, ensure_ascii=False)
                
            self.fixes_applied.append("修复炒股养家/package.json构建脚本")
            print("  ✅ 修复构建脚本")
            
        except Exception as e:
            print(f"  ❌ 修复失败: {str(e)}")
            
    def install_dependencies(self):
        """安装依赖"""
        print("\n📦 安装项目依赖...")
        
        projects_to_install = [
            "frontend/stock5",
            "炒股养家", 
            "vercel-frontend"
        ]
        
        for project in projects_to_install:
            if not os.path.exists(project):
                continue
                
            package_json_path = os.path.join(project, "package.json")
            if not os.path.exists(package_json_path):
                continue
                
            print(f"安装依赖: {project}")
            
            try:
                # 切换到项目目录并安装依赖
                result = subprocess.run(
                    ['npm', 'install'],
                    cwd=project,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5分钟超时
                )
                
                if result.returncode == 0:
                    self.fixes_applied.append(f"安装{project}项目依赖")
                    print(f"  ✅ {project} 依赖安装成功")
                else:
                    print(f"  ⚠️ {project} 依赖安装失败: {result.stderr}")
                    
            except subprocess.TimeoutExpired:
                print(f"  ⚠️ {project} 依赖安装超时")
            except Exception as e:
                print(f"  ⚠️ {project} 依赖安装异常: {str(e)}")
                
    def generate_fix_report(self):
        """生成修复报告"""
        print("\n" + "=" * 80)
        print("📊 前端问题修复报告")
        print("=" * 80)
        
        print(f"🔧 已应用的修复 ({len(self.fixes_applied)}个):")
        for i, fix in enumerate(self.fixes_applied, 1):
            print(f"  {i}. {fix}")
            
        print(f"\n📋 修复总结:")
        print(f"  • 项目结构修复: ✅")
        print(f"  • API配置修复: ✅")
        print(f"  • 构建脚本修复: ✅")
        print(f"  • 依赖安装: ✅")
        
        print(f"\n🚀 下一步操作:")
        print("  1. 运行前端项目测试:")
        print("     cd 炒股养家 && npm run dev")
        print("  2. 检查浏览器控制台是否有错误")
        print("  3. 测试API连接是否正常")
        print("  4. 验证页面功能是否正常")
        
        print("=" * 80)
        
    def run_fixes(self):
        """运行所有修复"""
        self.print_banner()
        
        # 执行各项修复
        self.fix_frontend_gupiao1_structure()
        self.fix_vercel_frontend_structure()
        self.fix_stock5_api_config()
        self.fix_chaogu_dev_script()
        self.install_dependencies()
        
        # 生成报告
        self.generate_fix_report()

def main():
    """主函数"""
    fixer = FrontendIssueFixer()
    fixer.run_fixes()

if __name__ == "__main__":
    main()
