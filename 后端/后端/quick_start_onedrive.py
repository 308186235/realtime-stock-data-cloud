#!/usr/bin/env python3
"""
OneDrive快速启动脚本
在rclone下载完成后,快速配置和测试OneDrive集成
"""

import os
import sys
import subprocess
import time
import json
from pathlib import Path

class OneDriveQuickStart:
    """OneDrive快速启动管理器"""
    
    def __init__(self):
        self.base_dir = Path("E:/交易8")
        self.rclone_zip = self.base_dir / "rclone.zip"
        self.rclone_dir = self.base_dir / "rclone"
        self.rclone_exe = None
        self.mount_point = Path("C:/mnt/onedrive")
        self.trading_data_dir = self.mount_point / "TradingData"
        
    def check_download_status(self):
        """检查rclone下载状态"""
        print("🔍 检查rclone下载状态...")
        
        if self.rclone_zip.exists():
            size_mb = self.rclone_zip.stat().st_size / (1024 * 1024)
            print(f"✅ rclone.zip已下载,大小: {size_mb:.1f}MB")
            return True
        else:
            print("⏳ rclone.zip还在下载中...")
            return False
    
    def extract_rclone(self):
        """解压rclone"""
        print("📦 解压rclone...")
        
        try:
            # 使用PowerShell解压
            cmd = f'Expand-Archive -Path "{self.rclone_zip}" -DestinationPath "{self.rclone_dir}" -Force'
            result = subprocess.run(["powershell", "-Command", cmd], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ rclone解压成功")
                
                # 查找rclone.exe
                for item in self.rclone_dir.rglob("rclone.exe"):
                    self.rclone_exe = item
                    print(f"✅ 找到rclone.exe: {self.rclone_exe}")
                    return True
                
                print("❌ 未找到rclone.exe")
                return False
            else:
                print(f"❌ 解压失败: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ 解压异常: {e}")
            return False
    
    def setup_rclone_path(self):
        """设置rclone路径"""
        print("🔧 设置rclone路径...")
        
        if not self.rclone_exe:
            print("❌ rclone.exe路径未设置")
            return False
        
        # 添加到当前会话的PATH
        rclone_dir = str(self.rclone_exe.parent)
        current_path = os.environ.get('PATH', '')
        
        if rclone_dir not in current_path:
            os.environ['PATH'] = f"{rclone_dir};{current_path}"
            print(f"✅ 已添加到PATH: {rclone_dir}")
        
        return True
    
    def test_rclone_command(self):
        """测试rclone命令"""
        print("🧪 测试rclone命令...")
        
        try:
            result = subprocess.run([str(self.rclone_exe), "version"], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                version_info = result.stdout.strip().split('\n')[0]
                print(f"✅ rclone测试成功: {version_info}")
                return True
            else:
                print(f"❌ rclone测试失败: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ rclone测试异常: {e}")
            return False
    
    def create_mount_point(self):
        """创建挂载点"""
        print("📁 创建挂载点...")
        
        try:
            self.mount_point.mkdir(parents=True, exist_ok=True)
            self.trading_data_dir.mkdir(parents=True, exist_ok=True)
            print(f"✅ 挂载点创建成功: {self.mount_point}")
            return True
        except Exception as e:
            print(f"❌ 创建挂载点失败: {e}")
            return False
    
    def generate_config_script(self):
        """生成配置脚本"""
        print("📝 生成配置脚本...")
        
        config_script = f"""@echo off
echo 🚀 开始配置rclone OneDrive...
echo.

echo 步骤1: 启动rclone配置
echo 请按照以下步骤操作:
echo 1. 选择 "n" (新建配置)
echo 2. 名称输入: onedrive_trading
echo 3. 存储类型选择: onedrive (通常是选项 26)
echo 4. client_id: 留空 (直接按回车)
echo 5. client_secret: 留空 (直接按回车)
echo 6. region: 选择 1 (Microsoft Cloud Global)
echo 7. 选择 "y" 进行高级配置
echo 8. drive_type: 选择 1 (OneDrive Personal)
echo 9. 选择 "y" 使用自动配置
echo 10. 在浏览器中完成OAuth授权
echo 11. 选择 "y" 确认配置
echo 12. 选择 "q" 退出配置
echo.
pause

"{self.rclone_exe}" config

echo.
echo 步骤2: 测试连接
echo 正在测试OneDrive连接...
"{self.rclone_exe}" ls onedrive_trading:

echo.
echo 步骤3: 创建交易数据目录
"{self.rclone_exe}" mkdir onedrive_trading:TradingData

echo.
echo 步骤4: 验证目录创建
"{self.rclone_exe}" ls onedrive_trading:TradingData

echo.
echo ✅ rclone OneDrive配置完成!
echo 下一步请运行: start_onedrive_mount.bat
pause
"""
        
        config_file = self.base_dir / "config_onedrive.bat"
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(config_script)
        
        print(f"✅ 配置脚本已生成: {config_file}")
        return config_file
    
    def generate_mount_script(self):
        """生成挂载脚本"""
        print("📝 生成挂载脚本...")
        
        mount_script = f"""@echo off
echo 🚀 启动OneDrive挂载...

echo 检查挂载点...
if not exist "{self.mount_point}" (
    mkdir "{self.mount_point}"
    echo ✅ 挂载点已创建: {self.mount_point}
)

echo 启动rclone挂载...
"{self.rclone_exe}" mount onedrive_trading: "{self.mount_point}" ^
  --vfs-cache-mode writes ^
  --vfs-cache-max-age 10m ^
  --log-level INFO ^
  --log-file "{self.base_dir}/rclone.log" ^
  --daemon

echo ✅ OneDrive挂载已启动!
echo 挂载点: {self.mount_point}
echo 日志文件: {self.base_dir}/rclone.log

echo.
echo 测试挂载状态...
timeout /t 3 /nobreak >nul
dir "{self.mount_point}"

echo.
echo 测试文件操作...
echo test > "{self.trading_data_dir}/test.txt"
type "{self.trading_data_dir}/test.txt"
del "{self.trading_data_dir}/test.txt"

echo.
echo ✅ OneDrive挂载测试完成!
pause
"""
        
        mount_file = self.base_dir / "start_onedrive_mount.bat"
        with open(mount_file, 'w', encoding='utf-8') as f:
            f.write(mount_script)
        
        print(f"✅ 挂载脚本已生成: {mount_file}")
        return mount_file
    
    def generate_test_script(self):
        """生成测试脚本"""
        print("📝 生成测试脚本...")
        
        test_script = f"""#!/usr/bin/env python3
# test_onedrive_integration.py

import os
import json
import time
from datetime import datetime

def test_onedrive_integration():
    print("🧪 测试OneDrive集成...")
    
    mount_path = r"{self.trading_data_dir}"
    
    # 检查挂载状态
    if not os.path.exists(mount_path):
        print(f"❌ 挂载点不存在: {{mount_path}}")
        return False
    
    # 测试写入
    test_data = {{
        "test_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "test_type": "onedrive_integration",
        "status": "testing"
    }}
    
    test_file = os.path.join(mount_path, "integration_test.json")
    
    try:
        with open(test_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 测试文件写入成功: {{test_file}}")
        
        # 等待同步
        time.sleep(2)
        
        # 测试读取
        with open(test_file, 'r', encoding='utf-8') as f:
            read_data = json.load(f)
        
        print(f"✅ 测试文件读取成功: {{read_data['test_time']}}")
        
        # 清理测试文件
        os.remove(test_file)
        print("✅ 测试文件已清理")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {{e}}")
        return False

if __name__ == "__main__":
    success = test_onedrive_integration()
    if success:
        print("🎉 OneDrive集成测试成功!")
    else:
        print("💥 OneDrive集成测试失败!")
"""
        
        test_file = self.base_dir / "test_onedrive_integration.py"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_script)
        
        print(f"✅ 测试脚本已生成: {test_file}")
        return test_file
    
    def update_trading_script(self):
        """更新交易脚本使用rclone挂载路径"""
        print("🔄 更新交易脚本...")
        
        try:
            # 读取现有脚本
            trading_script = self.base_dir / "simplified_local_integration.py"
            
            if trading_script.exists():
                with open(trading_script, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 替换路径
                old_path = 'self.onedrive_local_path = "C:/Users/锋/OneDrive/TradingData"'
                new_path = f'self.onedrive_local_path = "{self.trading_data_dir}"'
                
                if old_path in content:
                    content = content.replace(old_path, new_path)
                    
                    # 备份原文件
                    backup_file = trading_script.with_suffix('.py.backup')
                    trading_script.rename(backup_file)
                    
                    # 写入更新后的内容
                    with open(trading_script, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    print(f"✅ 交易脚本已更新,备份: {backup_file}")
                    return True
                else:
                    print("⚠️ 未找到需要替换的路径")
                    return False
            else:
                print("⚠️ 交易脚本不存在")
                return False
                
        except Exception as e:
            print(f"❌ 更新交易脚本失败: {e}")
            return False
    
    def run_quick_start(self):
        """运行快速启动流程"""
        print("🚀 OneDrive快速启动流程")
        print("=" * 50)
        
        # 1. 检查下载状态
        if not self.check_download_status():
            print("⏳ 请等待rclone下载完成后再运行此脚本")
            return False
        
        # 2. 解压rclone
        if not self.extract_rclone():
            return False
        
        # 3. 设置路径
        if not self.setup_rclone_path():
            return False
        
        # 4. 测试命令
        if not self.test_rclone_command():
            return False
        
        # 5. 创建挂载点
        if not self.create_mount_point():
            return False
        
        # 6. 生成脚本
        config_file = self.generate_config_script()
        mount_file = self.generate_mount_script()
        test_file = self.generate_test_script()
        
        # 7. 更新交易脚本
        self.update_trading_script()
        
        print("\n" + "=" * 50)
        print("🎉 快速启动准备完成!")
        print("\n📋 下一步操作:")
        print(f"1. 运行配置脚本: {config_file}")
        print(f"2. 运行挂载脚本: {mount_file}")
        print(f"3. 运行测试脚本: python {test_file}")
        print(f"4. 运行交易测试: python simplified_local_integration.py")
        print("\n🎯 完成后即可实现本地到云端的数据同步!")
        
        return True

def main():
    """主函数"""
    starter = OneDriveQuickStart()
    starter.run_quick_start()

if __name__ == "__main__":
    main()
