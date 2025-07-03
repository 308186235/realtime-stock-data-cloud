#!/bin/bash

# 茶股帮数据源 - Cloudflare部署脚本
# 自动部署茶股帮集成到Cloudflare Workers

echo "🚀 开始部署茶股帮数据源到Cloudflare..."
echo "=================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查必要工具
check_requirements() {
    echo -e "${BLUE}🔍 检查部署要求...${NC}"
    
    # 检查wrangler CLI
    if ! command -v wrangler &> /dev/null; then
        echo -e "${RED}❌ Wrangler CLI未安装${NC}"
        echo "请运行: npm install -g wrangler"
        exit 1
    fi
    
    # 检查是否已登录
    if ! wrangler whoami &> /dev/null; then
        echo -e "${RED}❌ 未登录Cloudflare${NC}"
        echo "请运行: wrangler login"
        exit 1
    fi
    
    echo -e "${GREEN}✅ 部署要求检查通过${NC}"
}

# 创建KV命名空间
create_kv_namespaces() {
    echo -e "${BLUE}📦 创建KV命名空间...${NC}"
    
    # 创建生产环境KV命名空间
    echo "创建股票缓存命名空间..."
    STOCK_CACHE_ID=$(wrangler kv:namespace create "STOCK_CACHE" --preview false | grep -o 'id = "[^"]*"' | cut -d'"' -f2)
    STOCK_CACHE_PREVIEW_ID=$(wrangler kv:namespace create "STOCK_CACHE" --preview | grep -o 'id = "[^"]*"' | cut -d'"' -f2)
    
    echo "创建市场数据命名空间..."
    MARKET_DATA_ID=$(wrangler kv:namespace create "MARKET_DATA" --preview false | grep -o 'id = "[^"]*"' | cut -d'"' -f2)
    MARKET_DATA_PREVIEW_ID=$(wrangler kv:namespace create "MARKET_DATA" --preview | grep -o 'id = "[^"]*"' | cut -d'"' -f2)
    
    echo "创建用户会话命名空间..."
    USER_SESSIONS_ID=$(wrangler kv:namespace create "USER_SESSIONS" --preview false | grep -o 'id = "[^"]*"' | cut -d'"' -f2)
    USER_SESSIONS_PREVIEW_ID=$(wrangler kv:namespace create "USER_SESSIONS" --preview | grep -o 'id = "[^"]*"' | cut -d'"' -f2)
    
    echo -e "${GREEN}✅ KV命名空间创建完成${NC}"
    echo "STOCK_CACHE_ID: $STOCK_CACHE_ID"
    echo "MARKET_DATA_ID: $MARKET_DATA_ID"
    echo "USER_SESSIONS_ID: $USER_SESSIONS_ID"
}

# 更新wrangler.toml配置
update_wrangler_config() {
    echo -e "${BLUE}⚙️ 更新Wrangler配置...${NC}"
    
    # 备份原配置
    if [ -f "wrangler-chagubang.toml" ]; then
        cp wrangler-chagubang.toml wrangler-chagubang.toml.backup
    fi
    
    # 更新KV命名空间ID
    sed -i "s/your-stock-cache-namespace-id/$STOCK_CACHE_ID/g" wrangler-chagubang.toml
    sed -i "s/your-market-data-namespace-id/$MARKET_DATA_ID/g" wrangler-chagubang.toml
    sed -i "s/your-user-sessions-namespace-id/$USER_SESSIONS_ID/g" wrangler-chagubang.toml
    
    # 更新开发环境ID
    sed -i "s/your-dev-stock-cache-namespace-id/$STOCK_CACHE_PREVIEW_ID/g" wrangler-chagubang.toml
    sed -i "s/your-dev-market-data-namespace-id/$MARKET_DATA_PREVIEW_ID/g" wrangler-chagubang.toml
    sed -i "s/your-dev-user-sessions-namespace-id/$USER_SESSIONS_PREVIEW_ID/g" wrangler-chagubang.toml
    
    echo -e "${GREEN}✅ Wrangler配置更新完成${NC}"
}

# 设置密钥
setup_secrets() {
    echo -e "${BLUE}🔐 设置Worker密钥...${NC}"
    
    # 设置Supabase Service Key
    echo "设置Supabase Service Key..."
    echo "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp6dWtmeHdhdmtuc2txY2Vwc2piIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MTI5ODUwNiwiZXhwIjoyMDY2ODc0NTA2fQ.Ksy_A6qfaUn9qBethAw4o8Xpn0iSxluaBTCxbnd3u5g" | wrangler secret put SUPABASE_SERVICE_KEY --config wrangler-chagubang.toml
    
    echo -e "${GREEN}✅ 密钥设置完成${NC}"
}

# 部署Worker
deploy_worker() {
    echo -e "${BLUE}🚀 部署Cloudflare Worker...${NC}"
    
    # 部署到生产环境
    wrangler publish --config wrangler-chagubang.toml --env production
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Worker部署成功${NC}"
    else
        echo -e "${RED}❌ Worker部署失败${NC}"
        exit 1
    fi
}

# 初始化Supabase数据库
setup_supabase() {
    echo -e "${BLUE}🗄️ 初始化Supabase数据库...${NC}"
    
    echo "请在Supabase控制台中执行以下SQL脚本："
    echo "文件: supabase-chagubang-schema.sql"
    echo ""
    echo "或者访问: https://supabase.com/dashboard/project/zzukfxwavknskqcepsjb/sql"
    echo ""
    read -p "按Enter键继续，当您完成数据库初始化后..."
    
    echo -e "${GREEN}✅ 数据库初始化完成${NC}"
}

# 测试部署
test_deployment() {
    echo -e "${BLUE}🧪 测试部署...${NC}"
    
    # 测试健康检查
    echo "测试健康检查..."
    HEALTH_RESPONSE=$(curl -s "https://api.aigupiao.me/api/chagubang/health")
    
    if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
        echo -e "${GREEN}✅ 健康检查通过${NC}"
    else
        echo -e "${YELLOW}⚠️ 健康检查可能有问题${NC}"
        echo "响应: $HEALTH_RESPONSE"
    fi
    
    # 测试API端点
    echo "测试API端点..."
    API_RESPONSE=$(curl -s "https://api.aigupiao.me/api/chagubang/stats")
    
    if echo "$API_RESPONSE" | grep -q "success"; then
        echo -e "${GREEN}✅ API端点测试通过${NC}"
    else
        echo -e "${YELLOW}⚠️ API端点可能有问题${NC}"
        echo "响应: $API_RESPONSE"
    fi
}

# 显示部署信息
show_deployment_info() {
    echo ""
    echo "🎉 茶股帮数据源部署完成！"
    echo "=================================="
    echo ""
    echo "📊 API端点:"
    echo "  健康检查: https://api.aigupiao.me/api/chagubang/health"
    echo "  股票数据: https://api.aigupiao.me/api/chagubang/stocks"
    echo "  市场概览: https://api.aigupiao.me/api/chagubang/market/overview"
    echo "  热门股票: https://api.aigupiao.me/api/chagubang/market/hot"
    echo "  搜索股票: https://api.aigupiao.me/api/chagubang/search?q=平安"
    echo "  服务统计: https://api.aigupiao.me/api/chagubang/stats"
    echo ""
    echo "🔧 管理端点:"
    echo "  添加Token: POST https://api.aigupiao.me/api/chagubang/token/add"
    echo "  测试Token: POST https://api.aigupiao.me/api/chagubang/token/test"
    echo ""
    echo "📋 下一步操作:"
    echo "1. 添加茶股帮Token:"
    echo "   curl -X POST https://api.aigupiao.me/api/chagubang/token/add \\"
    echo "        -H 'Content-Type: application/json' \\"
    echo "        -d '{\"token\":\"您的Token\",\"description\":\"生产Token\"}'"
    echo ""
    echo "2. 测试Token:"
    echo "   curl -X POST https://api.aigupiao.me/api/chagubang/token/test \\"
    echo "        -H 'Content-Type: application/json' \\"
    echo "        -d '{\"token\":\"您的Token\"}'"
    echo ""
    echo "3. 更新前端配置，使用新的API端点"
    echo ""
    echo "🎯 系统特性:"
    echo "  ✅ Cloudflare Workers高性能"
    echo "  ✅ Supabase数据存储"
    echo "  ✅ KV缓存加速"
    echo "  ✅ 定时数据同步"
    echo "  ✅ Token管理"
    echo "  ✅ 全球CDN加速"
    echo ""
}

# 主执行流程
main() {
    echo "茶股帮数据源 - Cloudflare部署"
    echo "适用于: api.aigupiao.me"
    echo "数据库: Supabase"
    echo ""
    
    # 确认部署
    read -p "确认开始部署? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "部署已取消"
        exit 0
    fi
    
    # 执行部署步骤
    check_requirements
    create_kv_namespaces
    update_wrangler_config
    setup_secrets
    setup_supabase
    deploy_worker
    test_deployment
    show_deployment_info
    
    echo -e "${GREEN}🎉 部署完成！${NC}"
}

# 错误处理
set -e
trap 'echo -e "${RED}❌ 部署过程中发生错误${NC}"; exit 1' ERR

# 运行主函数
main "$@"
