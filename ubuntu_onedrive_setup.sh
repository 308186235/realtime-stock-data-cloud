#!/bin/bash

# 阿里云Ubuntu OneDrive API自动化部署脚本
# 作者: AI助手
# 用途: 在阿里云ECS Ubuntu上部署OneDrive API服务

echo "🚀 开始阿里云Ubuntu OneDrive API部署..."

# 更新系统
echo "📦 更新系统包..."
sudo apt update && sudo apt upgrade -y

# 安装必要工具
echo "🔧 安装基础工具..."
sudo apt install -y curl wget unzip fuse3 git

# 安装Node.js 18
echo "📦 安装Node.js 18..."
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# 验证安装
echo "✅ 验证Node.js安装..."
node --version
npm --version

# 安装rclone
echo "📦 安装rclone..."
curl https://rclone.org/install.sh | sudo bash

# 验证rclone安装
echo "✅ 验证rclone安装..."
rclone version

# 创建挂载目录
echo "📁 创建OneDrive挂载目录..."
sudo mkdir -p /mnt/onedrive
sudo chown $USER:$USER /mnt/onedrive

# 创建API项目目录
echo "📁 创建API项目目录..."
mkdir -p ~/onedrive-api
cd ~/onedrive-api

# 创建package.json
echo "📄 创建package.json..."
cat > package.json << 'EOF'
{
  "name": "onedrive-trading-api",
  "version": "1.0.0",
  "description": "OneDrive Trading Data API for Cloudflare Workers",
  "main": "server.js",
  "scripts": {
    "start": "node server.js",
    "dev": "nodemon server.js"
  },
  "dependencies": {
    "express": "^4.18.2",
    "cors": "^2.8.5",
    "fs-extra": "^11.1.1",
    "chokidar": "^3.5.3"
  },
  "devDependencies": {
    "nodemon": "^3.0.1"
  }
}
EOF

# 安装依赖
echo "📦 安装Node.js依赖..."
npm install

# 创建API服务器
echo "📄 创建API服务器..."
cat > server.js << 'EOF'
const express = require('express');
const cors = require('cors');
const fs = require('fs-extra');
const path = require('path');
const chokidar = require('chokidar');

const app = express();
const PORT = 8080;

// 中间件
app.use(cors());
app.use(express.json());

// OneDrive挂载路径
const ONEDRIVE_PATH = '/mnt/onedrive/TradingData';

// 文件路径
const POSITIONS_FILE = path.join(ONEDRIVE_PATH, 'positions.json');
const BALANCE_FILE = path.join(ONEDRIVE_PATH, 'balance.json');

// 缓存数据
let cachedPositions = null;
let cachedBalance = null;
let lastPositionsUpdate = 0;
let lastBalanceUpdate = 0;

// 读取文件的安全函数
async function readFileSecurely(filePath) {
    try {
        if (await fs.pathExists(filePath)) {
            const content = await fs.readFile(filePath, 'utf8');
            return JSON.parse(content);
        }
        return null;
    } catch (error) {
        console.error(`读取文件失败 ${filePath}:`, error.message);
        return null;
    }
}

// 更新缓存
async function updateCache() {
    try {
        // 检查文件修改时间
        const positionsStats = await fs.stat(POSITIONS_FILE).catch(() => null);
        const balanceStats = await fs.stat(BALANCE_FILE).catch(() => null);

        // 更新持仓数据
        if (positionsStats && positionsStats.mtimeMs > lastPositionsUpdate) {
            cachedPositions = await readFileSecurely(POSITIONS_FILE);
            lastPositionsUpdate = positionsStats.mtimeMs;
            console.log('✅ 持仓数据已更新');
        }

        // 更新余额数据
        if (balanceStats && balanceStats.mtimeMs > lastBalanceUpdate) {
            cachedBalance = await readFileSecurely(BALANCE_FILE);
            lastBalanceUpdate = balanceStats.mtimeMs;
            console.log('✅ 余额数据已更新');
        }
    } catch (error) {
        console.error('更新缓存失败:', error.message);
    }
}

// 监听文件变化
function setupFileWatcher() {
    const watcher = chokidar.watch(ONEDRIVE_PATH, {
        ignored: /^\./, 
        persistent: true,
        ignoreInitial: false
    });

    watcher.on('change', (filePath) => {
        console.log(`📁 文件变化: ${filePath}`);
        updateCache();
    });

    watcher.on('add', (filePath) => {
        console.log(`📁 新文件: ${filePath}`);
        updateCache();
    });

    console.log(`👀 开始监听目录: ${ONEDRIVE_PATH}`);
}

// API路由

// 健康检查
app.get('/', (req, res) => {
    res.json({
        status: 'success',
        message: 'OneDrive Trading API 运行正常',
        timestamp: new Date().toISOString(),
        server: 'Aliyun ECS Ubuntu'
    });
});

// 状态检查
app.get('/api/status', async (req, res) => {
    try {
        const oneDriveExists = await fs.pathExists(ONEDRIVE_PATH);
        const positionsExists = await fs.pathExists(POSITIONS_FILE);
        const balanceExists = await fs.pathExists(BALANCE_FILE);

        res.json({
            status: 'success',
            onedrive_mounted: oneDriveExists,
            positions_file_exists: positionsExists,
            balance_file_exists: balanceExists,
            cached_positions: cachedPositions !== null,
            cached_balance: cachedBalance !== null,
            last_positions_update: new Date(lastPositionsUpdate).toISOString(),
            last_balance_update: new Date(lastBalanceUpdate).toISOString(),
            timestamp: new Date().toISOString()
        });
    } catch (error) {
        res.status(500).json({
            status: 'error',
            message: error.message,
            timestamp: new Date().toISOString()
        });
    }
});

// 获取持仓数据
app.get('/api/positions', async (req, res) => {
    try {
        if (!cachedPositions) {
            await updateCache();
        }

        if (cachedPositions) {
            res.json({
                status: 'success',
                data: cachedPositions,
                timestamp: new Date().toISOString(),
                last_update: new Date(lastPositionsUpdate).toISOString()
            });
        } else {
            res.status(404).json({
                status: 'error',
                message: '持仓数据文件不存在或无法读取',
                timestamp: new Date().toISOString()
            });
        }
    } catch (error) {
        res.status(500).json({
            status: 'error',
            message: error.message,
            timestamp: new Date().toISOString()
        });
    }
});

// 获取余额数据
app.get('/api/balance', async (req, res) => {
    try {
        if (!cachedBalance) {
            await updateCache();
        }

        if (cachedBalance) {
            res.json({
                status: 'success',
                data: cachedBalance,
                timestamp: new Date().toISOString(),
                last_update: new Date(lastBalanceUpdate).toISOString()
            });
        } else {
            res.status(404).json({
                status: 'error',
                message: '余额数据文件不存在或无法读取',
                timestamp: new Date().toISOString()
            });
        }
    } catch (error) {
        res.status(500).json({
            status: 'error',
            message: error.message,
            timestamp: new Date().toISOString()
        });
    }
});

// 启动服务器
app.listen(PORT, '0.0.0.0', async () => {
    console.log(`🚀 OneDrive Trading API 服务器启动成功!`);
    console.log(`📡 监听地址: http://0.0.0.0:${PORT}`);
    console.log(`🌐 外网访问: http://YOUR_SERVER_IP:${PORT}`);
    
    // 初始化缓存
    await updateCache();
    
    // 设置文件监听
    setupFileWatcher();
    
    // 定期更新缓存
    setInterval(updateCache, 30000); // 每30秒检查一次
});
EOF

# 创建systemd服务文件
echo "⚙️ 创建systemd服务..."
sudo tee /etc/systemd/system/onedrive-api.service > /dev/null << EOF
[Unit]
Description=OneDrive Trading API Service
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$HOME/onedrive-api
ExecStart=/usr/bin/node server.js
Restart=always
RestartSec=10
Environment=NODE_ENV=production

[Install]
WantedBy=multi-user.target
EOF

# 创建rclone挂载服务
echo "⚙️ 创建rclone挂载服务..."
sudo tee /etc/systemd/system/onedrive-mount.service > /dev/null << EOF
[Unit]
Description=OneDrive Mount Service
After=network.target

[Service]
Type=simple
User=$USER
ExecStart=/usr/bin/rclone mount onedrive_trading: /mnt/onedrive --vfs-cache-mode writes --allow-other --allow-non-empty
ExecStop=/bin/fusermount -u /mnt/onedrive
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 重新加载systemd
sudo systemctl daemon-reload

echo "✅ 基础环境部署完成!"
echo ""
echo "🔧 下一步操作:"
echo "1. 配置rclone OneDrive授权: rclone config"
echo "2. 启动挂载服务: sudo systemctl start onedrive-mount"
echo "3. 启动API服务: sudo systemctl start onedrive-api"
echo "4. 检查服务状态: sudo systemctl status onedrive-api"
echo ""
echo "📡 API服务将在 http://YOUR_SERVER_IP:8080 运行"
echo "🔍 测试命令: curl http://localhost:8080"
EOF

chmod +x ubuntu_onedrive_setup.sh
