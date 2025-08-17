#!/usr/bin/env python3
"""
自动化OneDrive配置脚本
使用MCP工具处理rclone配置和OneDrive集成
"""

import os
import sys
import subprocess
import time
import json
import webbrowser
from pathlib import Path
from datetime import datetime

class AutomatedOneDriveSetup:
    """自动化OneDrive设置管理器"""
    
    def __init__(self):
        self.base_dir = Path("E:/交易8")
        self.rclone_exe = self.base_dir / "rclone/rclone-v1.70.2-windows-amd64/rclone.exe"
        self.config_name = "onedrive_trading"
        self.mount_point = Path("C:/mnt/onedrive")
        self.trading_data_dir = self.mount_point / "TradingData"
        self.log_file = self.base_dir / "rclone.log"
        
    def check_prerequisites(self):
        """检查前置条件"""
        print("🔍 检查前置条件...")
        
        # 检查rclone.exe
        if not self.rclone_exe.exists():
            print(f"❌ rclone.exe不存在: {self.rclone_exe}")
            return False
        
        print(f"✅ rclone.exe已找到: {self.rclone_exe}")
        
        # 测试rclone命令
        try:
            result = subprocess.run([str(self.rclone_exe), "version"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                version_info = result.stdout.strip().split('\n')[0]
                print(f"✅ rclone版本: {version_info}")
                return True
            else:
                print(f"❌ rclone测试失败: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ rclone测试异常: {e}")
            return False
    
    def create_automated_config(self):
        """创建自动化配置"""
        print("📝 创建自动化rclone配置...")
        
        # 配置内容
        config_content = f"""[{self.config_name}]
type = onedrive
region = global
drive_type = personal
access_scopes = Files.Read Files.ReadWrite Files.Read.All Files.ReadWrite.All offline_access
"""
        
        # 获取rclone配置目录
        config_dir = Path.home() / "AppData/Roaming/rclone"
        config_dir.mkdir(parents=True, exist_ok=True)
        
        config_file = config_dir / "rclone.conf"
        
        # 如果配置文件已存在,备份
        if config_file.exists():
            backup_file = config_file.with_suffix(f'.conf.backup.{int(time.time())}')
            config_file.rename(backup_file)
            print(f"📦 已备份现有配置: {backup_file}")
        
        # 写入新配置
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(config_content)
        
        print(f"✅ 配置文件已创建: {config_file}")
        return config_file
    
    def start_oauth_flow(self):
        """启动OAuth授权流程"""
        print("🔐 启动OAuth授权流程...")

        try:
            # 启动rclone authorize命令(不使用--drive-type参数)
            cmd = [
                str(self.rclone_exe),
                "authorize",
                "onedrive"
            ]

            print("🌐 正在启动浏览器进行OAuth授权...")
            print("请在浏览器中完成OneDrive登录和授权")
            print(f"使用您的邮箱: 308186235@qq.com")

            # 运行授权命令
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if result.returncode == 0:
                # 提取token
                output = result.stdout
                print("📋 授权命令输出:")
                print(output)

                if "token =" in output:
                    # 查找token部分
                    lines = output.split('\n')
                    token_started = False
                    token_lines = []

                    for line in lines:
                        if "token =" in line:
                            token_started = True
                        if token_started:
                            token_lines.append(line)
                            if line.strip().endswith("}") and token_started:
                                break

                    if token_lines:
                        token_content = '\n'.join(token_lines)
                        print("✅ OAuth授权成功!")
                        return token_content
                    else:
                        print("⚠️ 未找到完整token信息")
                        # 尝试手动输入token
                        return self.manual_token_input()
                else:
                    print("⚠️ 输出中未找到token")
                    # 尝试手动输入token
                    return self.manual_token_input()
            else:
                print(f"❌ OAuth授权失败: {result.stderr}")
                # 尝试手动输入token
                return self.manual_token_input()

        except subprocess.TimeoutExpired:
            print("⏰ OAuth授权超时,请重试")
            return None
        except Exception as e:
            print(f"❌ OAuth授权异常: {e}")
            return None

    def manual_token_input(self):
        """手动输入token"""
        print("\n🔧 手动配置模式")
        print("=" * 50)
        print("请手动运行以下命令获取token:")
        print(f'"{self.rclone_exe}" authorize onedrive')
        print("\n然后将完整的token内容粘贴到下面:")
        print("(从 'token = {' 开始到 '}' 结束)")
        print("=" * 50)

        token_lines = []
        print("请输入token内容 (输入空行结束):")

        while True:
            line = input()
            if line.strip() == "":
                break
            token_lines.append(line)

        if token_lines:
            token_content = '\n'.join(token_lines)
            print("✅ 手动token输入完成")
            return token_content
        else:
            print("❌ 未输入token内容")
            return None
    
    def update_config_with_token(self, token_content):
        """更新配置文件添加token"""
        print("🔧 更新配置文件...")
        
        config_dir = Path.home() / "AppData/Roaming/rclone"
        config_file = config_dir / "rclone.conf"
        
        try:
            # 读取现有配置
            with open(config_file, 'r', encoding='utf-8') as f:
                config_content = f.read()
            
            # 添加token
            updated_config = config_content.rstrip() + '\n' + token_content + '\n'
            
            # 写回配置文件
            with open(config_file, 'w', encoding='utf-8') as f:
                f.write(updated_config)
            
            print("✅ 配置文件已更新")
            return True
            
        except Exception as e:
            print(f"❌ 更新配置文件失败: {e}")
            return False
    
    def test_connection(self):
        """测试OneDrive连接"""
        print("🧪 测试OneDrive连接...")
        
        try:
            # 测试列出根目录
            result = subprocess.run([
                str(self.rclone_exe), 
                "ls", 
                f"{self.config_name}:"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("✅ OneDrive连接测试成功!")
                print("根目录内容:")
                print(result.stdout)
                return True
            else:
                print(f"❌ OneDrive连接测试失败: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ 连接测试异常: {e}")
            return False
    
    def create_trading_directory(self):
        """创建交易数据目录"""
        print("📁 创建交易数据目录...")
        
        try:
            # 创建TradingData目录
            result = subprocess.run([
                str(self.rclone_exe),
                "mkdir",
                f"{self.config_name}:TradingData"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("✅ TradingData目录创建成功")
                return True
            else:
                # 可能目录已存在
                if "already exists" in result.stderr or result.returncode == 0:
                    print("✅ TradingData目录已存在")
                    return True
                else:
                    print(f"❌ 创建目录失败: {result.stderr}")
                    return False
                    
        except Exception as e:
            print(f"❌ 创建目录异常: {e}")
            return False
    
    def setup_mount(self):
        """设置挂载"""
        print("🔗 设置OneDrive挂载...")
        
        # 创建本地挂载点
        try:
            self.mount_point.mkdir(parents=True, exist_ok=True)
            self.trading_data_dir.mkdir(parents=True, exist_ok=True)
            print(f"✅ 挂载点已创建: {self.mount_point}")
        except Exception as e:
            print(f"❌ 创建挂载点失败: {e}")
            return False
        
        # 生成挂载脚本
        mount_script = f"""@echo off
echo 🚀 启动OneDrive挂载...

echo 检查现有挂载...
tasklist /FI "IMAGENAME eq rclone.exe" 2>NUL | find /I /N "rclone.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo ⚠️ rclone进程已在运行,正在停止...
    taskkill /F /IM rclone.exe >NUL 2>&1
    timeout /t 2 /nobreak >NUL
)

echo 启动rclone挂载...
"{self.rclone_exe}" mount {self.config_name}: "{self.mount_point}" ^
  --vfs-cache-mode writes ^
  --vfs-cache-max-age 10m ^
  --vfs-read-chunk-size 32M ^
  --buffer-size 32M ^
  --log-level INFO ^
  --log-file "{self.log_file}" ^
  --daemon

echo ✅ OneDrive挂载已启动!
echo 挂载点: {self.mount_point}
echo 日志文件: {self.log_file}

echo.
echo 等待挂载完成...
timeout /t 5 /nobreak >NUL

echo 测试挂载状态...
if exist "{self.mount_point}" (
    dir "{self.mount_point}" >NUL 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo ✅ 挂载测试成功!
        dir "{self.mount_point}"
    ) else (
        echo ❌ 挂载测试失败
    )
) else (
    echo ❌ 挂载点不存在
)

echo.
echo 测试文件操作...
echo test > "{self.trading_data_dir}\\test.txt" 2>NUL
if exist "{self.trading_data_dir}\\test.txt" (
    echo ✅ 文件写入测试成功
    type "{self.trading_data_dir}\\test.txt"
    del "{self.trading_data_dir}\\test.txt" >NUL 2>&1
) else (
    echo ❌ 文件写入测试失败
)

pause
"""
        
        mount_script_file = self.base_dir / "start_onedrive_mount_auto.bat"
        with open(mount_script_file, 'w', encoding='utf-8') as f:
            f.write(mount_script)
        
        print(f"✅ 挂载脚本已生成: {mount_script_file}")
        return mount_script_file
    
    def run_full_setup(self):
        """运行完整设置流程"""
        print("🚀 开始自动化OneDrive设置")
        print("=" * 60)
        
        # 1. 检查前置条件
        if not self.check_prerequisites():
            print("❌ 前置条件检查失败")
            return False
        
        # 2. 创建基础配置
        config_file = self.create_automated_config()
        if not config_file:
            print("❌ 创建配置失败")
            return False
        
        # 3. OAuth授权
        print("\n" + "=" * 60)
        print("🔐 开始OAuth授权流程")
        print("请注意:")
        print("1. 浏览器将自动打开OneDrive授权页面")
        print("2. 请使用您的邮箱 308186235@qq.com 登录")
        print("3. 授权完成后程序将自动继续")
        print("=" * 60)
        
        input("按回车键开始授权...")
        
        token_content = self.start_oauth_flow()
        if not token_content:
            print("❌ OAuth授权失败")
            return False
        
        # 4. 更新配置
        if not self.update_config_with_token(token_content):
            print("❌ 更新配置失败")
            return False
        
        # 5. 测试连接
        if not self.test_connection():
            print("❌ 连接测试失败")
            return False
        
        # 6. 创建目录
        if not self.create_trading_directory():
            print("❌ 创建目录失败")
            return False
        
        # 7. 设置挂载
        mount_script = self.setup_mount()
        if not mount_script:
            print("❌ 设置挂载失败")
            return False
        
        print("\n" + "=" * 60)
        print("🎉 OneDrive自动化设置完成!")
        print("=" * 60)
        print(f"✅ 配置文件: {config_file}")
        print(f"✅ 挂载脚本: {mount_script}")
        print(f"✅ 挂载点: {self.mount_point}")
        print(f"✅ 交易数据目录: {self.trading_data_dir}")
        print("\n📋 下一步操作:")
        print(f"1. 运行挂载脚本: {mount_script}")
        print("2. 测试文件同步")
        print("3. 集成到交易系统")
        
        return True

def main():
    """主函数"""
    setup = AutomatedOneDriveSetup()
    success = setup.run_full_setup()
    
    if success:
        print("\n🎯 设置成功完成!")
    else:
        print("\n💥 设置过程中出现错误!")
    
    input("\n按回车键退出...")

if __name__ == "__main__":
    main()
