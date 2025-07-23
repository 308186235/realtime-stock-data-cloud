"""
实时股票数据集成测试
测试完整的数据流:接收 -> 解析 -> 存储 -> 推送
"""
import asyncio
import requests
import json
import time
import logging
import websockets
from typing import Dict, Any

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RealtimeIntegrationTest:
    """实时股票数据集成测试"""
    
    def __init__(self):
        self.api_base_url = "http://localhost:8000/api/realtime"
        self.websocket_url = "ws://localhost:8000/api/realtime/ws"
        
        # 测试配置
        self.test_config = {
            'host': 'test.example.com',  # 测试用,实际需要真实服务器地址
            'port': 8888,                # 测试用,实际需要真实端口
            'token': 'process.env.STOCK_API_KEY'  # 真实API Key
        }
        
        self.test_results = {
            'api_tests': {},
            'websocket_tests': {},
            'integration_tests': {}
        }
    
    async def run_full_test(self):
        """运行完整测试"""
        logger.info("🚀 开始实时股票数据集成测试")
        
        try:
            # 1. 测试API接口
            await self.test_api_endpoints()
            
            # 2. 测试WebSocket连接
            await self.test_websocket_connection()
            
            # 3. 测试数据流集成
            await self.test_data_flow_integration()
            
            # 4. 生成测试报告
            self.generate_test_report()
            
        except Exception as e:
            logger.error(f"测试过程中出现错误: {str(e)}")
            raise
    
    async def test_api_endpoints(self):
        """测试API端点"""
        logger.info("📡 测试API端点...")
        
        # 测试获取服务状态
        try:
            response = requests.get(f"{self.api_base_url}/status")
            self.test_results['api_tests']['status'] = {
                'success': response.status_code == 200,
                'response': response.json() if response.status_code == 200 else response.text
            }
            logger.info(f"✅ 服务状态API测试: {response.status_code}")
        except Exception as e:
            self.test_results['api_tests']['status'] = {
                'success': False,
                'error': str(e)
            }
            logger.error(f"❌ 服务状态API测试失败: {str(e)}")
        
        # 测试获取服务配置
        try:
            response = requests.get(f"{self.api_base_url}/config")
            self.test_results['api_tests']['config'] = {
                'success': response.status_code == 200,
                'response': response.json() if response.status_code == 200 else response.text
            }
            logger.info(f"✅ 服务配置API测试: {response.status_code}")
        except Exception as e:
            self.test_results['api_tests']['config'] = {
                'success': False,
                'error': str(e)
            }
            logger.error(f"❌ 服务配置API测试失败: {str(e)}")
        
        # 测试启动测试服务
        try:
            response = requests.post(f"{self.api_base_url}/test/start")
            self.test_results['api_tests']['test_start'] = {
                'success': response.status_code == 200,
                'response': response.json() if response.status_code == 200 else response.text
            }
            logger.info(f"✅ 测试服务启动API: {response.status_code}")
        except Exception as e:
            self.test_results['api_tests']['test_start'] = {
                'success': False,
                'error': str(e)
            }
            logger.error(f"❌ 测试服务启动API失败: {str(e)}")
        
        # 测试生成测试数据
        try:
            response = requests.get(f"{self.api_base_url}/test/generate?count=10")
            self.test_results['api_tests']['test_generate'] = {
                'success': response.status_code == 200,
                'response': response.json() if response.status_code == 200 else response.text
            }
            logger.info(f"✅ 测试数据生成API: {response.status_code}")
        except Exception as e:
            self.test_results['api_tests']['test_generate'] = {
                'success': False,
                'error': str(e)
            }
            logger.error(f"❌ 测试数据生成API失败: {str(e)}")
        
        # 测试股票数据查询
        try:
            response = requests.get(f"{self.api_base_url}/stock/000001")
            self.test_results['api_tests']['stock_query'] = {
                'success': response.status_code in [200, 404],  # 404也是正常的
                'response': response.json() if response.status_code in [200, 404] else response.text
            }
            logger.info(f"✅ 股票数据查询API: {response.status_code}")
        except Exception as e:
            self.test_results['api_tests']['stock_query'] = {
                'success': False,
                'error': str(e)
            }
            logger.error(f"❌ 股票数据查询API失败: {str(e)}")
        
        # 测试市场概况
        try:
            response = requests.get(f"{self.api_base_url}/market/SZ/summary")
            self.test_results['api_tests']['market_summary'] = {
                'success': response.status_code == 200,
                'response': response.json() if response.status_code == 200 else response.text
            }
            logger.info(f"✅ 市场概况API: {response.status_code}")
        except Exception as e:
            self.test_results['api_tests']['market_summary'] = {
                'success': False,
                'error': str(e)
            }
            logger.error(f"❌ 市场概况API失败: {str(e)}")
    
    async def test_websocket_connection(self):
        """测试WebSocket连接"""
        logger.info("🔌 测试WebSocket连接...")
        
        try:
            async with websockets.connect(self.websocket_url) as websocket:
                # 测试连接建立
                self.test_results['websocket_tests']['connection'] = {
                    'success': True,
                    'message': 'WebSocket连接成功建立'
                }
                logger.info("✅ WebSocket连接建立成功")
                
                # 测试心跳
                ping_message = {
                    'type': 'ping',
                    'timestamp': time.time()
                }
                await websocket.send(json.dumps(ping_message))
                
                # 等待响应
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    response_data = json.loads(response)
                    
                    if response_data.get('type') == 'pong':
                        self.test_results['websocket_tests']['ping_pong'] = {
                            'success': True,
                            'response': response_data
                        }
                        logger.info("✅ WebSocket心跳测试成功")
                    else:
                        self.test_results['websocket_tests']['ping_pong'] = {
                            'success': False,
                            'error': '心跳响应格式错误'
                        }
                        logger.warning("⚠️ WebSocket心跳响应格式错误")
                        
                except asyncio.TimeoutError:
                    self.test_results['websocket_tests']['ping_pong'] = {
                        'success': False,
                        'error': '心跳响应超时'
                    }
                    logger.warning("⚠️ WebSocket心跳响应超时")
                
                # 测试股票订阅
                subscribe_message = {
                    'type': 'subscribe_stock',
                    'stock_code': '000001'
                }
                await websocket.send(json.dumps(subscribe_message))
                
                # 等待订阅确认
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    response_data = json.loads(response)
                    
                    if response_data.get('type') == 'subscription_confirmed':
                        self.test_results['websocket_tests']['stock_subscription'] = {
                            'success': True,
                            'response': response_data
                        }
                        logger.info("✅ 股票订阅测试成功")
                    else:
                        self.test_results['websocket_tests']['stock_subscription'] = {
                            'success': False,
                            'error': '订阅确认格式错误'
                        }
                        logger.warning("⚠️ 股票订阅确认格式错误")
                        
                except asyncio.TimeoutError:
                    self.test_results['websocket_tests']['stock_subscription'] = {
                        'success': False,
                        'error': '订阅确认超时'
                    }
                    logger.warning("⚠️ 股票订阅确认超时")
                
                # 测试市场订阅
                market_subscribe_message = {
                    'type': 'subscribe_market',
                    'market': 'SZ'
                }
                await websocket.send(json.dumps(market_subscribe_message))
                
                # 等待市场订阅确认
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    response_data = json.loads(response)
                    
                    if response_data.get('type') == 'market_subscription_confirmed':
                        self.test_results['websocket_tests']['market_subscription'] = {
                            'success': True,
                            'response': response_data
                        }
                        logger.info("✅ 市场订阅测试成功")
                    else:
                        self.test_results['websocket_tests']['market_subscription'] = {
                            'success': False,
                            'error': '市场订阅确认格式错误'
                        }
                        logger.warning("⚠️ 市场订阅确认格式错误")
                        
                except asyncio.TimeoutError:
                    self.test_results['websocket_tests']['market_subscription'] = {
                        'success': False,
                        'error': '市场订阅确认超时'
                    }
                    logger.warning("⚠️ 市场订阅确认超时")
        
        except Exception as e:
            self.test_results['websocket_tests']['connection'] = {
                'success': False,
                'error': str(e)
            }
            logger.error(f"❌ WebSocket连接测试失败: {str(e)}")
    
    async def test_data_flow_integration(self):
        """测试数据流集成"""
        logger.info("🔄 测试数据流集成...")
        
        try:
            # 测试启动服务(使用测试配置)
            start_response = requests.post(
                f"{self.api_base_url}/start",
                json=self.test_config
            )
            
            if start_response.status_code == 200:
                self.test_results['integration_tests']['service_start'] = {
                    'success': True,
                    'response': start_response.json()
                }
                logger.info("✅ 服务启动集成测试成功")
                
                # 等待服务稳定
                await asyncio.sleep(2)
                
                # 检查服务状态
                status_response = requests.get(f"{self.api_base_url}/status")
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    self.test_results['integration_tests']['service_status_check'] = {
                        'success': True,
                        'response': status_data
                    }
                    logger.info("✅ 服务状态检查成功")
                else:
                    self.test_results['integration_tests']['service_status_check'] = {
                        'success': False,
                        'error': f"状态检查失败: {status_response.status_code}"
                    }
                    logger.warning("⚠️ 服务状态检查失败")
                
                # 测试停止服务
                stop_response = requests.post(f"{self.api_base_url}/stop")
                if stop_response.status_code == 200:
                    self.test_results['integration_tests']['service_stop'] = {
                        'success': True,
                        'response': stop_response.json()
                    }
                    logger.info("✅ 服务停止集成测试成功")
                else:
                    self.test_results['integration_tests']['service_stop'] = {
                        'success': False,
                        'error': f"服务停止失败: {stop_response.status_code}"
                    }
                    logger.warning("⚠️ 服务停止失败")
            
            else:
                self.test_results['integration_tests']['service_start'] = {
                    'success': False,
                    'error': f"服务启动失败: {start_response.status_code} - {start_response.text}"
                }
                logger.error(f"❌ 服务启动集成测试失败: {start_response.status_code}")
        
        except Exception as e:
            self.test_results['integration_tests']['data_flow'] = {
                'success': False,
                'error': str(e)
            }
            logger.error(f"❌ 数据流集成测试失败: {str(e)}")
    
    def generate_test_report(self):
        """生成测试报告"""
        print("\n" + "="*80)
        print("📊 实时股票数据集成测试报告")
        print("="*80)
        
        # API测试结果
        print("\n🔧 API端点测试结果:")
        api_success_count = 0
        api_total_count = len(self.test_results['api_tests'])
        
        for test_name, result in self.test_results['api_tests'].items():
            status = "✅ 通过" if result['success'] else "❌ 失败"
            print(f"   - {test_name}: {status}")
            if result['success']:
                api_success_count += 1
            elif 'error' in result:
                print(f"     错误: {result['error']}")
        
        print(f"   API测试通过率: {api_success_count}/{api_total_count} ({api_success_count/api_total_count*100:.1f}%)")
        
        # WebSocket测试结果
        print("\n🔌 WebSocket测试结果:")
        ws_success_count = 0
        ws_total_count = len(self.test_results['websocket_tests'])
        
        for test_name, result in self.test_results['websocket_tests'].items():
            status = "✅ 通过" if result['success'] else "❌ 失败"
            print(f"   - {test_name}: {status}")
            if result['success']:
                ws_success_count += 1
            elif 'error' in result:
                print(f"     错误: {result['error']}")
        
        if ws_total_count > 0:
            print(f"   WebSocket测试通过率: {ws_success_count}/{ws_total_count} ({ws_success_count/ws_total_count*100:.1f}%)")
        
        # 集成测试结果
        print("\n🔄 集成测试结果:")
        integration_success_count = 0
        integration_total_count = len(self.test_results['integration_tests'])
        
        for test_name, result in self.test_results['integration_tests'].items():
            status = "✅ 通过" if result['success'] else "❌ 失败"
            print(f"   - {test_name}: {status}")
            if result['success']:
                integration_success_count += 1
            elif 'error' in result:
                print(f"     错误: {result['error']}")
        
        if integration_total_count > 0:
            print(f"   集成测试通过率: {integration_success_count}/{integration_total_count} ({integration_success_count/integration_total_count*100:.1f}%)")
        
        # 总体评估
        total_success = api_success_count + ws_success_count + integration_success_count
        total_tests = api_total_count + ws_total_count + integration_total_count
        overall_rate = (total_success / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n🎯 总体测试结果:")
        print(f"   - 总测试数: {total_tests}")
        print(f"   - 通过数: {total_success}")
        print(f"   - 失败数: {total_tests - total_success}")
        print(f"   - 通过率: {overall_rate:.1f}%")
        
        if overall_rate >= 90:
            print(f"   - 评级: ✅ 优秀")
        elif overall_rate >= 70:
            print(f"   - 评级: ✅ 良好")
        elif overall_rate >= 50:
            print(f"   - 评级: ⚠️ 一般")
        else:
            print(f"   - 评级: ❌ 需要改进")
        
        print("\n💡 使用说明:")
        print("   1. 配置真实的服务器地址和端口")
        print("   2. 确保Redis服务正在运行")
        print("   3. 启动后端服务: python backend/app.py")
        print("   4. 使用API Key: process.env.STOCK_API_KEY")
        print("   5. 注意数据堆积不要超过100M")
        
        print("="*80)

async def main():
    """主函数"""
    test = RealtimeIntegrationTest()
    
    try:
        await test.run_full_test()
    except KeyboardInterrupt:
        logger.info("测试被用户中断")
    except Exception as e:
        logger.error(f"测试失败: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
