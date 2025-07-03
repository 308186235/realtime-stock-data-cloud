# rclone OneDrive 配置和使用指南

## 🎯 **目标**

通过rclone挂载OneDrive，实现本地交易数据与云端系统的无缝同步。

## 📋 **前置条件**

- ✅ rclone已下载（正在进行中）
- ✅ 有效的OneDrive账户
- ✅ 本地交易软件可正常导出数据

## 🚀 **第一步：安装和配置rclone**

### 1.1 解压和安装
```bash
# 下载完成后解压
Expand-Archive -Path "rclone.zip" -DestinationPath "rclone"

# 将rclone.exe复制到系统路径
copy rclone\rclone-*\rclone.exe C:\Windows\System32\

# 或者添加到PATH环境变量
$env:PATH += ";E:\交易8\rclone\rclone-v1.70.2-windows-amd64"
```

### 1.2 配置OneDrive
```bash
# 启动配置向导
rclone config

# 配置步骤：
# 1. 选择 "n" (新建配置)
# 2. 名称输入: onedrive_trading
# 3. 存储类型选择: onedrive (通常是选项 26)
# 4. client_id: 留空（使用默认）
# 5. client_secret: 留空（使用默认）
# 6. region: 选择 1 (Microsoft Cloud Global)
# 7. 选择 "y" 进行高级配置
# 8. drive_type: 选择 1 (OneDrive Personal)
# 9. 选择 "y" 使用自动配置
# 10. 在浏览器中完成OAuth授权
# 11. 选择 "y" 确认配置
# 12. 选择 "q" 退出配置
```

### 1.3 测试连接
```bash
# 测试连接
rclone ls onedrive_trading:

# 创建交易数据目录
rclone mkdir onedrive_trading:TradingData

# 验证目录创建
rclone ls onedrive_trading:TradingData
```

## 🔧 **第二步：本地挂载设置**

### 2.1 创建挂载点
```bash
# 创建本地挂载目录
mkdir C:\mnt\onedrive
```

### 2.2 挂载OneDrive
```bash
# 前台测试挂载（用于调试）
rclone mount onedrive_trading: C:\mnt\onedrive --vfs-cache-mode writes

# 后台挂载（正式使用）
rclone mount onedrive_trading: C:\mnt\onedrive --vfs-cache-mode writes --daemon

# Windows服务方式挂载（推荐）
rclone mount onedrive_trading: C:\mnt\onedrive ^
  --vfs-cache-mode writes ^
  --vfs-cache-max-age 10m ^
  --vfs-read-chunk-size 32M ^
  --buffer-size 32M ^
  --log-level INFO ^
  --log-file C:\logs\rclone.log ^
  --daemon
```

### 2.3 验证挂载
```bash
# 检查挂载状态
dir C:\mnt\onedrive

# 测试文件操作
echo "test" > C:\mnt\onedrive\TradingData\test.txt
type C:\mnt\onedrive\TradingData\test.txt
del C:\mnt\onedrive\TradingData\test.txt
```

## 📊 **第三步：修改交易软件导出路径**

### 3.1 更新导出脚本
```python
# 修改 simplified_local_integration.py
class LocalDataManager:
    def __init__(self):
        # 原路径
        # self.onedrive_local_path = "C:/Users/锋/OneDrive/TradingData"
        
        # 新路径（rclone挂载）
        self.onedrive_local_path = "C:/mnt/onedrive/TradingData"
        self.local_export_path = "C:/TradingData"
        
        # 确保目录存在
        os.makedirs(self.onedrive_local_path, exist_ok=True)
        os.makedirs(self.local_export_path, exist_ok=True)
```

### 3.2 测试数据同步
```python
# 运行测试
python simplified_local_integration.py

# 检查OneDrive网页版是否有数据
# 访问: https://onedrive.live.com
```

## 🌐 **第四步：云端服务器配置**

### 4.1 云端安装rclone
```bash
# Linux服务器
curl -O https://downloads.rclone.org/rclone-current-linux-amd64.zip
unzip rclone-current-linux-amd64.zip
sudo cp rclone-*/rclone /usr/local/bin/
sudo chmod +x /usr/local/bin/rclone
```

### 4.2 云端配置OneDrive
```bash
# 使用相同的配置
rclone config

# 或者复制本地配置文件
# Windows: %APPDATA%\rclone\rclone.conf
# Linux: ~/.config/rclone/rclone.conf
```

### 4.3 云端挂载
```bash
# 创建挂载点
sudo mkdir -p /mnt/onedrive
sudo chown $USER:$USER /mnt/onedrive

# 挂载OneDrive
rclone mount onedrive_trading: /mnt/onedrive \
  --vfs-cache-mode writes \
  --vfs-cache-max-age 10m \
  --daemon

# 验证挂载
ls -la /mnt/onedrive/TradingData/
```

## 🔄 **第五步：自动化脚本**

### 5.1 Windows启动脚本
```batch
@echo off
REM start_onedrive_mount.bat

echo 启动OneDrive挂载...
rclone mount onedrive_trading: C:\mnt\onedrive ^
  --vfs-cache-mode writes ^
  --vfs-cache-max-age 10m ^
  --log-level INFO ^
  --log-file C:\logs\rclone.log ^
  --daemon

echo OneDrive挂载完成！
pause
```

### 5.2 Linux启动脚本
```bash
#!/bin/bash
# start_onedrive_mount.sh

echo "启动OneDrive挂载..."
rclone mount onedrive_trading: /mnt/onedrive \
  --vfs-cache-mode writes \
  --vfs-cache-max-age 10m \
  --log-level INFO \
  --log-file /var/log/rclone.log \
  --daemon

echo "OneDrive挂载完成！"
```

## 🛠️ **第六步：故障排除**

### 6.1 常见问题
```bash
# 检查rclone进程
tasklist | findstr rclone

# 停止rclone挂载
taskkill /f /im rclone.exe

# 重新挂载
rclone mount onedrive_trading: C:\mnt\onedrive --vfs-cache-mode writes --daemon

# 检查日志
type C:\logs\rclone.log
```

### 6.2 性能优化
```bash
# 高性能配置
rclone mount onedrive_trading: C:\mnt\onedrive ^
  --vfs-cache-mode full ^
  --vfs-cache-max-age 1h ^
  --vfs-cache-max-size 1G ^
  --vfs-read-chunk-size 64M ^
  --vfs-read-chunk-size-limit 2G ^
  --buffer-size 64M ^
  --daemon
```

## 📈 **第七步：监控和维护**

### 7.1 监控脚本
```python
import os
import time
import subprocess

def check_mount_status():
    """检查挂载状态"""
    mount_path = "C:/mnt/onedrive"
    
    if os.path.exists(mount_path):
        try:
            # 尝试列出目录
            files = os.listdir(mount_path)
            print(f"✅ OneDrive挂载正常，包含 {len(files)} 个项目")
            return True
        except Exception as e:
            print(f"❌ OneDrive挂载异常: {e}")
            return False
    else:
        print(f"❌ 挂载点不存在: {mount_path}")
        return False

def restart_mount():
    """重启挂载"""
    print("🔄 重启OneDrive挂载...")
    
    # 停止现有挂载
    subprocess.run(["taskkill", "/f", "/im", "rclone.exe"], 
                   capture_output=True)
    
    time.sleep(2)
    
    # 重新挂载
    subprocess.run([
        "rclone", "mount", "onedrive_trading:", "C:/mnt/onedrive",
        "--vfs-cache-mode", "writes",
        "--daemon"
    ])
    
    print("✅ OneDrive挂载重启完成")

if __name__ == "__main__":
    if not check_mount_status():
        restart_mount()
```

## 🎯 **验收标准**

- [ ] rclone成功安装并配置OneDrive
- [ ] 本地可以挂载OneDrive为文件系统
- [ ] 交易数据可以写入挂载目录
- [ ] OneDrive网页版能看到同步的文件
- [ ] 云端服务器能读取相同的文件
- [ ] 数据同步延迟小于30秒
- [ ] 系统稳定运行24小时无异常

## 🎉 **完成后的效果**

1. **本地交易软件** → 导出数据到 `C:/mnt/onedrive/TradingData/`
2. **rclone自动同步** → 数据上传到OneDrive云端
3. **云端服务器** → 从 `/mnt/onedrive/TradingData/` 读取最新数据
4. **Worker API** → 返回真实的本地交易数据
5. **前端应用** → 显示实时的交易信息

这样就实现了完整的本地到云端的数据流！
