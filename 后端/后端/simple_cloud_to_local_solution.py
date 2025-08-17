#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的云端到本地交易解决方案
确保云端Agent能够通过API调用本地电脑进行交易
"""

import asyncio
import json
import logging
import time
import requests
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uvicorn
import threading

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 数据模型
class TradeRequest(BaseModel):
    action: str  # buy/sell
    stock_code: str
    quantity: int
    price: Optional[float] = None

class ExportRequest(BaseModel):
    data_type: str = "all"

# 创建FastAPI应用
app = FastAPI(title="本地交易API", version="1.0.0")

# 添加CORS支持
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LocalTradingAPI:
    """本地交易API"""
    
    def __init__(self):
        self.trader_api = None
        self.init_trader_api()
    
    def init_trader_api(self):
        """初始化交易API"""
        try:
            # 尝试导入交易模块
            from trader_api import TraderAPI
            self.trader_api = TraderAPI()
            logger.info("✅ 交易API初始化成功")
        except Exception as e:
            logger.warning(f"⚠️ 交易API初始化失败: {e}")
            logger.info("💡 将使用模拟交易模式")
    
    def execute_trade(self, action: str, stock_code: str, quantity: int, price: Optional[float] = None) -> Dict[str, Any]:
        """执行交易"""
        logger.info(f"💰 执行交易: {action} {stock_code} {quantity}股 @{price or '市价'}")
        
        try:
            if self.trader_api:
                # 使用真实交易API
                if action.lower() == "buy":
                    success = self.trader_api.buy(stock_code, quantity, price or "市价")
                elif action.lower() == "sell":
                    success = self.trader_api.sell(stock_code, quantity, price or "市价")
                else:
                    return {"success": False, "message": f"不支持的交易类型: {action}"}
                
                return {
                    "success": success,
                    "message": f"{action}操作{'成功' if success else '失败'}",
                    "trade_details": {
                        "action": action,
                        "stock_code": stock_code,
                        "quantity": quantity,
                        "price": price or "市价",
                        "timestamp": datetime.now().isoformat()
                    }
                }
            else:
                # 模拟交易
                logger.info("🎭 模拟交易执行")
                return {
                    "success": True,
                    "message": f"模拟{action}操作成功",
                    "trade_details": {
                        "action": action,
                        "stock_code": stock_code,
                        "quantity": quantity,
                        "price": price or "市价",
                        "timestamp": datetime.now().isoformat(),
                        "mode": "simulation"
                    }
                }
                
        except Exception as e:
            logger.error(f"❌ 交易执行失败: {e}")
            return {"success": False, "message": f"交易执行异常: {e}"}
    
    def export_data(self, data_type: str = "all") -> Dict[str, Any]:
        """导出数据"""
        logger.info(f"📊 导出数据: {data_type}")
        
        try:
            if self.trader_api:
                # 使用真实导出API
                if data_type == "holdings":
                    data = self.trader_api.export_holdings()
                elif data_type == "transactions":
                    data = self.trader_api.export_transactions()
                else:
                    data = self.trader_api.export_all()
                
                return {
                    "success": True,
                    "message": "数据导出成功",
                    "data": data,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                # 模拟数据
                mock_data = {
                    "holdings": [
                        {"stock_code": "000001", "stock_name": "平安银行", "quantity": 100, "cost_price": 12.5},
                        {"stock_code": "000002", "stock_name": "万科A", "quantity": 200, "cost_price": 18.3}
                    ],
                    "balance": 50000.0,
                    "total_value": 56160.0
                }
                
                return {
                    "success": True,
                    "message": "模拟数据导出成功",
                    "data": mock_data,
                    "timestamp": datetime.now().isoformat(),
                    "mode": "simulation"
                }
                
        except Exception as e:
            logger.error(f"❌ 数据导出失败: {e}")
            return {"success": False, "message": f"数据导出异常: {e}"}

# 创建全局交易API实例
trading_api = LocalTradingAPI()

# API路由
@app.get("/")
async def root():
    """根路径"""
    return {
        "service": "本地交易API",
        "status": "运行中",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "status": "GET /status",
            "trade": "POST /trade",
            "export": "POST /export",
            "health": "GET /health"
        }
    }

@app.get("/status")
async def get_status():
    """获取状态"""
    return {
        "service_running": True,
        "trader_api_available": trading_api.trader_api is not None,
        "timestamp": datetime.now().isoformat(),
        "mode": "real" if trading_api.trader_api else "simulation"
    }

@app.post("/trade")
async def execute_trade(request: TradeRequest):
    """执行交易"""
    result = trading_api.execute_trade(
        action=request.action,
        stock_code=request.stock_code,
        quantity=request.quantity,
        price=request.price
    )
    
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])
    
    return result

@app.post("/export")
async def export_data(request: ExportRequest):
    """导出数据"""
    result = trading_api.export_data(request.data_type)
    
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])
    
    return result

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

class CloudToLocalTester:
    """云端到本地测试器"""
    
    def __init__(self, local_api_url: str = "http://localhost:8888"):
        self.local_api_url = local_api_url
    
    def test_connection(self):
        """测试连接"""
        try:
            response = requests.get(f"{self.local_api_url}/status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 本地API连接成功")
                print(f"   - 服务状态: {data.get('service_running')}")
                print(f"   - 交易API: {data.get('trader_api_available')}")
                print(f"   - 运行模式: {data.get('mode')}")
                return True
            else:
                print(f"❌ 本地API连接失败: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 本地API连接异常: {e}")
            return False
    
    def test_trade(self):
        """测试交易"""
        try:
            trade_data = {
                "action": "buy",
                "stock_code": "000001",
                "quantity": 100,
                "price": 12.5
            }
            
            response = requests.post(f"{self.local_api_url}/trade", json=trade_data, timeout=10)
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 交易测试成功")
                print(f"   - 操作: {result['trade_details']['action']}")
                print(f"   - 股票: {result['trade_details']['stock_code']}")
                print(f"   - 数量: {result['trade_details']['quantity']}")
                print(f"   - 价格: {result['trade_details']['price']}")
                return True
            else:
                print(f"❌ 交易测试失败: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 交易测试异常: {e}")
            return False
    
    def test_export(self):
        """测试导出"""
        try:
            export_data = {"data_type": "holdings"}
            
            response = requests.post(f"{self.local_api_url}/export", json=export_data, timeout=10)
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 导出测试成功")
                print(f"   - 数据类型: holdings")
                print(f"   - 数据条数: {len(result.get('data', {}).get('holdings', []))}")
                return True
            else:
                print(f"❌ 导出测试失败: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 导出测试异常: {e}")
            return False

def start_local_api_server():
    """启动本地API服务器"""
    logger.info("🚀 启动本地交易API服务器")
    logger.info("📍 地址: http://localhost:8888")
    logger.info("📖 文档: http://localhost:8888/docs")
    
    uvicorn.run(app, host="0.0.0.0", port=8888, log_level="info")

def test_cloud_to_local():
    """测试云端到本地通信"""
    print("🧪 测试云端到本地通信")
    print("=" * 50)
    
    tester = CloudToLocalTester()
    
    # 测试连接
    print("\n1. 测试连接...")
    connection_ok = tester.test_connection()
    
    if connection_ok:
        # 测试交易
        print("\n2. 测试交易...")
        tester.test_trade()
        
        # 测试导出
        print("\n3. 测试导出...")
        tester.test_export()
    else:
        print("\n❌ 连接失败,请确保本地API服务器正在运行")
        print("💡 启动命令: python simple_cloud_to_local_solution.py")

def main():
    """主函数"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # 测试模式
        test_cloud_to_local()
    else:
        # 服务器模式
        start_local_api_server()

if __name__ == "__main__":
    main()
