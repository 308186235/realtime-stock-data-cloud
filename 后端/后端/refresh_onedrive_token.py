#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OneDrive Token刷新工具
专门用于刷新过期的OneDrive访问token
"""

import subprocess
import time
from pathlib import Path

class OneDriveTokenRefresher:
    def __init__(self):
        self.rclone_exe = Path("E:/交易8/rclone/rclone-v1.70.2-windows-amd64/rclone.exe")
        self.config_name = "onedrive_trading"
        
    def check_rclone(self):
        """检查rclone程序"""
        if not self.rclone_exe.exists():
            print(f"❌ rclone程序不存在: {self.rclone_exe}")
            return False
        print("✅ rclone程序存在")
        return True
    
    def show_refresh_guide(self):
        """显示刷新指南"""
        print("=" * 60)
        print("🔄 OneDrive Token刷新指南")
        print("=" * 60)
        print()
        print("📋 即将开始token刷新过程,请按照以下步骤操作:")
        print()
        print("1️⃣ 当询问是否刷新token时:")
        print("   - 输入 'y' 然后按回车")
        print()
        print("2️⃣ 当询问是否使用浏览器授权时:")
        print("   - 输入 'y' 然后按回车")
        print()
        print("3️⃣ 浏览器会自动打开:")
        print("   - 登录您的个人OneDrive账户")
        print("   - 点击'接受'授权rclone访问")
        print()
        print("4️⃣ 授权完成后:")
        print("   - 浏览器会显示'Success!'")
        print("   - 返回命令行窗口")
        print()
        print("5️⃣ 完成配置:")
        print("   - 确认配置正确")
        print("   - 等待刷新完成")
        print()
        print("=" * 60)
        print("准备好了吗?按任意键开始刷新...")
        input()
    
    def refresh_token(self):
        """刷新token"""
        print("🔄 开始刷新OneDrive token...")
        
        try:
            # 构建刷新命令
            cmd = [str(self.rclone_exe), 'config', 'reconnect', f'{self.config_name}:']
            
            print(f"🚀 执行命令: {' '.join(cmd)}")
            print()
            print("📋 请在下面的交互界面中完成授权:")
            print("-" * 40)
            
            # 运行刷新命令
            result = subprocess.run(cmd)
            
            print("-" * 40)
            
            if result.returncode == 0:
                print("✅ Token刷新完成!")
                return True
            else:
                print("❌ Token刷新失败")
                return False
                
        except Exception as e:
            print(f"❌ Token刷新异常: {e}")
            return False
    
    def test_connection(self):
        """测试连接"""
        print("🔍 测试OneDrive连接...")
        
        try:
            result = subprocess.run(
                [str(self.rclone_exe), 'lsd', f'{self.config_name}:', '--max-depth', '1'],
                capture_output=True, text=True, timeout=30
            )
            
            if result.returncode == 0:
                print("✅ OneDrive连接成功!")
                print("📁 OneDrive根目录内容:")
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        print(f"   📂 {line.strip()}")
                return True
            else:
                print(f"❌ OneDrive连接失败:")
                print(f"   {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ 连接超时")
            return False
        except Exception as e:
            print(f"❌ 测试连接失败: {e}")
            return False
    
    def show_config_info(self):
        """显示配置信息"""
        print("📋 显示当前配置信息...")
        
        try:
            result = subprocess.run(
                [str(self.rclone_exe), 'config', 'show', self.config_name],
                capture_output=True, text=True
            )
            
            if result.returncode == 0:
                print("✅ 当前配置:")
                print("-" * 40)
                print(result.stdout)
                print("-" * 40)
                return True
            else:
                print(f"❌ 无法显示配置: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ 显示配置失败: {e}")
            return False
    
    def run(self):
        """运行刷新流程"""
        print("=" * 60)
        print("🔄 OneDrive Token刷新工具")
        print("=" * 60)
        
        # 1. 检查rclone
        if not self.check_rclone():
            return False
        
        # 2. 显示当前配置
        print()
        self.show_config_info()
        
        # 3. 显示刷新指南
        print()
        self.show_refresh_guide()
        
        # 4. 刷新token
        if not self.refresh_token():
            print()
            print("❌ Token刷新失败")
            print("📋 可能的原因:")
            print("1. 网络连接问题")
            print("2. OneDrive账户问题")
            print("3. 授权过程中断")
            print()
            print("💡 建议:")
            print("1. 检查网络连接")
            print("2. 重新运行此工具")
            print("3. 如果问题持续,请重新配置rclone")
            return False
        
        # 5. 测试连接
        print()
        if not self.test_connection():
            print("❌ 连接测试失败,但token可能已刷新")
            print("💡 请稍后再试或检查网络连接")
            return False
        
        print()
        print("🎉 OneDrive Token刷新成功!")
        print("=" * 60)
        print("✅ 现在可以正常使用OneDrive挂载功能了")
        print("💡 下一步:")
        print("1. 运行 python setup_personal_onedrive.py 完成挂载设置")
        print("2. 或者直接运行 start_personal_onedrive.bat 启动挂载")
        print("=" * 60)
        
        return True

def main():
    refresher = OneDriveTokenRefresher()
    success = refresher.run()
    
    if not success:
        print()
        print("❌ Token刷新失败")
        print("📋 如需帮助,请检查:")
        print("1. 网络连接是否正常")
        print("2. OneDrive账户是否可以正常访问")
        print("3. 浏览器是否能正常打开授权页面")
    
    print()
    input("按任意键退出...")

if __name__ == "__main__":
    main()
