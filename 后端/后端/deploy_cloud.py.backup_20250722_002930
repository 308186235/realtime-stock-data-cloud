#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
云端部署脚本
支持多种云平台部署
"""

import os
import subprocess
import json
import time
from pathlib import Path

class CloudDeployer:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.backend_path = self.project_root / "backend"
        
    def deploy_to_railway(self):
        """部署到Railway"""
        print("🚂 部署到Railway...")
        
        try:
            # 检查Railway CLI
            subprocess.run(["railway", "--version"], check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Railway CLI未安装，请先安装:")
            print("npm install -g @railway/cli")
            return False
        
        try:
            # 登录检查
            result = subprocess.run(["railway", "whoami"], capture_output=True, text=True)
            if result.returncode != 0:
                print("请先登录Railway: railway login")
                return False
            
            # 创建railway.json配置
            railway_config = {
                "build": {
                    "builder": "NIXPACKS"
                },
                "deploy": {
                    "startCommand": "python backend/app.py",
                    "healthcheckPath": "/api/health"
                }
            }
            
            with open("railway.json", "w") as f:
                json.dump(railway_config, f, indent=2)
            
            # 部署
            print("🚀 开始部署...")
            subprocess.run(["railway", "up"], check=True)
            
            # 获取部署URL
            result = subprocess.run(["railway", "domain"], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ 部署成功！")
                print(f"🌐 访问地址: {result.stdout.strip()}")
                return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Railway部署失败: {e}")
            return False
    
    def deploy_to_render(self):
        """部署到Render"""
        print("🎨 准备Render部署配置...")
        
        # 创建render.yaml
        render_config = """
services:
  - type: web
    name: trading-backend
    env: python
    buildCommand: pip install -r backend/requirements.txt
    startCommand: python backend/app.py
    envVars:
      - key: PYTHONPATH
        value: /opt/render/project/src
      - key: PORT
        value: 8000
    healthCheckPath: /api/health
"""
        
        with open("render.yaml", "w") as f:
            f.write(render_config)
        
        print("✅ Render配置已创建")
        print("📝 请按以下步骤操作:")
        print("1. 访问 https://render.com")
        print("2. 连接GitHub仓库")
        print("3. 选择Web Service")
        print("4. 使用render.yaml配置")
        
        return True
    
    def deploy_to_fly(self):
        """部署到Fly.io"""
        print("🪰 部署到Fly.io...")
        
        try:
            # 检查flyctl
            subprocess.run(["flyctl", "version"], check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ flyctl未安装，请先安装:")
            print("https://fly.io/docs/getting-started/installing-flyctl/")
            return False
        
        # 创建fly.toml
        fly_config = """
app = "trading-system"
kill_signal = "SIGINT"
kill_timeout = 5
processes = []

[env]
  PYTHONPATH = "/app"
  PORT = "8000"

[experimental]
  auto_rollback = true

[[services]]
  http_checks = []
  internal_port = 8000
  processes = ["app"]
  protocol = "tcp"
  script_checks = []
  [services.concurrency]
    hard_limit = 25
    soft_limit = 20
    type = "connections"

  [[services.ports]]
    force_https = true
    handlers = ["http"]
    port = 80

  [[services.ports]]
    handlers = ["tls", "http"]
    port = 443

  [[services.tcp_checks]]
    grace_period = "1s"
    interval = "15s"
    restart_limit = 0
    timeout = "2s"

  [[services.http_checks]]
    interval = "10s"
    grace_period = "5s"
    method = "get"
    path = "/api/health"
    protocol = "http"
    timeout = "2s"
    tls_skip_verify = false
"""
        
        with open("fly.toml", "w") as f:
            f.write(fly_config)
        
        try:
            # 初始化应用
            subprocess.run(["flyctl", "launch", "--no-deploy"], check=True)
            
            # 部署
            print("🚀 开始部署...")
            subprocess.run(["flyctl", "deploy"], check=True)
            
            print("✅ Fly.io部署成功！")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Fly.io部署失败: {e}")
            return False
    
    def deploy_docker(self):
        """Docker部署"""
        print("🐳 Docker部署...")
        
        try:
            # 构建镜像
            print("📦 构建Docker镜像...")
            subprocess.run([
                "docker", "build", 
                "-t", "trading-system:latest", 
                "."
            ], check=True)
            
            # 运行容器
            print("🚀 启动容器...")
            subprocess.run([
                "docker", "run", 
                "-d", 
                "--name", "trading-system",
                "-p", "8000:8000",
                "-v", f"{self.project_root}/data:/app/data",
                "-v", f"{self.project_root}/logs:/app/logs",
                "trading-system:latest"
            ], check=True)
            
            print("✅ Docker部署成功！")
            print("🌐 访问地址: http://localhost:8000")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Docker部署失败: {e}")
            return False
    
    def create_requirements(self):
        """创建requirements.txt"""
        requirements = """
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
sqlite3
pandas==2.1.3
numpy==1.24.3
requests==2.31.0
websockets==12.0
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.0
redis==5.0.1
celery==5.3.4
apscheduler==3.10.4
pydantic==2.5.0
httpx==0.25.2
aiofiles==23.2.1
"""
        
        requirements_path = self.backend_path / "requirements.txt"
        if not requirements_path.exists():
            with open(requirements_path, "w") as f:
                f.write(requirements.strip())
            print(f"✅ 已创建 {requirements_path}")

def main():
    deployer = CloudDeployer()
    
    print("🌐 云端部署工具")
    print("=" * 50)
    print("1. Railway (推荐 - 免费)")
    print("2. Render (稳定 - 免费)")
    print("3. Fly.io (性能好)")
    print("4. Docker本地")
    print("5. 创建requirements.txt")
    print("=" * 50)
    
    choice = input("请选择部署方式 (1-5): ").strip()
    
    # 确保requirements.txt存在
    deployer.create_requirements()
    
    if choice == "1":
        deployer.deploy_to_railway()
    elif choice == "2":
        deployer.deploy_to_render()
    elif choice == "3":
        deployer.deploy_to_fly()
    elif choice == "4":
        deployer.deploy_docker()
    elif choice == "5":
        print("✅ requirements.txt已创建")
    else:
        print("❌ 无效选择")

if __name__ == "__main__":
    main()
