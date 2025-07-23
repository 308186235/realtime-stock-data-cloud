#!/usr/bin/env python3
"""
简化的OneDrive配置脚本
解决OAuth授权端口问题
"""

import os
import sys
import subprocess
import time
import json
import webbrowser
from pathlib import Path
from datetime import datetime

class SimpleOneDriveConfig:
    """简化OneDrive配置管理器"""
    
    def __init__(self):
        self.base_dir = Path("E:/交易8")
        self.rclone_exe = self.base_dir / "rclone/rclone-v1.70.2-windows-amd64/rclone.exe"
        self.config_name = "onedrive_trading"
        self.mount_point = Path("C:/mnt/onedrive")
        self.trading_data_dir = self.mount_point / "TradingData"
        
    def check_rclone(self):
        """检查rclone"""
        print("🔍 检查rclone...")
        
        if not self.rclone_exe.exists():
            print(f"❌ rclone.exe不存在: {self.rclone_exe}")
            return False
        
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
    
    def interactive_config(self):
        """交互式配置"""
        print("🔧 启动交互式rclone配置...")
        print("=" * 60)
        print("📋 配置步骤:")
        print("1. 选择 'n' (新建远程)")
        print("2. 名称输入: onedrive_trading")
        print("3. 存储类型选择: onedrive (通常是选项 38)")
        print("4. client_id: 留空 (直接按回车)")
        print("5. client_secret: 留空 (直接按回车)")
        print("6. region: 选择 1 (Microsoft Cloud Global)")
        print("7. tenant: 留空 (直接按回车)")
        print("8. 高级配置: 选择 'n' (使用默认)")
        print("9. 自动配置: 选择 'y' (使用自动配置)")
        print("10. 在浏览器中完成OAuth授权")
        print("11. 确认配置: 选择 'y'")
        print("12. 退出: 选择 'q'")
        print("=" * 60)
        
        input("按回车键开始配置...")
        
        try:
            # 启动交互式配置
            subprocess.run([str(self.rclone_exe), "config"], check=False)
            return True
        except Exception as e:
            print(f"❌ 配置失败: {e}")
            return False
    
    def test_connection(self):
        """测试连接"""
        print("🧪 测试OneDrive连接...")
        
        try:
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
            result = subprocess.run([
                str(self.rclone_exe),
                "mkdir",
                f"{self.config_name}:TradingData"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 or "already exists" in result.stderr:
                print("✅ TradingData目录创建成功")
                return True
            else:
                print(f"❌ 创建目录失败: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ 创建目录异常: {e}")
            return False
    
    def test_file_operations(self):
        """测试文件操作"""
        print("📝 测试文件操作...")
        
        # 创建测试文件
        test_content = {
            "test_time": datetime.now().isoformat(),
            "test_type": "onedrive_integration",
            "status": "testing"
        }
        
        test_file_local = self.base_dir / "test_upload.json"
        
        try:
            # 写入本地测试文件
            with open(test_file_local, 'w', encoding='utf-8') as f:
                json.dump(test_content, f, ensure_ascii=False, indent=2)
            
            # 上传到OneDrive
            result = subprocess.run([
                str(self.rclone_exe),
                "copy",
                str(test_file_local),
                f"{self.config_name}:TradingData/"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("✅ 文件上传测试成功")
                
                # 测试下载
                download_result = subprocess.run([
                    str(self.rclone_exe),
                    "cat",
                    f"{self.config_name}:TradingData/test_upload.json"
                ], capture_output=True, text=True, timeout=30)
                
                if download_result.returncode == 0:
                    print("✅ 文件下载测试成功")
                    print("文件内容:")
                    print(download_result.stdout)
                    
                    # 清理测试文件
                    subprocess.run([
                        str(self.rclone_exe),
                        "delete",
                        f"{self.config_name}:TradingData/test_upload.json"
                    ], capture_output=True, text=True, timeout=30)
                    
                    test_file_local.unlink()
                    print("✅ 测试文件已清理")
                    return True
                else:
                    print(f"❌ 文件下载测试失败: {download_result.stderr}")
                    return False
            else:
                print(f"❌ 文件上传测试失败: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ 文件操作测试异常: {e}")
            return False
    
    def create_mount_script(self):
        """创建挂载脚本"""
        print("📝 创建挂载脚本...")
        
        # 创建挂载点
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

echo 检查现有rclone进程...
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
  --log-level INFO ^
  --log-file "{self.base_dir}/rclone.log" ^
  --daemon

echo ✅ OneDrive挂载已启动!
echo 挂载点: {self.mount_point}
echo 日志文件: {self.base_dir}/rclone.log

echo.
echo 等待挂载完成...
timeout /t 5 /nobreak >NUL

echo 测试挂载状态...
if exist "{self.mount_point}" (
    dir "{self.mount_point}" >NUL 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo ✅ 挂载测试成功!
        echo 目录内容:
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
    echo ✅ 文件删除测试成功
) else (
    echo ❌ 文件写入测试失败
)

echo.
echo 🎉 OneDrive挂载配置完成!
echo 📁 交易数据目录: {self.trading_data_dir}
echo 📋 现在可以将交易软件导出路径设置为: {self.trading_data_dir}
pause
"""
        
        mount_script_file = self.base_dir / "mount_onedrive.bat"
        with open(mount_script_file, 'w', encoding='utf-8') as f:
            f.write(mount_script)
        
        print(f"✅ 挂载脚本已生成: {mount_script_file}")
        return mount_script_file
    
    def update_trading_script(self):
        """更新交易脚本路径"""
        print("🔄 更新交易脚本...")
        
        trading_script = self.base_dir / "simplified_local_integration.py"
        
        if not trading_script.exists():
            print("⚠️ 交易脚本不存在,跳过更新")
            return True
        
        try:
            with open(trading_script, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 替换OneDrive路径
            old_patterns = [
                'self.onedrive_local_path = "C:/Users/锋/OneDrive/TradingData"',
                'self.onedrive_local_path = "C:\\Users\\锋\\OneDrive\\TradingData"',
                'onedrive_local_path = "C:/Users/锋/OneDrive/TradingData"',
                'onedrive_local_path = "C:\\Users\\锋\\OneDrive\\TradingData"'
            ]
            
            new_path = f'self.onedrive_local_path = "{self.trading_data_dir}"'
            
            updated = False
            for old_pattern in old_patterns:
                if old_pattern in content:
                    content = content.replace(old_pattern, new_path)
                    updated = True
            
            if updated:
                # 备份原文件
                backup_file = trading_script.with_suffix('.py.backup')
                trading_script.rename(backup_file)
                
                # 写入更新后的内容
                with open(trading_script, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"✅ 交易脚本已更新,备份: {backup_file}")
            else:
                print("⚠️ 未找到需要替换的路径")
            
            return True
            
        except Exception as e:
            print(f"❌ 更新交易脚本失败: {e}")
            return False
    
    def run_setup(self):
        """运行设置流程"""
        print("🚀 简化OneDrive配置流程")
        print("=" * 60)
        
        # 1. 检查rclone
        if not self.check_rclone():
            return False
        
        # 2. 交互式配置
        print("\n📋 步骤1: 配置OneDrive连接")
        if not self.interactive_config():
            return False
        
        # 3. 测试连接
        print("\n📋 步骤2: 测试连接")
        if not self.test_connection():
            print("❌ 连接测试失败,请检查配置")
            return False
        
        # 4. 创建目录
        print("\n📋 步骤3: 创建交易数据目录")
        if not self.create_trading_directory():
            return False
        
        # 5. 测试文件操作
        print("\n📋 步骤4: 测试文件操作")
        if not self.test_file_operations():
            return False
        
        # 6. 创建挂载脚本
        print("\n📋 步骤5: 创建挂载脚本")
        mount_script = self.create_mount_script()
        if not mount_script:
            return False
        
        # 7. 更新交易脚本
        print("\n📋 步骤6: 更新交易脚本")
        self.update_trading_script()
        
        print("\n" + "=" * 60)
        print("🎉 OneDrive配置完成!")
        print("=" * 60)
        print(f"✅ 挂载脚本: {mount_script}")
        print(f"✅ 挂载点: {self.mount_point}")
        print(f"✅ 交易数据目录: {self.trading_data_dir}")
        print("\n📋 下一步操作:")
        print(f"1. 运行挂载脚本: {mount_script}")
        print("2. 测试文件同步")
        print("3. 集成到交易系统")
        print("\n🎯 配置成功完成!")
        
        return True

def main():
    """主函数"""
    config = SimpleOneDriveConfig()
    success = config.run_setup()
    
    if success:
        print("\n🎯 配置成功完成!")
    else:
        print("\n💥 配置过程中出现错误!")
    
    input("\n按回车键退出...")

if __name__ == "__main__":
    main()
