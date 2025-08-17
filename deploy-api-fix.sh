#!/bin/bash

# 快速修复API端点 - 部署到Cloudflare
echo "🚀 快速修复API端点问题"
echo "=================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查wrangler
check_wrangler() {
    echo -e "${BLUE}🔍 检查Wrangler CLI...${NC}"
    
    if ! command -v wrangler &> /dev/null; then
        echo -e "${RED}❌ Wrangler CLI未安装${NC}"
        echo "安装命令: npm install -g wrangler"
        return 1
    fi
    
    if ! wrangler whoami &> /dev/null; then
        echo -e "${RED}❌ 未登录Cloudflare${NC}"
        echo "登录命令: wrangler login"
        return 1
    fi
    
    echo -e "${GREEN}✅ Wrangler CLI就绪${NC}"
    return 0
}

# 部署API Worker
deploy_api() {
    echo -e "${BLUE}🚀 部署API Worker到Cloudflare...${NC}"
    
    # 检查文件是否存在
    if [ ! -f "cloudflare-api-worker.js" ]; then
        echo -e "${RED}❌ cloudflare-api-worker.js 文件不存在${NC}"
        return 1
    fi
    
    if [ ! -f "wrangler-api.toml" ]; then
        echo -e "${RED}❌ wrangler-api.toml 文件不存在${NC}"
        return 1
    fi
    
    # 部署到生产环境
    echo "部署到生产环境..."
    if wrangler publish --config wrangler-api.toml --env production; then
        echo -e "${GREEN}✅ API Worker部署成功${NC}"
        return 0
    else
        echo -e "${RED}❌ API Worker部署失败${NC}"
        return 1
    fi
}

# 测试API端点
test_api() {
    echo -e "${BLUE}🧪 测试API端点...${NC}"
    
    # 等待部署生效
    echo "等待5秒让部署生效..."
    sleep 5
    
    # 测试关键端点
    endpoints=(
        "https://api.aigupiao.me/"
        "https://api.aigupiao.me/api/agent-analysis"
        "https://api.aigupiao.me/api/account-balance"
        "https://api.aigupiao.me/api/chagubang/health"
    )
    
    success_count=0
    total_count=${#endpoints[@]}
    
    for endpoint in "${endpoints[@]}"; do
        echo "测试: $endpoint"
        
        if curl -s -f "$endpoint" > /dev/null; then
            echo -e "  ${GREEN}✅ 成功${NC}"
            ((success_count++))
        else
            echo -e "  ${RED}❌ 失败${NC}"
        fi
    done
    
    echo ""
    echo "测试结果: $success_count/$total_count 端点正常"
    
    if [ $success_count -eq $total_count ]; then
        echo -e "${GREEN}🎉 所有API端点测试通过！${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️ 部分API端点可能需要时间生效${NC}"
        return 1
    fi
}

# 显示使用说明
show_usage() {
    echo ""
    echo "🎯 API修复完成！"
    echo "=================================="
    echo ""
    echo "📊 可用的API端点:"
    echo "  根路径: https://api.aigupiao.me/"
    echo "  Agent分析: https://api.aigupiao.me/api/agent-analysis"
    echo "  账户余额: https://api.aigupiao.me/api/account-balance"
    echo "  茶股帮数据: https://api.aigupiao.me/api/chagubang/health"
    echo "  实时数据: https://api.aigupiao.me/api/realtime-data/stocks"
    echo "  技术指标: https://api.aigupiao.me/api/technical/indicators"
    echo ""
    echo "🔧 如果前端仍有问题:"
    echo "1. 清除浏览器缓存"
    echo "2. 重新编译前端应用"
    echo "3. 检查前端配置中的baseUrl"
    echo ""
    echo "📱 前端应该现在可以正常工作了！"
}

# 主执行流程
main() {
    echo "AI股票交易系统 - API端点快速修复"
    echo "目标: 修复前端API调用404错误"
    echo ""
    
    # 确认执行
    read -p "确认开始修复? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "修复已取消"
        exit 0
    fi
    
    # 执行修复步骤
    if check_wrangler; then
        if deploy_api; then
            test_api
            show_usage
            echo -e "${GREEN}🎉 API修复完成！${NC}"
            exit 0
        else
            echo -e "${RED}❌ API部署失败${NC}"
            exit 1
        fi
    else
        echo -e "${RED}❌ 环境检查失败${NC}"
        echo ""
        echo "请先安装并配置Wrangler CLI:"
        echo "1. npm install -g wrangler"
        echo "2. wrangler login"
        exit 1
    fi
}

# 错误处理
set -e
trap 'echo -e "${RED}❌ 修复过程中发生错误${NC}"; exit 1' ERR

# 运行主函数
main "$@"
