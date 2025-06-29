# 股票交易系统服务器环境搭建指南

## 1. 安装必要软件

### 安装 Python 3.10 或更高版本
1. 访问 Python 官方网站下载页面:https://www.python.org/downloads/
2. 下载 Python 3.10 或更高版本的 Windows 安装程序
3. 运行安装程序,确保勾选 "Add Python to PATH" 选项
4. 完成安装后,打开命令提示符或 PowerShell,输入 `python --version` 验证安装

### 安装 Node.js (用于前端)
1. 访问 Node.js 官方网站:https://nodejs.org/
2. 下载并安装长期支持版 (LTS)
3. 安装后通过命令 `node --version` 和 `npm --version` 验证

## 2. 配置后端环境

1. 在项目根目录下创建 Python 虚拟环境:
```
cd E:\交易1
python -m venv venv
```

2. 激活虚拟环境:
```
.\venv\Scripts\Activate.ps1
```

3. 安装后端依赖:
```
cd backend
pip install -r requirements.txt
```

4. 创建环境变量配置文件:
   - 复制 `backend/dongwu_broker_env.example` 为 `.env` 文件
   - 编辑 `.env` 文件,填入必要的配置信息

```
# 在项目根目录创建 .env 文件,包含以下内容:

# 数据库配置
DATABASE_URL=sqlite:///./stock_trading.db

# API 配置
TUSHARE_TOKEN=your_tushare_token

# 东吴证券同花顺设置
THS_PATH=C:/同花顺
DONGWU_ACCOUNT_ID=your_dongwu_account_id
DONGWU_ACCOUNT_PWD=your_dongwu_account_password
DONGWU_DEFAULT_BROKER=THS_DONGWU
```

## 3. 配置前端环境

1. 安装前端依赖:
```
cd E:\交易1\frontend\股票
npm install
```

2. 安装 uni-app 开发工具 (全局安装):
```
npm install -g @vue/cli
```

## 4. 启动服务

### 启动后端服务
```
cd E:\交易1
.\venv\Scripts\Activate.ps1
cd backend
# 创建日志目录
mkdir logs
python -m uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### 启动前端服务
```
cd E:\交易1\frontend\股票
npx uni serve
```

## 5. 访问应用

- 后端 API 文档: http://localhost:8000/docs
- 前端界面: http://localhost:9000/

## 6. 常见问题排查

1. 如果安装依赖时出现错误,可能是由于某些包需要编译,确保已安装 Visual C++ 构建工具:
   - 下载地址:https://visualstudio.microsoft.com/visual-cpp-build-tools/

2. 如果启动后端时提示找不到模块,确认是否在正确的虚拟环境中:
   - 检查 PowerShell 提示符前是否有 `(venv)`

3. 如果运行时提示缺少 DLL 文件,可能需要安装 Microsoft Visual C++ Redistributable:
   - 下载地址:https://aka.ms/vs/17/release/vc_redist.x64.exe 
