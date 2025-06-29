# 🚀 frp手动设置指南

## 📥 下载frp

### 方法1：直接下载
1. 访问：https://github.com/fatedier/frp/releases
2. 下载：`frp_0.52.3_windows_amd64.zip`
3. 解压到 `E:\交易8\frp\` 目录

### 方法2：使用百度网盘等国内镜像
如果GitHub下载慢，可以搜索"frp 0.52.3 下载"

## 📝 配置文件

创建 `frpc.ini` 配置文件：

```ini
[common]
# 免费服务器选项1
server_addr = frp.freefrp.net
server_port = 7000
token = freefrp.net

# 免费服务器选项2（备用）
# server_addr = free.frp.icu
# server_port = 7000
# token = 

[stock_api]
type = http
local_ip = 127.0.0.1
local_port = 8000
custom_domains = stock.frp.freefrp.net
```

## 🚀 启动frp

```bash
# 进入frp目录
cd E:\交易8\frp

# 启动客户端
frpc.exe -c frpc.ini
```

## 🌐 访问地址

启动成功后，访问地址：
- **HTTP**: `http://stock.frp.freefrp.net`
- **API测试**: `http://stock.frp.freefrp.net/api/auth/test`

## ⚠️ 注意事项

1. **免费服务器限制**：
   - 可能不稳定
   - 有流量限制
   - 仅供测试使用

2. **生产环境建议**：
   - 使用自己的VPS搭建frp服务器
   - 或者购买商业内网穿透服务

## 🔄 与ngrok对比

| 特性 | ngrok | frp |
|------|-------|-----|
| 免费版稳定性 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| 配置复杂度 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| 自定义域名 | ❌ (付费) | ✅ (免费) |
| 开源 | ❌ | ✅ |
| 流量限制 | 有 | 无 |

## 💡 建议

**当前阶段**：继续使用ngrok，因为它已经工作正常

**长期规划**：如果需要更多控制权，可以考虑：
1. 购买VPS搭建frp服务器
2. 使用商业内网穿透服务
3. 配置固定公网IP + 端口转发
