#!/bin/bash
# Ubuntu云服务器快速安装脚本
# 阿里云混合交易系统一键部署

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# 检查是否为root用户
check_root() {
    if [[ $EUID -eq 0 ]]; then
        log_error "请不要使用root用户运行此脚本，使用普通用户并配置sudo权限"
        exit 1
    fi
}

# 检查Ubuntu版本
check_ubuntu() {
    if [[ ! -f /etc/os-release ]]; then
        log_error "无法检测操作系统版本"
        exit 1
    fi
    
    source /etc/os-release
    if [[ "$ID" != "ubuntu" ]]; then
        log_error "此脚本仅支持Ubuntu系统，当前系统: $ID"
        exit 1
    fi
    
    log_info "检测到Ubuntu系统: $PRETTY_NAME"
}

# 检查网络连接
check_network() {
    log_step "检查网络连接..."
    if ! ping -c 1 8.8.8.8 >/dev/null 2>&1; then
        log_error "网络连接失败，请检查网络设置"
        exit 1
    fi
    log_info "网络连接正常"
}

# 更新系统
update_system() {
    log_step "更新系统包..."
    sudo apt update
    sudo apt upgrade -y
    log_info "系统更新完成"
}

# 安装基础依赖
install_dependencies() {
    log_step "安装基础依赖..."
    
    # 基础包列表
    PACKAGES=(
        "python3.11"
        "python3.11-venv"
        "python3-pip"
        "nginx"
        "supervisor"
        "redis-server"
        "mysql-client"
        "curl"
        "wget"
        "git"
        "htop"
        "vim"
        "unzip"
        "build-essential"
        "libssl-dev"
        "libffi-dev"
        "python3.11-dev"
        "software-properties-common"
        "apt-transport-https"
        "ca-certificates"
        "gnupg"
        "lsb-release"
    )
    
    # 添加Python 3.11 PPA（如果需要）
    if ! python3.11 --version >/dev/null 2>&1; then
        log_info "添加Python 3.11 PPA..."
        sudo add-apt-repository ppa:deadsnakes/ppa -y
        sudo apt update
    fi
    
    # 安装包
    for package in "${PACKAGES[@]}"; do
        log_info "安装: $package"
        sudo apt install -y "$package"
    done
    
    # 设置Python 3.11为默认python3
    sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1
    
    log_info "基础依赖安装完成"
}

# 安装Python包
install_python_packages() {
    log_step "安装Python包..."
    
    # 升级pip
    python3 -m pip install --upgrade pip
    
    # Python包列表
    PYTHON_PACKAGES=(
        "fastapi>=0.104.0"
        "uvicorn[standard]>=0.24.0"
        "aiohttp>=3.9.0"
        "requests>=2.31.0"
        "pandas>=2.1.0"
        "numpy>=1.24.0"
        "pyyaml>=6.0"
        "python-multipart>=0.0.6"
        "psutil>=5.9.0"
        "redis>=5.0.0"
        "pymysql>=1.1.0"
        "cryptography>=41.0.0"
        "python-jose[cryptography]>=3.3.0"
    )
    
    # 安装Python包
    for package in "${PYTHON_PACKAGES[@]}"; do
        log_info "安装Python包: $package"
        python3 -m pip install "$package"
    done
    
    log_info "Python包安装完成"
}

# 创建应用目录
create_directories() {
    log_step "创建应用目录..."
    
    DIRECTORIES=(
        "/opt/trading-system"
        "/opt/trading-system/config"
        "/opt/trading-system/data"
        "/opt/trading-system/backups"
        "/opt/trading-system/scripts"
        "/var/log/trading-system"
        "/var/run/trading-system"
    )
    
    for dir in "${DIRECTORIES[@]}"; do
        sudo mkdir -p "$dir"
        sudo chown -R $USER:$USER "$dir"
        log_info "创建目录: $dir"
    done
    
    log_info "应用目录创建完成"
}

# 配置防火墙
configure_firewall() {
    log_step "配置防火墙..."
    
    # 启用UFW
    sudo ufw --force enable
    
    # 允许SSH
    sudo ufw allow ssh
    
    # 允许HTTP和HTTPS
    sudo ufw allow http
    sudo ufw allow https
    
    # 允许API端口
    sudo ufw allow 8080
    
    # 显示防火墙状态
    sudo ufw status
    
    log_info "防火墙配置完成"
}

# 启动基础服务
start_services() {
    log_step "启动基础服务..."
    
    # 启动并启用Redis
    sudo systemctl start redis-server
    sudo systemctl enable redis-server
    log_info "Redis服务已启动"
    
    # 启动并启用Nginx
    sudo systemctl start nginx
    sudo systemctl enable nginx
    log_info "Nginx服务已启动"
    
    log_info "基础服务启动完成"
}

# 下载项目文件（如果需要）
download_project() {
    log_step "准备项目文件..."
    
    # 如果当前目录没有项目文件，提示用户
    if [[ ! -f "ubuntu_cloud_deployment.py" ]]; then
        log_warn "未找到项目文件，请确保以下文件存在："
        echo "  - ubuntu_cloud_deployment.py"
        echo "  - aliyun_hybrid_implementation.py"
        echo "  - aliyun_deployment_config.yml"
        echo "  - ubuntu_service_manager.py"
        echo ""
        log_info "请将项目文件上传到当前目录，然后重新运行此脚本"
        exit 1
    fi
    
    log_info "项目文件检查完成"
}

# 运行主部署脚本
run_deployment() {
    log_step "运行主部署脚本..."
    
    if [[ -f "ubuntu_cloud_deployment.py" ]]; then
        python3 ubuntu_cloud_deployment.py
        log_info "主部署脚本执行完成"
    else
        log_error "未找到ubuntu_cloud_deployment.py文件"
        exit 1
    fi
}

# 验证安装
verify_installation() {
    log_step "验证安装..."
    
    # 等待服务启动
    sleep 10
    
    # 检查API服务
    if curl -s http://localhost:8080/api/system/status >/dev/null; then
        log_info "✅ API服务运行正常"
    else
        log_warn "⚠️ API服务可能未正常启动"
    fi
    
    # 检查Nginx代理
    if curl -s http://localhost/health >/dev/null; then
        log_info "✅ Nginx代理运行正常"
    else
        log_warn "⚠️ Nginx代理可能未正常配置"
    fi
    
    # 检查Redis
    if redis-cli ping | grep -q PONG; then
        log_info "✅ Redis服务运行正常"
    else
        log_warn "⚠️ Redis服务可能未正常启动"
    fi
    
    log_info "安装验证完成"
}

# 显示安装结果
show_results() {
    echo ""
    echo "=========================================="
    echo "🎉 阿里云混合交易系统安装完成！"
    echo "=========================================="
    echo ""
    echo "📊 服务状态检查："
    echo "   python3 ubuntu_service_manager.py status"
    echo ""
    echo "🏥 系统健康检查："
    echo "   python3 ubuntu_service_manager.py health"
    echo ""
    echo "🌐 访问地址："
    echo "   API文档: http://$(curl -s ifconfig.me)/api/docs"
    echo "   健康检查: http://$(curl -s ifconfig.me)/health"
    echo "   系统状态: http://$(curl -s ifconfig.me)/api/system/status"
    echo ""
    echo "📋 查看日志："
    echo "   sudo journalctl -u trading-system -f"
    echo ""
    echo "🔧 服务管理："
    echo "   sudo systemctl restart trading-system"
    echo "   sudo systemctl status trading-system"
    echo ""
    echo "📁 重要目录："
    echo "   应用目录: /opt/trading-system"
    echo "   日志目录: /var/log/trading-system"
    echo "   配置目录: /opt/trading-system/config"
    echo ""
    echo "=========================================="
}

# 主函数
main() {
    echo "🚀 阿里云混合交易系统 - Ubuntu快速安装"
    echo "=========================================="
    
    # 执行安装步骤
    check_root
    check_ubuntu
    check_network
    update_system
    install_dependencies
    install_python_packages
    create_directories
    configure_firewall
    start_services
    download_project
    run_deployment
    verify_installation
    show_results
    
    log_info "🎉 安装完成！"
}

# 错误处理
trap 'log_error "安装过程中发生错误，请检查日志"; exit 1' ERR

# 运行主函数
main "$@"
