# 依赖包管理说明

## 文件说明

- `requirements.txt` - 主要依赖包，包含所有核心功能所需的包
- `requirements-dev.txt` - 开发环境额外依赖，包含测试、代码格式化等工具
- `requirements-prod.txt` - 生产环境依赖，基于主requirements并添加生产环境特定包

## 安装说明

### 开发环境
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 生产环境
```bash
pip install -r requirements-prod.txt
```

### 虚拟环境（推荐）
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

## 维护说明

1. 新增依赖时，请添加到 `requirements.txt` 并指定版本号
2. 开发工具依赖请添加到 `requirements-dev.txt`
3. 定期更新依赖包版本，确保安全性
4. 使用 `pip freeze > requirements-freeze.txt` 生成精确版本快照

## 版本管理

- 使用 `==` 固定版本号确保环境一致性
- 关键依赖包必须指定版本
- 定期检查包的安全更新
