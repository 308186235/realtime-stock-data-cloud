# 路由器端口转发配置指南

## 🔧 配置步骤

### 1. 获取本机IP
```bash
ipconfig
# 找到你的内网IP，如：192.168.1.100
```

### 2. 登录路由器管理界面
- 通常是：http://192.168.1.1 或 http://192.168.0.1
- 输入管理员账号密码

### 3. 找到端口转发设置
- 通常在：高级设置 → 端口转发 → 虚拟服务器
- 或：网络 → NAT → 端口映射

### 4. 添加转发规则
```
服务名称：股票交易API
外部端口：8000
内部IP：192.168.1.100 (你的电脑IP)
内部端口：8000
协议：TCP
状态：启用
```

### 5. 获取公网IP
```bash
curl ifconfig.me
# 或访问：https://whatismyipaddress.com/
```

### 6. 测试访问
```
http://你的公网IP:8000/api/auth/test
```

## ⚠️ 注意事项
- 需要路由器管理权限
- 公网IP可能会变化（动态IP）
- 需要考虑安全性
- 防火墙可能需要配置
