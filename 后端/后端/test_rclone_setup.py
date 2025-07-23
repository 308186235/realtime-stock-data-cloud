#!/usr/bin/env python3
"""
测试rclone OneDrive挂载方案
"""

import os
import json
import subprocess
import time
import platform

def check_rclone_installed():
    """检查rclone是否已安装"""
    try:
        result = subprocess.run(['rclone', 'version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version = result.stdout.split('\n')[0]
            print(f"✅ rclone已安装: {version}")
            return True
        else:
            print("❌ rclone未正确安装")
            return False
    except FileNotFoundError:
        print("❌ rclone未安装")
        return False
    except Exception as e:
        print(f"❌ 检查rclone失败: {e}")
        return False

def check_rclone_config():
    """检查rclone OneDrive配置"""
    try:
        result = subprocess.run(['rclone', 'config', 'show'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            configs = result.stdout
            if 'onedrive' in configs.lower():
                print("✅ 发现OneDrive配置")
                
                # 提取配置名称
                lines = configs.split('\n')
                onedrive_configs = []
                for line in lines:
                    if line.startswith('[') and line.endswith(']'):
                        config_name = line.strip('[]')
                        onedrive_configs.append(config_name)
                
                if onedrive_configs:
                    print(f"📋 可用配置: {', '.join(onedrive_configs)}")
                    return onedrive_configs[0]  # 返回第一个配置
                else:
                    print("⚠️ 未找到具体的OneDrive配置名称")
                    return None
            else:
                print("⚠️ 未找到OneDrive配置")
                return None
        else:
            print("❌ 无法读取rclone配置")
            return None
    except Exception as e:
        print(f"❌ 检查rclone配置失败: {e}")
        return None

def test_rclone_connection(config_name):
    """测试rclone连接"""
    try:
        print(f"🔍 测试rclone连接: {config_name}")
        result = subprocess.run(['rclone', 'ls', f'{config_name}:', '--max-depth', '1'], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            files = result.stdout.strip().split('\n') if result.stdout.strip() else []
            print(f"✅ 连接成功,发现 {len(files)} 个文件/文件夹")
            
            # 检查是否有TradingData文件夹
            trading_data_exists = any('TradingData' in line for line in files)
            if trading_data_exists:
                print("📁 发现TradingData文件夹")
            else:
                print("⚠️ 未发现TradingData文件夹")
            
            return True
        else:
            print(f"❌ 连接失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ 测试连接失败: {e}")
        return False

def create_test_mount_point():
    """创建测试挂载点"""
    system = platform.system()
    
    if system == "Windows":
        mount_point = "C:\\temp\\onedrive_test"
    else:
        mount_point = "/tmp/onedrive_test"
    
    try:
        os.makedirs(mount_point, exist_ok=True)
        print(f"✅ 创建挂载点: {mount_point}")
        return mount_point
    except Exception as e:
        print(f"❌ 创建挂载点失败: {e}")
        return None

def test_mount_onedrive(config_name, mount_point):
    """测试挂载OneDrive (仅测试命令,不实际挂载)"""
    system = platform.system()
    
    if system == "Windows":
        mount_cmd = [
            'rclone', 'mount', f'{config_name}:', mount_point,
            '--vfs-cache-mode', 'writes',
            '--vfs-cache-max-age', '5m'
        ]
    else:
        mount_cmd = [
            'rclone', 'mount', f'{config_name}:', mount_point,
            '--vfs-cache-mode', 'writes',
            '--vfs-cache-max-age', '5m',
            '--daemon'
        ]
    
    print(f"🔧 挂载命令: {' '.join(mount_cmd)}")
    print("⚠️ 注意: 实际挂载需要在后台运行,这里仅显示命令")
    
    return mount_cmd

def test_file_operations(config_name):
    """测试文件操作 (通过rclone命令)"""
    try:
        print("🔍 测试文件操作...")
        
        # 创建测试文件
        test_data = {
            "test": True,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "message": "rclone测试文件"
        }
        
        test_file = "rclone_test.json"
        with open(test_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False, indent=2)
        
        print(f"📝 创建本地测试文件: {test_file}")
        
        # 上传测试文件
        upload_cmd = ['rclone', 'copy', test_file, f'{config_name}:TradingData/']
        result = subprocess.run(upload_cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ 文件上传成功")
            
            # 验证文件存在
            check_cmd = ['rclone', 'ls', f'{config_name}:TradingData/{test_file}']
            check_result = subprocess.run(check_cmd, capture_output=True, text=True, timeout=15)
            
            if check_result.returncode == 0:
                print("✅ 文件验证成功")
                
                # 下载文件验证
                download_file = f"downloaded_{test_file}"
                download_cmd = ['rclone', 'copy', f'{config_name}:TradingData/{test_file}', '.']
                download_result = subprocess.run(download_cmd, capture_output=True, text=True, timeout=30)
                
                if download_result.returncode == 0 and os.path.exists(test_file):
                    print("✅ 文件下载验证成功")
                    
                    # 清理测试文件
                    os.remove(test_file)
                    if os.path.exists(download_file):
                        os.remove(download_file)
                    
                    # 删除云端测试文件
                    delete_cmd = ['rclone', 'delete', f'{config_name}:TradingData/{test_file}']
                    subprocess.run(delete_cmd, capture_output=True, text=True, timeout=15)
                    
                    return True
                else:
                    print("❌ 文件下载验证失败")
            else:
                print("❌ 文件验证失败")
        else:
            print(f"❌ 文件上传失败: {result.stderr}")
        
        # 清理本地文件
        if os.path.exists(test_file):
            os.remove(test_file)
        
        return False
        
    except Exception as e:
        print(f"❌ 文件操作测试失败: {e}")
        return False

def main():
    """主函数"""
    print("🎯 rclone OneDrive挂载方案测试")
    print("=" * 60)
    
    # 1. 检查rclone安装
    if not check_rclone_installed():
        print("\n📝 安装指南:")
        print("Windows: 下载 https://downloads.rclone.org/rclone-current-windows-amd64.zip")
        print("Linux: curl -O https://downloads.rclone.org/rclone-current-linux-amd64.zip")
        return
    
    # 2. 检查配置
    config_name = check_rclone_config()
    if not config_name:
        print("\n📝 配置指南:")
        print("运行: rclone config")
        print("选择: n (新建配置)")
        print("名称: onedrive_trading")
        print("类型: onedrive")
        print("按提示完成OAuth授权")
        return
    
    # 3. 测试连接
    if not test_rclone_connection(config_name):
        print("\n❌ 连接测试失败,请检查网络和授权")
        return
    
    # 4. 测试文件操作
    if test_file_operations(config_name):
        print("\n🎉 文件操作测试成功!")
    else:
        print("\n⚠️ 文件操作测试失败")
    
    # 5. 显示挂载命令
    mount_point = create_test_mount_point()
    if mount_point:
        mount_cmd = test_mount_onedrive(config_name, mount_point)
        
        print(f"\n{'='*60}")
        print("🚀 下一步: 实际挂载OneDrive")
        print(f"{'='*60}")
        print("1. 运行挂载命令 (需要管理员权限):")
        print(f"   {' '.join(mount_cmd)}")
        print(f"\n2. 验证挂载:")
        print(f"   ls {mount_point}")
        print(f"\n3. 测试文件访问:")
        print(f"   echo 'test' > {mount_point}/test.txt")
        print(f"   cat {mount_point}/test.txt")
        print(f"\n4. 卸载 (完成后):")
        if platform.system() == "Windows":
            print(f"   taskkill /f /im rclone.exe")
        else:
            print(f"   fusermount -u {mount_point}")
    
    print(f"\n✅ rclone方案验证完成!")
    print("📋 这个方案比分享链接更稳定,适合生产环境使用")

if __name__ == "__main__":
    main()
