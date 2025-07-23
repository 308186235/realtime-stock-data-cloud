# rclone挂载OneDrive方案

## 🎯 方案概述

使用rclone工具将OneDrive挂载为本地磁盘,让服务器代码直接操作本地路径,实现无缝的云端文件访问。

## 📋 实施步骤

### 1. 安装rclone

#### Windows (本地测试)
```powershell
# 下载rclone
Invoke-WebRequest -Uri "https://downloads.rclone.org/rclone-current-windows-amd64.zip" -OutFile "rclone.zip"
Expand-Archive -Path "rclone.zip" -DestinationPath "."
```

#### Linux (服务器部署)
```bash
# 下载并安装rclone
curl -O https://downloads.rclone.org/rclone-current-linux-amd64.zip
unzip rclone-current-linux-amd64.zip
sudo cp rclone-*/rclone /usr/local/bin/
sudo chmod +x /usr/local/bin/rclone
```

### 2. 配置OneDrive账户

```bash
# 启动配置向导
rclone config

# 配置步骤:
# 1. 选择 "n" 创建新配置
# 2. 输入名称: "onedrive_trading"
# 3. 选择存储类型: "onedrive"
# 4. 留空client_id和client_secret (使用默认)
# 5. 选择账户类型: "1" (OneDrive Personal)
# 6. 按提示完成OAuth授权
```

### 3. 挂载OneDrive

#### 创建挂载点
```bash
# Linux
sudo mkdir -p /mnt/onedrive
sudo chown $USER:$USER /mnt/onedrive

# Windows
mkdir C:\mnt\onedrive
```

#### 挂载命令
```bash
# Linux - 前台运行 (测试用)
rclone mount onedrive_trading: /mnt/onedrive --vfs-cache-mode writes

# Linux - 后台运行 (生产用)
nohup rclone mount onedrive_trading: /mnt/onedrive \
  --vfs-cache-mode writes \
  --vfs-cache-max-age 10m \
  --vfs-read-chunk-size 32M \
  --vfs-read-chunk-size-limit 1G \
  --buffer-size 32M \
  --log-level INFO \
  --log-file /var/log/rclone.log \
  --daemon &

# Windows
rclone mount onedrive_trading: C:\mnt\onedrive --vfs-cache-mode writes
```

### 4. 验证挂载

```bash
# 检查挂载状态
df -h | grep onedrive
ls -la /mnt/onedrive

# 测试读写
echo "test" > /mnt/onedrive/test.txt
cat /mnt/onedrive/test.txt
rm /mnt/onedrive/test.txt
```

## 🔧 代码集成

### 本地交易软件修改

修改导出路径,直接保存到挂载的OneDrive目录:

```python
# 原来的导出路径
# export_path = "C:/TradingData/"

# 新的OneDrive挂载路径
export_path = "/mnt/onedrive/TradingData/"  # Linux
# export_path = "C:/mnt/onedrive/TradingData/"  # Windows

# 确保目录存在
os.makedirs(export_path, exist_ok=True)

# 导出文件
positions_file = os.path.join(export_path, "latest_positions.json")
balance_file = os.path.join(export_path, "latest_balance.json")
```

### 云端服务器读取

在云端服务器上也挂载相同的OneDrive,直接读取文件:

```python
# 云端服务器读取OneDrive文件
import json
import os

def read_trading_data(data_type):
    """从OneDrive挂载目录读取交易数据"""
    try:
        file_path = f"/mnt/onedrive/TradingData/latest_{data_type}.json"
        
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        else:
            print(f"文件不存在: {file_path}")
            return None
            
    except Exception as e:
        print(f"读取{data_type}数据失败: {e}")
        return None

# 使用示例
positions = read_trading_data("positions")
balance = read_trading_data("balance")
```

## 🔄 自动化脚本

### 启动脚本 (start_rclone.sh)

```bash
#!/bin/bash

# rclone OneDrive挂载启动脚本

MOUNT_POINT="/mnt/onedrive"
REMOTE_NAME="onedrive_trading"
LOG_FILE="/var/log/rclone.log"
PID_FILE="/var/run/rclone.pid"

# 检查是否已经挂载
if mountpoint -q "$MOUNT_POINT"; then
    echo "OneDrive已经挂载在 $MOUNT_POINT"
    exit 0
fi

# 创建挂载点
sudo mkdir -p "$MOUNT_POINT"
sudo chown $USER:$USER "$MOUNT_POINT"

# 启动rclone挂载
echo "启动OneDrive挂载..."
rclone mount "$REMOTE_NAME": "$MOUNT_POINT" \
    --vfs-cache-mode writes \
    --vfs-cache-max-age 10m \
    --vfs-read-chunk-size 32M \
    --buffer-size 32M \
    --log-level INFO \
    --log-file "$LOG_FILE" \
    --daemon \
    --pidfile "$PID_FILE"

# 等待挂载完成
sleep 5

# 验证挂载
if mountpoint -q "$MOUNT_POINT"; then
    echo "✅ OneDrive挂载成功: $MOUNT_POINT"
    echo "📁 可用空间: $(df -h $MOUNT_POINT | tail -1 | awk '{print $4}')"
else
    echo "❌ OneDrive挂载失败"
    exit 1
fi
```

### 停止脚本 (stop_rclone.sh)

```bash
#!/bin/bash

# rclone OneDrive挂载停止脚本

MOUNT_POINT="/mnt/onedrive"
PID_FILE="/var/run/rclone.pid"

# 卸载
if mountpoint -q "$MOUNT_POINT"; then
    echo "卸载OneDrive..."
    fusermount -u "$MOUNT_POINT" || umount "$MOUNT_POINT"
    echo "✅ OneDrive已卸载"
else
    echo "OneDrive未挂载"
fi

# 停止rclone进程
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if kill -0 "$PID" 2>/dev/null; then
        kill "$PID"
        echo "✅ rclone进程已停止"
    fi
    rm -f "$PID_FILE"
fi
```

### 系统服务 (rclone-onedrive.service)

```ini
[Unit]
Description=rclone OneDrive Mount
After=network.target

[Service]
Type=forking
User=your_username
Group=your_group
ExecStart=/usr/local/bin/start_rclone.sh
ExecStop=/usr/local/bin/stop_rclone.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## 🎯 优势

1. **✅ 透明访问** - 像操作本地文件一样操作OneDrive
2. **✅ 实时同步** - 文件修改自动同步到云端
3. **✅ 高性能** - 本地缓存提高访问速度
4. **✅ 跨平台** - Windows/Linux都支持
5. **✅ 可靠性** - 自动重连和错误恢复

## 🔧 故障排除

### 常见问题

1. **挂载失败**
   ```bash
   # 检查rclone配置
   rclone config show
   
   # 测试连接
   rclone ls onedrive_trading:
   ```

2. **权限问题**
   ```bash
   # 修复挂载点权限
   sudo chown -R $USER:$USER /mnt/onedrive
   ```

3. **网络断开**
   ```bash
   # rclone会自动重连,检查日志
   tail -f /var/log/rclone.log
   ```

## 📝 注意事项

1. **网络依赖** - 需要稳定的网络连接
2. **缓存管理** - 合理配置缓存大小和过期时间
3. **权限控制** - 确保服务运行用户有适当权限
4. **监控告警** - 监控挂载状态和同步情况

这个方案比分享链接方案更稳定可靠,适合生产环境使用!
