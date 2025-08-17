#!/usr/bin/env python3
"""
云端部署准备脚本
为Cloudflare Workers/Pages和阿里云部署准备文件
"""
import os
import json
import shutil
from datetime import datetime

class CloudDeploymentPreparator:
    def __init__(self):
        self.project_name = "ai-stock-trading-system"
        self.build_dir = "cloud_deployment"
        
    def create_deployment_structure(self):
        """创建部署目录结构"""
        print("📁 创建部署目录结构...")
        
        # 清理并创建主目录
        if os.path.exists(self.build_dir):
            shutil.rmtree(self.build_dir)
        
        # 创建目录结构
        dirs = [
            f"{self.build_dir}/frontend",
            f"{self.build_dir}/backend", 
            f"{self.build_dir}/config",
            f"{self.build_dir}/docs",
            f"{self.build_dir}/cloudflare",
            f"{self.build_dir}/aliyun"
        ]
        
        for dir_path in dirs:
            os.makedirs(dir_path, exist_ok=True)
            print(f"   ✅ 创建目录: {dir_path}")
        
        return True
    
    def prepare_frontend_files(self):
        """准备前端文件"""
        print("🎨 准备前端文件...")
        
        frontend_mappings = [
            ('frontend/simple_frontend.html', 'frontend/index.html'),
            ('frontend/realtime_data_monitor.html', 'frontend/monitor.html'),
            ('frontend/test_supabase_frontend.html', 'frontend/test.html')
        ]
        
        # 复制HTML文件
        for src, dest in frontend_mappings:
            if os.path.exists(src):
                dest_path = os.path.join(self.build_dir, dest)
                shutil.copy2(src, dest_path)
                print(f"   ✅ 复制: {src} -> {dest}")
        
        # 复制JavaScript服务文件
        js_dir = os.path.join(self.build_dir, 'frontend/js')
        os.makedirs(js_dir, exist_ok=True)
        
        js_files = [
            'frontend/services/aiService.js',
            'frontend/services/marketDataService.js',
            'frontend/services/auth-service.js'
        ]
        
        for js_file in js_files:
            if os.path.exists(js_file):
                filename = os.path.basename(js_file)
                dest_path = os.path.join(js_dir, filename)
                shutil.copy2(js_file, dest_path)
                print(f"   ✅ 复制JS: {filename}")
        
        return True
    
    def prepare_backend_files(self):
        """准备后端文件"""
        print("⚙️ 准备后端文件...")
        
        # 复制主要后端文件
        backend_files = [
            'backend/main.py',
            'backend/config/database.py',
            'backend/config/supabase.py',
            'backend/api/auth.py',
            'backend/api/stocks.py',
            'backend/api/trades.py'
        ]
        
        for src_file in backend_files:
            if os.path.exists(src_file):
                # 保持目录结构
                rel_path = os.path.relpath(src_file, 'backend')
                dest_path = os.path.join(self.build_dir, 'backend', rel_path)
                
                # 创建目标目录
                dest_dir = os.path.dirname(dest_path)
                os.makedirs(dest_dir, exist_ok=True)
                
                shutil.copy2(src_file, dest_path)
                print(f"   ✅ 复制: {src_file}")
        
        # 复制requirements.txt
        if os.path.exists('requirements.txt'):
            shutil.copy2('requirements.txt', os.path.join(self.build_dir, 'backend/requirements.txt'))
            print("   ✅ 复制: requirements.txt")
        
        return True
    
    def create_cloudflare_config(self):
        """创建Cloudflare配置"""
        print("☁️ 创建Cloudflare配置...")
        
        # Worker配置
        worker_config = {
            "name": f"{self.project_name}-api",
            "main": "worker.js",
            "compatibility_date": "2024-01-01",
            "vars": {
                "ENVIRONMENT": "production"
            }
        }
        
        # 生成wrangler.toml
        wrangler_toml = f"""name = "{worker_config['name']}"
main = "{worker_config['main']}"
compatibility_date = "{worker_config['compatibility_date']}"

[vars]
ENVIRONMENT = "production"
SUPABASE_URL = "https://zzukfxwavknskqcepsjb.supabase.co"

# 使用 wrangler secret put 命令设置以下密钥:
# wrangler secret put SUPABASE_KEY
# wrangler secret put SUPABASE_SERVICE_KEY
# wrangler secret put JWT_SECRET_KEY
"""
        
        with open(os.path.join(self.build_dir, 'cloudflare/wrangler.toml'), 'w', encoding='utf-8') as f:
            f.write(wrangler_toml)
        
        # 生成Worker脚本
        worker_js = '''/**
 * AI股票交易系统 - Cloudflare Worker
 */

// CORS配置
const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization',
};

// 处理CORS预检请求
function handleCORS(request) {
  if (request.method === 'OPTIONS') {
    return new Response(null, { status: 200, headers: corsHeaders });
  }
  return null;
}

// 主要API处理
async function handleAPI(request, env) {
  const url = new URL(request.url);
  const path = url.pathname;
  
  // 健康检查
  if (path === '/api/health') {
    return new Response(JSON.stringify({
      status: 'ok',
      timestamp: new Date().toISOString(),
      service: 'ai-stock-trading-system',
      environment: env.ENVIRONMENT || 'production'
    }), {
      headers: { 'Content-Type': 'application/json', ...corsHeaders }
    });
  }
  
  // 股票数据API
  if (path === '/api/stocks/list') {
    const mockStocks = [
      { symbol: 'AAPL', name: 'Apple Inc.', price: 150.25, change: 2.5 },
      { symbol: 'GOOGL', name: 'Alphabet Inc.', price: 2800.50, change: -15.25 },
      { symbol: 'MSFT', name: 'Microsoft Corp.', price: 300.75, change: 5.10 },
      { symbol: 'TSLA', name: 'Tesla Inc.', price: 800.25, change: 25.50 }
    ];
    
    return new Response(JSON.stringify({
      success: true,
      data: mockStocks,
      timestamp: new Date().toISOString()
    }), {
      headers: { 'Content-Type': 'application/json', ...corsHeaders }
    });
  }
  
  // 用户认证API
  if (path.startsWith('/api/auth')) {
    return new Response(JSON.stringify({
      message: 'Authentication API',
      status: 'available'
    }), {
      headers: { 'Content-Type': 'application/json', ...corsHeaders }
    });
  }
  
  // 404处理
  return new Response(JSON.stringify({
    error: 'Not Found',
    path: path
  }), {
    status: 404,
    headers: { 'Content-Type': 'application/json', ...corsHeaders }
  });
}

// 主处理函数
export default {
  async fetch(request, env, ctx) {
    try {
      // 处理CORS
      const corsResponse = handleCORS(request);
      if (corsResponse) return corsResponse;
      
      // 处理API请求
      return await handleAPI(request, env);
      
    } catch (error) {
      return new Response(JSON.stringify({
        error: 'Internal Server Error',
        message: error.message
      }), {
        status: 500,
        headers: { 'Content-Type': 'application/json', ...corsHeaders }
      });
    }
  }
};
'''
        
        with open(os.path.join(self.build_dir, 'cloudflare/worker.js'), 'w', encoding='utf-8') as f:
            f.write(worker_js)
        
        print("   ✅ Cloudflare配置文件已创建")
        return True
    
    def create_aliyun_config(self):
        """创建阿里云配置"""
        print("🐧 创建阿里云配置...")
        
        # Docker配置
        dockerfile = '''FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# 复制requirements并安装Python依赖
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY backend/ ./backend/
COPY config/ ./config/

# 设置环境变量
ENV PYTHONPATH=/app
ENV PORT=8000

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
'''
        
        with open(os.path.join(self.build_dir, 'aliyun/Dockerfile'), 'w', encoding='utf-8') as f:
            f.write(dockerfile)
        
        # Docker Compose配置
        docker_compose = '''version: '3.8'

services:
  ai-stock-trading-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - SUPABASE_URL=https://zzukfxwavknskqcepsjb.supabase.co
      - SUPABASE_KEY=${SUPABASE_KEY}
      - SUPABASE_SERVICE_KEY=${SUPABASE_SERVICE_KEY}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - TRADING_MODE=live
    restart: unless-stopped
    
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - ai-stock-trading-api
    restart: unless-stopped
'''
        
        with open(os.path.join(self.build_dir, 'aliyun/docker-compose.yml'), 'w', encoding='utf-8') as f:
            f.write(docker_compose)
        
        print("   ✅ 阿里云配置文件已创建")
        return True
    
    def create_deployment_docs(self):
        """创建部署文档"""
        print("📚 创建部署文档...")
        
        # 主部署指南
        main_guide = f"""# AI股票交易系统 - 云端部署指南

## 项目概述
- **项目名称**: {self.project_name}
- **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **部署目标**: Cloudflare Workers/Pages + 阿里云

## 部署选项

### 选项1: Cloudflare Workers + Pages
**优势**: 全球CDN,自动扩展,成本低
**适用**: 轻量级应用,全球用户

#### 部署步骤:
1. 安装Wrangler CLI: `npm install -g wrangler`
2. 登录Cloudflare: `wrangler auth login`
3. 部署Worker: `cd cloudflare && wrangler deploy`
4. 部署Pages: `wrangler pages deploy ../frontend --project-name {self.project_name}`

### 选项2: 阿里云容器服务
**优势**: 完整后端支持,数据库集成,国内访问快
**适用**: 企业级应用,复杂业务逻辑

#### 部署步骤:
1. 构建Docker镜像: `cd aliyun && docker build -t {self.project_name} .`
2. 推送到阿里云镜像仓库
3. 使用容器服务部署: `docker-compose up -d`

## 配置要求

### 环境变量
- `SUPABASE_URL`: Supabase项目URL
- `SUPABASE_KEY`: Supabase匿名密钥
- `SUPABASE_SERVICE_KEY`: Supabase服务密钥
- `JWT_SECRET_KEY`: JWT签名密钥

### 域名配置
- 配置DNS记录指向部署服务
- 设置SSL证书(推荐Let's Encrypt)

## 监控和维护
- 设置日志监控
- 配置性能告警
- 定期备份数据

## 成本估算
- **Cloudflare**: 免费额度 + 按使用量付费
- **阿里云**: 按实例规格和流量计费

详细配置请参考各平台的具体文档。
"""
        
        with open(os.path.join(self.build_dir, 'docs/DEPLOYMENT_GUIDE.md'), 'w', encoding='utf-8') as f:
            f.write(main_guide)
        
        print("   ✅ 部署指南已创建")
        return True
    
    def prepare_deployment(self):
        """执行完整的部署准备"""
        print("🚀 开始云端部署准备...")
        print("=" * 50)
        
        try:
            # 创建目录结构
            self.create_deployment_structure()
            
            # 准备文件
            self.prepare_frontend_files()
            self.prepare_backend_files()
            
            # 创建配置
            self.create_cloudflare_config()
            self.create_aliyun_config()
            
            # 创建文档
            self.create_deployment_docs()
            
            # 复制配置文件
            config_files = ['.env.production', 'supabase_init.sql', 'nginx.conf']
            for config_file in config_files:
                if os.path.exists(config_file):
                    shutil.copy2(config_file, os.path.join(self.build_dir, 'config', config_file))
                    print(f"   ✅ 复制配置: {config_file}")
            
            print("\n🎉 云端部署准备完成!")
            print(f"📁 部署文件位置: {self.build_dir}/")
            print("\n📋 下一步操作:")
            print("1. 查看部署指南: cloud_deployment/docs/DEPLOYMENT_GUIDE.md")
            print("2. 选择部署平台: Cloudflare 或 阿里云")
            print("3. 配置环境变量和域名")
            print("4. 执行部署命令")
            
            return True
            
        except Exception as e:
            print(f"❌ 部署准备失败: {e}")
            return False

def main():
    """主函数"""
    preparator = CloudDeploymentPreparator()
    return preparator.prepare_deployment()

if __name__ == "__main__":
    try:
        result = main()
        exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️ 部署准备被用户中断")
        exit(1)
