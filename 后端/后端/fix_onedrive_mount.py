#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OneDrive挂载修复工具
解决rclone OneDrive挂载的token过期和配置问题
"""

import os
import sys
import subprocess
import time
import json
from pathlib import Path

class OneDriveMountFixer:
    def __init__(self):
        self.base_dir = Path("E:/交易8 - 副本")
        self.rclone_exe = Path("E:/交易8/rclone/rclone-v1.70.2-windows-amd64/rclone.exe")
        self.mount_point = Path("C:/mnt/onedrive")
        self.trading_data_dir = self.mount_point / "TradingData"
        self.config_name = "onedrive_trading"
        self.log_file = self.base_dir / "rclone.log"
        
    def check_rclone_exists(self):
        """检查rclone是否存在"""
        print("🔍 检查rclone程序...")
        if not self.rclone_exe.exists():
            print(f"❌ rclone程序不存在: {self.rclone_exe}")
            return False
        print(f"✅ rclone程序存在: {self.rclone_exe}")
        return True
    
    def check_mount_point(self):
        """检查并创建挂载点"""
        print("🔍 检查挂载点...")
        try:
            self.mount_point.mkdir(parents=True, exist_ok=True)
            self.trading_data_dir.mkdir(parents=True, exist_ok=True)
            print(f"✅ 挂载点已准备: {self.mount_point}")
            return True
        except Exception as e:
            print(f"❌ 创建挂载点失败: {e}")
            return False
    
    def kill_existing_rclone(self):
        """停止现有的rclone进程"""
        print("🔍 检查现有rclone进程...")
        try:
            result = subprocess.run(
                ['tasklist', '/FI', 'IMAGENAME eq rclone.exe'],
                capture_output=True, text=True, encoding='gbk'
            )
            
            if 'rclone.exe' in result.stdout:
                print("⚠️ 发现运行中的rclone进程,正在停止...")
                subprocess.run(['taskkill', '/F', '/IM', 'rclone.exe'], 
                             capture_output=True)
                time.sleep(2)
                print("✅ 已停止现有rclone进程")
            else:
                print("✅ 没有运行中的rclone进程")
            return True
        except Exception as e:
            print(f"❌ 检查rclone进程失败: {e}")
            return False
    
    def check_config(self):
        """检查rclone配置"""
        print("🔍 检查rclone配置...")
        try:
            result = subprocess.run(
                [str(self.rclone_exe), 'config', 'show', self.config_name],
                capture_output=True, text=True, encoding='utf-8'
            )
            
            if result.returncode == 0:
                print(f"✅ 找到配置: {self.config_name}")
                return True
            else:
                print(f"❌ 配置不存在: {self.config_name}")
                return False
        except Exception as e:
            print(f"❌ 检查配置失败: {e}")
            return False
    
    def test_connection(self):
        """测试OneDrive连接"""
        print("🔍 测试OneDrive连接...")
        try:
            result = subprocess.run(
                [str(self.rclone_exe), 'lsd', f'{self.config_name}:'],
                capture_output=True, text=True, encoding='utf-8',
                timeout=30
            )
            
            if result.returncode == 0:
                print("✅ OneDrive连接正常")
                return True
            else:
                print(f"❌ OneDrive连接失败: {result.stderr}")
                if "token expired" in result.stderr or "invalid_request" in result.stderr:
                    print("🔄 检测到token过期,需要重新授权")
                return False
        except subprocess.TimeoutExpired:
            print("❌ OneDrive连接超时")
            return False
        except Exception as e:
            print(f"❌ 测试连接失败: {e}")
            return False
    
    def refresh_token_interactive(self):
        """交互式刷新OneDrive token"""
        print("🔄 开始刷新OneDrive token...")
        print("📋 这是一个交互式过程,请按照提示操作")
        print()

        try:
            # 手动启动token刷新
            cmd = [str(self.rclone_exe), 'config', 'reconnect', f'{self.config_name}:']
            print(f"🚀 执行命令: {' '.join(cmd)}")
            print("📋 请在命令行中完成以下步骤:")
            print("1. 选择 'y' 刷新token")
            print("2. 选择 'y' 使用浏览器授权")
            print("3. 在浏览器中登录您的个人OneDrive账户")
            print("4. 完成授权后返回")
            print()

            # 直接调用,让用户手动操作
            result = subprocess.run(cmd, cwd=str(self.base_dir))

            if result.returncode == 0:
                print("✅ Token刷新完成")
                return True
            else:
                print("❌ Token刷新失败")
                return False

        except Exception as e:
            print(f"❌ Token刷新异常: {e}")
            return False

    def create_personal_config(self):
        """为个人账户创建OneDrive配置"""
        print("🔧 为个人OneDrive账户创建配置...")
        print("📋 请按照以下步骤操作:")
        print("1. 选择 'n' 创建新的remote")
        print("2. 输入名称: onedrive_trading")
        print("3. 选择 OneDrive (Microsoft OneDrive)")
        print("4. 选择个人账户类型")
        print("5. 在浏览器中登录您的个人OneDrive账户")
        print("6. 完成授权")
        print()

        try:
            cmd = [str(self.rclone_exe), 'config']
            result = subprocess.run(cmd, cwd=str(self.base_dir))

            if result.returncode == 0:
                print("✅ 配置创建完成")
                return True
            else:
                print("❌ 配置创建失败")
                return False

        except Exception as e:
            print(f"❌ 配置创建异常: {e}")
            return False
    
    def start_mount(self):
        """启动OneDrive挂载"""
        print("🚀 启动OneDrive挂载...")
        
        try:
            # 构建挂载命令
            cmd = [
                str(self.rclone_exe), 'mount',
                f'{self.config_name}:', str(self.mount_point),
                '--vfs-cache-mode', 'writes',
                '--vfs-cache-max-age', '10m',
                '--log-level', 'INFO',
                '--log-file', str(self.log_file),
                '--daemon'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
            
            if result.returncode == 0:
                print("✅ OneDrive挂载启动成功")
                time.sleep(3)  # 等待挂载完成
                return True
            else:
                print(f"❌ OneDrive挂载启动失败: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ 启动挂载异常: {e}")
            return False
    
    def test_mount(self):
        """测试挂载状态"""
        print("🔍 测试挂载状态...")
        
        try:
            # 检查挂载点是否可访问
            if not self.mount_point.exists():
                print(f"❌ 挂载点不存在: {self.mount_point}")
                return False
            
            # 尝试列出目录
            files = list(self.mount_point.iterdir())
            print(f"✅ 挂载点可访问,包含 {len(files)} 个项目")
            
            # 测试写入权限
            test_file = self.trading_data_dir / "mount_test.txt"
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write(f"mount test {time.time()}")
            
            if test_file.exists():
                test_file.unlink()
                print("✅ 挂载读写测试成功")
                return True
            else:
                print("❌ 挂载写入测试失败")
                return False
                
        except Exception as e:
            print(f"❌ 挂载测试失败: {e}")
            return False
    
    def create_startup_script(self):
        """创建启动脚本"""
        print("📝 创建启动脚本...")
        
        script_content = f'''@echo off
chcp 65001 >nul
echo 🚀 启动OneDrive交易系统挂载...

echo 检查rclone进程...
tasklist /FI "IMAGENAME eq rclone.exe" 2>NUL | find /I /N "rclone.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo ✅ rclone进程已在运行
) else (
    echo 🔄 启动rclone挂载...
    "{self.rclone_exe}" mount {self.config_name}: "{self.mount_point}" ^
      --vfs-cache-mode writes ^
      --vfs-cache-max-age 10m ^
      --log-level INFO ^
      --log-file "{self.log_file}" ^
      --daemon
    
    echo ✅ rclone挂载已启动
    timeout /t 3 /nobreak >nul
)

echo 🔍 测试挂载状态...
if exist "{self.mount_point}" (
    dir "{self.mount_point}" >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo ✅ OneDrive挂载正常
        echo 📁 交易数据目录: {self.trading_data_dir}
    ) else (
        echo ❌ OneDrive挂载异常
    )
) else (
    echo ❌ 挂载点不存在
)

echo.
echo 🎉 OneDrive交易系统已启动!
pause
'''
        
        try:
            script_path = self.base_dir / "start_onedrive_trading.bat"
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(script_content)
            print(f"✅ 启动脚本已创建: {script_path}")
            return True
        except Exception as e:
            print(f"❌ 创建启动脚本失败: {e}")
            return False
    
    def fix_mount(self):
        """修复OneDrive挂载"""
        print("=" * 60)
        print("🔧 OneDrive挂载修复工具")
        print("=" * 60)
        
        # 1. 检查rclone程序
        if not self.check_rclone_exists():
            return False
        
        # 2. 检查挂载点
        if not self.check_mount_point():
            return False
        
        # 3. 停止现有进程
        if not self.kill_existing_rclone():
            return False
        
        # 4. 检查配置
        if not self.check_config():
            print("❌ 需要先配置rclone OneDrive")
            print("🔧 开始创建个人OneDrive配置...")
            if not self.create_personal_config():
                print("❌ 配置创建失败")
                return False

        # 5. 测试连接
        if not self.test_connection():
            print("🔄 尝试刷新token...")
            if not self.refresh_token_interactive():
                print("❌ Token刷新失败,请重新配置")
                return False

            # 再次测试连接
            if not self.test_connection():
                print("❌ 连接仍然失败,请检查网络和配置")
                return False
        
        # 6. 启动挂载
        if not self.start_mount():
            return False
        
        # 7. 测试挂载
        if not self.test_mount():
            return False
        
        # 8. 创建启动脚本
        self.create_startup_script()
        
        print()
        print("🎉 OneDrive挂载修复完成!")
        print(f"📁 挂载点: {self.mount_point}")
        print(f"📊 交易数据目录: {self.trading_data_dir}")
        print(f"📋 日志文件: {self.log_file}")
        print()
        print("💡 使用说明:")
        print("1. 交易软件导出路径设置为: C:\\mnt\\onedrive\\TradingData")
        print("2. 使用 start_onedrive_trading.bat 启动系统")
        print("3. 如有问题请查看日志文件")
        
        return True

def main():
    fixer = OneDriveMountFixer()
    success = fixer.fix_mount()
    
    if not success:
        print()
        print("❌ OneDrive挂载修复失败")
        print("📋 请检查:")
        print("1. rclone程序是否存在")
        print("2. OneDrive账户是否正常")
        print("3. 网络连接是否正常")
        print("4. 是否有管理员权限")
        sys.exit(1)

if __name__ == "__main__":
    main()
