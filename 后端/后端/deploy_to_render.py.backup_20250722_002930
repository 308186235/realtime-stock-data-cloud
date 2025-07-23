#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动化Render部署脚本
"""

import subprocess
import requests
import time
import json
from pathlib import Path

class RenderDeployer:
    """Render自动部署器"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.render_url = None
    
    def check_git_status(self):
        """检查Git状态"""
        print("📋 检查Git状态...")
        
        try:
            # 检查是否有未提交的更改
            result = subprocess.run(
                ["git", "status", "--porcelain"], 
                capture_output=True, 
                text=True,
                cwd=self.project_root
            )
            
            if result.stdout.strip():
                print("⚠️ 发现未提交的更改:")
                print(result.stdout)
                
                commit = input("是否提交这些更改? (y/n): ").lower()
                if commit == 'y':
                    return self.commit_changes()
                else:
                    print("❌ 请先提交更改后再部署")
                    return False
            else:
                print("✅ Git状态正常")
                return True
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Git检查失败: {e}")
            return False
    
    def commit_changes(self):
        """提交更改"""
        try:
            # 添加所有文件
            subprocess.run(["git", "add", "."], check=True, cwd=self.project_root)
            
            # 提交
            commit_msg = f"Render部署配置 - {time.strftime('%Y-%m-%d %H:%M:%S')}"
            subprocess.run(
                ["git", "commit", "-m", commit_msg], 
                check=True, 
                cwd=self.project_root
            )
            
            # 推送
            subprocess.run(["git", "push"], check=True, cwd=self.project_root)
            
            print("✅ 代码已提交并推送")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Git操作失败: {e}")
            return False
    
    def wait_for_deployment(self, service_url):
        """等待部署完成"""
        print("⏳ 等待Render部署完成...")
        print("💡 这可能需要5-10分钟，请耐心等待...")
        
        max_attempts = 60  # 最多等待30分钟
        attempt = 0
        
        while attempt < max_attempts:
            try:
                response = requests.get(f"{service_url}/api/health", timeout=10)
                if response.status_code == 200:
                    print("✅ 部署成功！服务已启动")
                    return True
                    
            except requests.exceptions.RequestException:
                pass
            
            attempt += 1
            print(f"⏳ 等待中... ({attempt}/{max_attempts})")
            time.sleep(30)  # 每30秒检查一次
        
        print("❌ 部署超时，请手动检查Render控制台")
        return False
    
    def test_api_endpoints(self, service_url):
        """测试API端点"""
        print("🧪 测试API端点...")
        
        endpoints = [
            "/api/health",
            "/api/docs",
        ]
        
        for endpoint in endpoints:
            try:
                url = f"{service_url}{endpoint}"
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    print(f"✅ {endpoint} - 正常")
                else:
                    print(f"⚠️ {endpoint} - 状态码: {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                print(f"❌ {endpoint} - 错误: {e}")
    
    def update_local_client(self, service_url):
        """更新本地客户端配置"""
        print("🔧 更新本地客户端配置...")
        
        client_file = self.project_root / "local_hybrid_client.py"
        
        if not client_file.exists():
            print("❌ local_hybrid_client.py 不存在")
            return False
        
        try:
            # 读取文件
            with open(client_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            # 替换URL
            old_url = 'RENDER_URL = "https://your-app-name.onrender.com"'
            new_url = f'RENDER_URL = "{service_url}"'
            
            if old_url in content:
                content = content.replace(old_url, new_url)
                
                # 写回文件
                with open(client_file, "w", encoding="utf-8") as f:
                    f.write(content)
                
                print(f"✅ 本地客户端URL已更新为: {service_url}")
                return True
            else:
                print("⚠️ 未找到需要替换的URL模式")
                print(f"💡 请手动将URL更新为: {service_url}")
                return True
                
        except Exception as e:
            print(f"❌ 更新本地客户端失败: {e}")
            return False
    
    def create_startup_script(self, service_url):
        """创建启动脚本"""
        print("📝 创建启动脚本...")
        
        # Windows启动脚本
        windows_script = f"""@echo off
echo 🚀 启动混合架构交易系统
echo ================================

echo 1. 检查Render服务状态...
curl -s {service_url}/api/health
if %errorlevel% neq 0 (
    echo ❌ Render服务未响应，请检查网络连接
    pause
    exit /b 1
)

echo 2. 启动本地交易客户端...
python local_hybrid_client.py

pause
"""
        
        with open("start_hybrid_system.bat", "w", encoding="utf-8") as f:
            f.write(windows_script)
        
        # Linux启动脚本
        linux_script = f"""#!/bin/bash
echo "🚀 启动混合架构交易系统"
echo "================================"

echo "1. 检查Render服务状态..."
if ! curl -s {service_url}/api/health > /dev/null; then
    echo "❌ Render服务未响应，请检查网络连接"
    exit 1
fi

echo "2. 启动本地交易客户端..."
python3 local_hybrid_client.py
"""
        
        with open("start_hybrid_system.sh", "w", encoding="utf-8") as f:
            f.write(linux_script)
        
        # 设置执行权限
        import os
        os.chmod("start_hybrid_system.sh", 0o755)
        
        print("✅ 启动脚本已创建:")
        print("  - start_hybrid_system.bat (Windows)")
        print("  - start_hybrid_system.sh (Linux)")
    
    def show_next_steps(self, service_url):
        """显示后续步骤"""
        print("\n" + "="*60)
        print("🎉 Render混合架构部署完成！")
        print("="*60)
        
        print(f"\n🌐 云端API地址: {service_url}")
        print(f"📖 API文档: {service_url}/docs")
        print(f"🔍 健康检查: {service_url}/api/health")
        
        print("\n📋 后续步骤:")
        print("1. 运行本地客户端:")
        print("   python local_hybrid_client.py")
        print("   或使用启动脚本: start_hybrid_system.bat")
        
        print("\n2. 更新移动应用配置:")
        print(f"   API地址改为: {service_url}")
        
        print("\n3. 测试完整流程:")
        print("   - 移动应用连接云端API ✓")
        print("   - 云端API通过WebSocket连接本地客户端 ✓") 
        print("   - 本地客户端操作交易软件 ✓")
        
        print("\n💡 优势:")
        print("- 🆓 免费750小时/月")
        print("- 🌐 移动应用直连云端，稳定可靠")
        print("- 🖥️ 交易软件在本地，安全可控")
        print("- 🔄 自动重连，断线恢复")

def main():
    """主函数"""
    print("🎨 Render自动部署工具")
    print("=" * 50)
    
    deployer = RenderDeployer()
    
    # 1. 检查Git状态
    if not deployer.check_git_status():
        return
    
    # 2. 提示用户手动部署
    print("\n📋 请按以下步骤在Render手动部署:")
    print("1. 访问 https://render.com")
    print("2. 连接GitHub仓库")
    print("3. 选择Web Service")
    print("4. 使用render.yaml配置")
    print("5. 等待部署完成")
    
    # 3. 获取部署URL
    service_url = input("\n🔗 请输入部署完成后的Render URL: ").strip()
    
    if not service_url:
        print("❌ 未提供URL，退出")
        return
    
    if not service_url.startswith("https://"):
        service_url = "https://" + service_url
    
    # 4. 等待部署完成
    if deployer.wait_for_deployment(service_url):
        # 5. 测试API
        deployer.test_api_endpoints(service_url)
        
        # 6. 更新本地客户端
        deployer.update_local_client(service_url)
        
        # 7. 创建启动脚本
        deployer.create_startup_script(service_url)
        
        # 8. 显示后续步骤
        deployer.show_next_steps(service_url)
    
    print("\n🎯 部署完成！现在可以启动混合架构系统了。")

if __name__ == "__main__":
    main()
