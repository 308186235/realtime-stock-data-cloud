#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP Cloudflare Worker 修复工具
解决 "此路由上没有了 worker" 问题
"""

import os
import json
import time
import subprocess
import requests
from datetime import datetime

class MCPCloudflareWorkerFix:
    def __init__(self):
        self.domain = "aigupiao.me"
        self.worker_name = "aigupiao-subdomain-router"
        self.routes = [
            "aigupiao.me/*",
            "admin.aigupiao.me/*", 
            "mobile.aigupiao.me/*",
            "api.aigupiao.me/*",
            "app.aigupiao.me/*"
        ]
        
    def log(self, message, level="INFO"):
        """日志输出"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        colors = {
            "INFO": "\033[36m",     # 青色
            "SUCCESS": "\033[32m",  # 绿色
            "WARNING": "\033[33m",  # 黄色
            "ERROR": "\033[31m",    # 红色
            "RESET": "\033[0m"      # 重置
        }
        
        color = colors.get(level, colors["INFO"])
        reset = colors["RESET"]
        print(f"{color}[{timestamp}] {message}{reset}")
    
    def create_simple_worker_code(self):
        """创建简化的 Worker 代码"""
        worker_code = '''
/**
 * 简化版 Cloudflare Worker - aigupiao.me 路由系统
 * MCP 修复版本
 */

addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
  const url = new URL(request.url)
  const hostname = url.hostname
  const pathname = url.pathname
  
  // 添加CORS头
  const corsHeaders = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With'
  }
  
  // 处理预检请求
  if (request.method === 'OPTIONS') {
    return new Response(null, {
      status: 200,
      headers: corsHeaders
    })
  }
  
  try {
    // 路由处理
    switch(hostname) {
      case 'app.aigupiao.me':
        return handleAppDomain(pathname, request, corsHeaders)
      case 'api.aigupiao.me':
        return handleAPIDomain(pathname, request, corsHeaders)
      case 'mobile.aigupiao.me':
        return handleMobileDomain(pathname, request, corsHeaders)
      case 'admin.aigupiao.me':
        return handleAdminDomain(pathname, request, corsHeaders)
      case 'aigupiao.me':
      case 'www.aigupiao.me':
        return handleMainDomain(pathname, request, corsHeaders)
      default:
        return createResponse(`Worker路由成功 - 域名: ${hostname}`, 200, corsHeaders)
    }
  } catch (error) {
    return createResponse(`路由错误: ${error.message}`, 500, corsHeaders)
  }
}

// 主应用域名处理
async function handleAppDomain(pathname, request, corsHeaders) {
  if (pathname === '/test') {
    return createResponse('App域名测试成功', 200, corsHeaders)
  }
  
  // 代理到 Pages
  return proxyToPages(pathname, request, corsHeaders)
}

// API域名处理
async function handleAPIDomain(pathname, request, corsHeaders) {
  if (pathname === '/health') {
    return createResponse(JSON.stringify({
      status: 'healthy',
      timestamp: new Date().toISOString(),
      worker: 'aigupiao-subdomain-router',
      version: '1.0.0-mcp-fix'
    }), 200, corsHeaders, 'application/json')
  }
  
  if (pathname === '/test') {
    return createResponse('API域名测试成功', 200, corsHeaders)
  }
  
  // 代理到后端API
  return proxyToBackend(pathname, request, corsHeaders)
}

// 移动端域名处理
async function handleMobileDomain(pathname, request, corsHeaders) {
  if (pathname === '/test') {
    return createResponse('Mobile域名测试成功', 200, corsHeaders)
  }
  
  return proxyToPages('/mobile.html', request, corsHeaders)
}

// 管理后台域名处理
async function handleAdminDomain(pathname, request, corsHeaders) {
  if (pathname === '/test') {
    return createResponse('Admin域名测试成功', 200, corsHeaders)
  }
  
  return proxyToPages('/admin.html', request, corsHeaders)
}

// 主站域名处理
async function handleMainDomain(pathname, request, corsHeaders) {
  if (pathname === '/test') {
    return createResponse('主站域名测试成功', 200, corsHeaders)
  }
  
  return proxyToPages(pathname, request, corsHeaders)
}

// 代理到 Cloudflare Pages
async function proxyToPages(pathname, request, corsHeaders) {
  const targetUrl = `https://bei-fen.pages.dev${pathname}`
  
  try {
    const response = await fetch(targetUrl, {
      method: request.method,
      headers: request.headers,
      body: request.method !== 'GET' && request.method !== 'HEAD' ? request.body : undefined
    })
    
    const newResponse = new Response(response.body, {
      status: response.status,
      statusText: response.statusText,
      headers: {
        ...Object.fromEntries(response.headers.entries()),
        ...corsHeaders
      }
    })
    
    return newResponse
  } catch (error) {
    return createResponse(`Pages代理错误: ${error.message}`, 502, corsHeaders)
  }
}

// 代理到后端API
async function proxyToBackend(pathname, request, corsHeaders) {
  const backendUrl = `https://trading-system-api.netlify.app${pathname}`
  
  try {
    const response = await fetch(backendUrl, {
      method: request.method,
      headers: request.headers,
      body: request.method !== 'GET' && request.method !== 'HEAD' ? request.body : undefined
    })
    
    const newResponse = new Response(response.body, {
      status: response.status,
      statusText: response.statusText,
      headers: {
        ...Object.fromEntries(response.headers.entries()),
        ...corsHeaders
      }
    })
    
    return newResponse
  } catch (error) {
    return createResponse(`API代理错误: ${error.message}`, 502, corsHeaders)
  }
}

// 创建响应
function createResponse(content, status = 200, headers = {}, contentType = 'text/plain') {
  return new Response(content, {
    status: status,
    headers: {
      'Content-Type': `${contentType}; charset=utf-8`,
      ...headers
    }
  })
}
'''
        
        # 保存 Worker 代码到文件
        with open('simple_worker.js', 'w', encoding='utf-8') as f:
            f.write(worker_code.strip())
        
        self.log("✅ Worker 代码已生成: simple_worker.js", "SUCCESS")
        return 'simple_worker.js'
    
    def show_manual_fix_steps(self):
        """显示手动修复步骤"""
        self.log("🔧 MCP 手动修复步骤:", "INFO")
        self.log("="*60)
        
        self.log("📋 步骤1: 创建新的 Worker", "INFO")
        self.log("   1. 访问 Cloudflare Dashboard")
        self.log("   2. 进入 Workers & Pages")
        self.log("   3. 点击 'Create application'")
        self.log("   4. 选择 'Create Worker'")
        self.log(f"   5. 命名为: {self.worker_name}")
        
        self.log("\n📋 步骤2: 部署 Worker 代码", "INFO")
        self.log("   1. 复制 simple_worker.js 中的代码")
        self.log("   2. 粘贴到 Worker 编辑器")
        self.log("   3. 点击 'Save and Deploy'")
        
        self.log("\n📋 步骤3: 配置路由", "INFO")
        self.log("   1. 在 Worker 页面点击 'Triggers'")
        self.log("   2. 点击 'Add route'")
        self.log("   3. 添加以下路由:")
        for route in self.routes:
            self.log(f"      - {route}")
        
        self.log("\n📋 步骤4: 测试验证", "INFO")
        self.log("   测试以下地址:")
        self.log("   - https://api.aigupiao.me/test")
        self.log("   - https://app.aigupiao.me/test")
        self.log("   - https://mobile.aigupiao.me/test")
        self.log("   - https://admin.aigupiao.me/test")
        self.log("   - https://aigupiao.me/test")
        
    def create_wrangler_config(self):
        """创建 Wrangler 配置文件"""
        config = {
            "name": self.worker_name,
            "main": "simple_worker.js",
            "compatibility_date": "2024-01-01",
            "routes": [
                {"pattern": route, "zone_name": self.domain}
                for route in self.routes
            ]
        }
        
        with open('wrangler.toml', 'w', encoding='utf-8') as f:
            f.write(f"""name = "{self.worker_name}"
main = "simple_worker.js"
compatibility_date = "2024-01-01"

[[routes]]
pattern = "aigupiao.me/*"
zone_name = "aigupiao.me"

[[routes]]
pattern = "*.aigupiao.me/*"
zone_name = "aigupiao.me"
""")
        
        self.log("✅ Wrangler 配置已生成: wrangler.toml", "SUCCESS")
        
    def run_mcp_fix(self):
        """运行 MCP 修复流程"""
        self.log("🚀 开始 MCP Cloudflare Worker 修复...")
        self.log(f"目标域名: {self.domain}")
        self.log(f"Worker名称: {self.worker_name}")
        self.log("="*60)
        
        # 1. 生成 Worker 代码
        worker_file = self.create_simple_worker_code()
        
        # 2. 生成 Wrangler 配置
        self.create_wrangler_config()
        
        # 3. 显示修复步骤
        self.show_manual_fix_steps()
        
        # 4. 生成快速测试脚本
        self.create_test_script()
        
        self.log("\n🎉 MCP 修复准备完成！", "SUCCESS")
        self.log("请按照上述步骤手动完成 Worker 部署", "INFO")
        
    def create_test_script(self):
        """创建测试脚本"""
        test_script = '''#!/usr/bin/env python3
import requests
import time

def test_worker_routes():
    """测试 Worker 路由"""
    routes = [
        "https://api.aigupiao.me/test",
        "https://app.aigupiao.me/test", 
        "https://mobile.aigupiao.me/test",
        "https://admin.aigupiao.me/test",
        "https://aigupiao.me/test"
    ]
    
    print("🧪 测试 Worker 路由...")
    print("="*50)
    
    for url in routes:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"✅ {url} - 成功")
            else:
                print(f"❌ {url} - 状态码: {response.status_code}")
        except Exception as e:
            print(f"❌ {url} - 错误: {e}")
        
        time.sleep(1)
    
    print("\\n🔍 测试健康检查...")
    try:
        response = requests.get("https://api.aigupiao.me/health", timeout=10)
        if response.status_code == 200:
            print("✅ 健康检查成功")
            print(f"响应: {response.text}")
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 健康检查错误: {e}")

if __name__ == "__main__":
    test_worker_routes()
'''
        
        with open('test_worker.py', 'w', encoding='utf-8') as f:
            f.write(test_script)
        
        self.log("✅ 测试脚本已生成: test_worker.py", "SUCCESS")

if __name__ == "__main__":
    fixer = MCPCloudflareWorkerFix()
    fixer.run_mcp_fix()
