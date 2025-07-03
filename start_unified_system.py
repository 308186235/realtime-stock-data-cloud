#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一系统启动脚本
启动完整的AI股票交易系统，包括：
1. 后端API服务
2. 统一本地Agent
3. WebSocket管理器
4. 数据流管理器
"""

import asyncio
import subprocess
import sys
import time
import logging
import signal
import os
import requests
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class UnifiedSystemManager:
    """统一系统管理器"""
    
    def __init__(self):
        self.processes = {}
        self.running = False
        
    async def start_all_services(self):
        """启动所有服务"""
        logger.info("🚀 启动统一AI股票交易系统")
        logger.info("="*80)
        logger.info("系统组件:")
        logger.info("  ✅ 后端API服务 (FastAPI)")
        logger.info("  ✅ 统一本地Agent (WebSocket客户端)")
        logger.info("  ✅ WebSocket管理器 (云端本地通信)")
        logger.info("  ✅ 数据流管理器 (茶股帮数据处理)")
        logger.info("  ✅ 配置管理器 (北交所开关等)")
        logger.info("="*80)
        
        self.running = True
        
        try:
            # 1. 检查环境
            await self.check_environment()
            
            # 2. 启动后端API服务
            await self.start_backend_api()
            
            # 3. 等待后端启动
            await self.wait_for_backend()
            
            # 4. 启动统一本地Agent
            await self.start_unified_local_agent()
            
            # 5. 等待服务稳定
            await asyncio.sleep(5)
            
            # 6. 验证系统连接
            await self.verify_system_connections()
            
            # 7. 显示系统状态
            await self.show_system_status()
            
            # 8. 运行系统测试
            await self.run_system_tests()
            
            # 9. 监控服务运行
            await self.monitor_services()
            
        except KeyboardInterrupt:
            logger.info("收到中断信号，正在停止服务...")
        except Exception as e:
            logger.error(f"系统启动失败: {e}")
        finally:
            await self.stop_all_services()
    
    async def check_environment(self):
        """检查环境"""
        logger.info("🔍 检查运行环境")
        
        # 检查Python版本
        if sys.version_info < (3, 7):
            raise Exception("需要Python 3.7或更高版本")
        logger.info(f"✅ Python版本: {sys.version}")
        
        # 检查必要文件
        required_files = [
            "backend/app.py",
            "unified_local_agent.py",
            "backend/services/unified_websocket_manager.py",
            "backend/services/data_flow_manager.py",
            "backend/api/cloud_local_trading_api.py",
            "炒股养家/services/unifiedAgentService.js"
        ]
        
        missing_files = []
        for file_path in required_files:
            if not os.path.exists(file_path):
                missing_files.append(file_path)
        
        if missing_files:
            logger.error("❌ 缺少必要文件:")
            for file_path in missing_files:
                logger.error(f"   - {file_path}")
            raise Exception("缺少必要文件")
        
        logger.info("✅ 环境检查通过")
    
    async def start_backend_api(self):
        """启动后端API服务"""
        logger.info("🌐 启动后端API服务")
        
        try:
            # 切换到backend目录
            backend_dir = "backend"
            if not os.path.exists(backend_dir):
                backend_dir = "."
            
            # 启动FastAPI服务
            cmd = [
                sys.executable, "-m", "uvicorn", 
                "app:app", 
                "--host", "0.0.0.0", 
                "--port", "8000", 
                "--reload"
            ]
            
            process = subprocess.Popen(
                cmd,
                cwd=backend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.processes["backend"] = process
            logger.info("✅ 后端API服务启动中...")
            
        except Exception as e:
            logger.error(f"❌ 后端API服务启动失败: {e}")
            raise
    
    async def wait_for_backend(self):
        """等待后端服务启动"""
        logger.info("⏳ 等待后端服务启动...")
        
        max_attempts = 30
        for attempt in range(max_attempts):
            try:
                response = requests.get("http://localhost:8000/health", timeout=2)
                if response.status_code == 200:
                    logger.info("✅ 后端服务已启动")
                    return
            except:
                pass
            
            await asyncio.sleep(2)
            logger.info(f"   尝试 {attempt + 1}/{max_attempts}")
        
        raise Exception("后端服务启动超时")
    
    async def start_unified_local_agent(self):
        """启动统一本地Agent"""
        logger.info("🤖 启动统一本地Agent")
        
        try:
            if os.path.exists("unified_local_agent.py"):
                cmd = [sys.executable, "unified_local_agent.py"]
                
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                self.processes["local_agent"] = process
                logger.info("✅ 统一本地Agent启动中...")
            else:
                logger.warning("⚠️ unified_local_agent.py 文件不存在")
                
        except Exception as e:
            logger.error(f"❌ 统一本地Agent启动失败: {e}")
    
    async def verify_system_connections(self):
        """验证系统连接"""
        logger.info("🔗 验证系统连接")
        
        try:
            # 检查后端API
            response = requests.get("http://localhost:8000/api/config/status", timeout=5)
            if response.status_code == 200:
                logger.info("✅ 后端API连接正常")
            else:
                logger.warning("⚠️ 后端API连接异常")
            
            # 检查本地Agent
            try:
                response = requests.get("http://localhost:8080/status", timeout=3)
                if response.status_code == 200:
                    logger.info("✅ 本地Agent连接正常")
                else:
                    logger.warning("⚠️ 本地Agent连接异常")
            except:
                logger.warning("⚠️ 本地Agent未响应")
            
            # 检查WebSocket连接
            try:
                response = requests.get("http://localhost:8000/api/cloud-local/connections", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    connections = data.get("connections", {})
                    local_agents = len(connections.get("local_agents", []))
                    logger.info(f"✅ WebSocket连接: {local_agents}个本地Agent")
                else:
                    logger.warning("⚠️ WebSocket连接状态未知")
            except:
                logger.warning("⚠️ 无法获取WebSocket连接状态")
                
        except Exception as e:
            logger.error(f"❌ 验证系统连接失败: {e}")
    
    async def show_system_status(self):
        """显示系统状态"""
        logger.info("\n" + "="*80)
        logger.info("📊 系统状态")
        logger.info("="*80)
        
        # 显示进程状态
        for service_name, process in self.processes.items():
            if process.poll() is None:
                logger.info(f"✅ {service_name}: 运行中 (PID: {process.pid})")
            else:
                logger.info(f"❌ {service_name}: 已停止")
        
        # 显示访问地址
        logger.info("\n🌐 服务地址:")
        logger.info("  - 后端API: http://localhost:8000")
        logger.info("  - API文档: http://localhost:8000/docs")
        logger.info("  - 配置管理: http://localhost:8000/api/config")
        logger.info("  - 本地Agent: http://localhost:8080")
        
        # 显示WebSocket地址
        logger.info("\n🔗 WebSocket连接:")
        logger.info("  - 本地Agent: ws://localhost:8000/ws/local-agent")
        logger.info("  - 前端客户端: ws://localhost:8000/ws/agent-client")
        
        # 显示前端信息
        logger.info("\n📱 前端应用:")
        logger.info("  - 项目路径: ./炒股养家")
        logger.info("  - 启动方式: 使用HBuilderX运行项目")
        logger.info("  - Agent控制台: 导航第一个tab")
        
        logger.info("\n📋 使用说明:")
        logger.info("1. 所有后端服务已启动")
        logger.info("2. 在HBuilderX中运行前端项目")
        logger.info("3. 访问Agent控制台管理系统")
        logger.info("4. 在设置页面配置北交所权限")
        logger.info("5. 按 Ctrl+C 停止所有服务")
        
        logger.info("="*80)
    
    async def run_system_tests(self):
        """运行系统测试"""
        logger.info("🧪 运行系统测试")
        
        try:
            # 运行完整系统测试
            if os.path.exists("test_complete_system.py"):
                logger.info("📋 执行完整系统测试...")
                
                # 在后台运行测试
                test_process = subprocess.Popen(
                    [sys.executable, "test_complete_system.py"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                # 等待测试完成（最多30秒）
                try:
                    stdout, stderr = test_process.communicate(timeout=30)
                    if test_process.returncode == 0:
                        logger.info("✅ 系统测试通过")
                    else:
                        logger.warning("⚠️ 系统测试有警告")
                except subprocess.TimeoutExpired:
                    test_process.kill()
                    logger.warning("⚠️ 系统测试超时")
            else:
                logger.info("ℹ️ 跳过系统测试（测试文件不存在）")
                
        except Exception as e:
            logger.error(f"❌ 系统测试失败: {e}")
    
    async def monitor_services(self):
        """监控服务运行状态"""
        logger.info("👀 开始监控服务状态...")
        logger.info("💡 提示: 按 Ctrl+C 停止所有服务")
        
        while self.running:
            try:
                # 检查进程状态
                for service_name, process in list(self.processes.items()):
                    if process.poll() is not None:
                        logger.warning(f"⚠️ 服务 {service_name} 已停止")
                        
                        # 读取错误输出
                        if process.stderr:
                            stderr_output = process.stderr.read()
                            if stderr_output:
                                logger.error(f"❌ {service_name} 错误: {stderr_output[:500]}")
                
                # 每60秒检查一次
                await asyncio.sleep(60)
                
            except Exception as e:
                logger.error(f"❌ 监控服务时出错: {e}")
                await asyncio.sleep(10)
    
    async def stop_all_services(self):
        """停止所有服务"""
        logger.info("🛑 停止所有服务")
        
        self.running = False
        
        for service_name, process in self.processes.items():
            try:
                if process.poll() is None:
                    logger.info(f"🔄 停止 {service_name}...")
                    
                    # 尝试优雅停止
                    process.terminate()
                    
                    # 等待进程结束
                    try:
                        process.wait(timeout=10)
                        logger.info(f"✅ {service_name} 已停止")
                    except subprocess.TimeoutExpired:
                        # 强制杀死进程
                        process.kill()
                        logger.info(f"🔪 强制停止 {service_name}")
                        
            except Exception as e:
                logger.error(f"❌ 停止 {service_name} 时出错: {e}")
        
        logger.info("✅ 所有服务已停止")

def signal_handler(signum, frame):
    """信号处理器"""
    logger.info("收到停止信号，正在关闭系统...")
    sys.exit(0)

async def main():
    """主函数"""
    # 设置信号处理
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 显示启动信息
    logger.info("🎯 统一AI股票交易系统启动器")
    logger.info(f"启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("="*80)
    
    # 启动系统管理器
    manager = UnifiedSystemManager()
    await manager.start_all_services()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 系统已停止")
    except Exception as e:
        logger.error(f"❌ 系统启动失败: {e}")
        sys.exit(1)
