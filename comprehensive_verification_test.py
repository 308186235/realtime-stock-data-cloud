#!/usr/bin/env python3
"""
全面验证测试 - 再次检查所有功能
确保云端Agent真的可以获取所有本地数据
"""

import requests
import time
import json
from datetime import datetime
import sys

class ComprehensiveVerificationTest:
    def __init__(self):
        self.config = {
            'local_server': 'http://localhost:8890',
            'cloud_server': 'https://2bedf35d6777.ngrok-free.app',
            'timeout': 30
        }
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'VerificationTest/1.0',
            'Accept': 'application/json'
        })
        
        self.verification_results = {}
        self.critical_failures = []
        self.warnings = []
    
    def log(self, message, level="INFO"):
        """记录日志"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        colors = {
            "INFO": "\033[36m",
            "SUCCESS": "\033[32m",
            "WARNING": "\033[33m",
            "ERROR": "\033[31m",
            "CRITICAL": "\033[91m",
            "RESET": "\033[0m"
        }
        color = colors.get(level, colors["INFO"])
        print(f"{color}[{timestamp}] [{level}] {message}{colors['RESET']}")
    
    def verify_service_availability(self):
        """验证服务可用性"""
        self.log("🔍 验证服务可用性...", "INFO")
        
        # 检查本地服务
        try:
            response = requests.get(f"{self.config['local_server']}/health", timeout=5)
            if response.status_code == 200:
                self.log("✅ 本地服务正常运行", "SUCCESS")
                local_available = True
            else:
                self.log(f"❌ 本地服务异常: {response.status_code}", "ERROR")
                local_available = False
                self.critical_failures.append("本地服务不可用")
        except Exception as e:
            self.log(f"❌ 本地服务连接失败: {e}", "ERROR")
            local_available = False
            self.critical_failures.append(f"本地服务连接失败: {e}")
        
        # 检查云端服务
        try:
            response = requests.get(f"{self.config['cloud_server']}/health", timeout=10)
            if response.status_code == 200:
                self.log("✅ 云端服务正常运行", "SUCCESS")
                cloud_available = True
            else:
                self.log(f"❌ 云端服务异常: {response.status_code}", "ERROR")
                cloud_available = False
                self.critical_failures.append("云端服务不可用")
        except Exception as e:
            self.log(f"❌ 云端服务连接失败: {e}", "ERROR")
            cloud_available = False
            self.critical_failures.append(f"云端服务连接失败: {e}")
        
        self.verification_results['service_availability'] = {
            'local': local_available,
            'cloud': cloud_available,
            'both_available': local_available and cloud_available
        }
        
        return local_available and cloud_available
    
    def verify_data_endpoints(self):
        """验证数据端点"""
        self.log("📊 验证数据端点...", "INFO")
        
        critical_endpoints = [
            {'name': '账户余额', 'path': '/balance', 'required_fields': ['total_assets', 'available_cash']},
            {'name': '持仓信息', 'path': '/positions', 'required_fields': ['positions', 'total_positions']},
            {'name': '成交记录', 'path': '/trades', 'required_fields': ['trades', 'total_trades']},
            {'name': '委托订单', 'path': '/orders', 'required_fields': ['orders', 'total_orders']},
            {'name': '历史记录', 'path': '/history', 'required_fields': ['trades', 'orders', 'positions']}
        ]
        
        endpoint_results = {}
        
        for endpoint in critical_endpoints:
            self.log(f"🧪 验证: {endpoint['name']}")
            
            try:
                # 测试云端访问
                response = self.session.get(f"{self.config['cloud_server']}{endpoint['path']}", timeout=15)
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        
                        # 检查必需字段
                        missing_fields = []
                        for field in endpoint['required_fields']:
                            if field not in data:
                                missing_fields.append(field)
                        
                        if not missing_fields:
                            self.log(f"   ✅ {endpoint['name']}: 数据完整", "SUCCESS")
                            endpoint_results[endpoint['name']] = {
                                'accessible': True,
                                'data_complete': True,
                                'response_size': len(response.content)
                            }
                            
                            # 显示关键数据
                            self.display_key_data(endpoint['name'], data)
                            
                        else:
                            self.log(f"   ⚠️ {endpoint['name']}: 缺少字段 {missing_fields}", "WARNING")
                            self.warnings.append(f"{endpoint['name']}缺少字段: {missing_fields}")
                            endpoint_results[endpoint['name']] = {
                                'accessible': True,
                                'data_complete': False,
                                'missing_fields': missing_fields
                            }
                    
                    except json.JSONDecodeError:
                        self.log(f"   ❌ {endpoint['name']}: 响应不是有效JSON", "ERROR")
                        self.critical_failures.append(f"{endpoint['name']}响应格式错误")
                        endpoint_results[endpoint['name']] = {
                            'accessible': False,
                            'error': 'invalid_json'
                        }
                
                else:
                    self.log(f"   ❌ {endpoint['name']}: HTTP {response.status_code}", "ERROR")
                    self.critical_failures.append(f"{endpoint['name']}不可访问: {response.status_code}")
                    endpoint_results[endpoint['name']] = {
                        'accessible': False,
                        'status_code': response.status_code
                    }
            
            except Exception as e:
                self.log(f"   ❌ {endpoint['name']}: 异常 - {e}", "ERROR")
                self.critical_failures.append(f"{endpoint['name']}访问异常: {e}")
                endpoint_results[endpoint['name']] = {
                    'accessible': False,
                    'error': str(e)
                }
        
        self.verification_results['data_endpoints'] = endpoint_results
        return endpoint_results
    
    def display_key_data(self, endpoint_name, data):
        """显示关键数据"""
        if endpoint_name == '账户余额':
            total_assets = data.get('total_assets', 0)
            available_cash = data.get('available_cash', 0)
            self.log(f"     💰 总资产: {total_assets}, 可用资金: {available_cash}", "INFO")
        
        elif endpoint_name == '持仓信息':
            positions = data.get('positions', [])
            total_positions = data.get('total_positions', 0)
            self.log(f"     📊 持仓数量: {total_positions}, 实际记录: {len(positions)}", "INFO")
            if positions:
                first_pos = positions[0]
                self.log(f"     📈 样本: {first_pos.get('stock_code')} - {first_pos.get('quantity')}股", "INFO")
        
        elif endpoint_name == '成交记录':
            trades = data.get('trades', [])
            total_trades = data.get('total_trades', 0)
            self.log(f"     📋 成交记录: {total_trades}, 实际记录: {len(trades)}", "INFO")
            if trades:
                recent_trade = trades[-1]  # 最新的交易
                self.log(f"     💼 最新: {recent_trade.get('action')} {recent_trade.get('stock_code')}", "INFO")
        
        elif endpoint_name == '委托订单':
            orders = data.get('orders', [])
            pending_orders = data.get('pending_orders', 0)
            self.log(f"     📝 订单数量: {len(orders)}, 待成交: {pending_orders}", "INFO")
    
    def verify_export_functionality(self):
        """验证导出功能"""
        self.log("📤 验证导出功能...", "INFO")
        
        export_tests = [
            {'name': '导出持仓JSON', 'path': '/export/positions', 'format': 'json'},
            {'name': '导出持仓CSV', 'path': '/export/positions?format=csv', 'format': 'csv'},
            {'name': '导出成交JSON', 'path': '/export/trades', 'format': 'json'},
            {'name': '导出全部数据', 'path': '/export/all', 'format': 'json'}
        ]
        
        export_results = {}
        
        for export_test in export_tests:
            self.log(f"📋 验证: {export_test['name']}")
            
            try:
                response = self.session.get(f"{self.config['cloud_server']}{export_test['path']}", timeout=20)
                
                if response.status_code == 200:
                    content_size = len(response.content)
                    
                    if export_test['format'] == 'json':
                        try:
                            data = response.json()
                            self.log(f"   ✅ {export_test['name']}: {content_size}字节 JSON数据", "SUCCESS")
                            export_results[export_test['name']] = {
                                'success': True,
                                'size': content_size,
                                'format': 'json',
                                'data_keys': list(data.keys()) if isinstance(data, dict) else []
                            }
                        except json.JSONDecodeError:
                            self.log(f"   ❌ {export_test['name']}: JSON解析失败", "ERROR")
                            export_results[export_test['name']] = {'success': False, 'error': 'json_parse_error'}
                    
                    elif export_test['format'] == 'csv':
                        # CSV格式验证
                        content = response.text
                        lines = content.split('\n')
                        self.log(f"   ✅ {export_test['name']}: {len(lines)}行 CSV数据", "SUCCESS")
                        export_results[export_test['name']] = {
                            'success': True,
                            'size': content_size,
                            'format': 'csv',
                            'lines': len(lines)
                        }
                
                else:
                    self.log(f"   ❌ {export_test['name']}: HTTP {response.status_code}", "ERROR")
                    export_results[export_test['name']] = {
                        'success': False,
                        'status_code': response.status_code
                    }
            
            except Exception as e:
                self.log(f"   ❌ {export_test['name']}: 异常 - {e}", "ERROR")
                export_results[export_test['name']] = {
                    'success': False,
                    'error': str(e)
                }
        
        self.verification_results['export_functionality'] = export_results
        return export_results
    
    def verify_trading_functionality(self):
        """验证交易功能"""
        self.log("💼 验证交易功能...", "INFO")
        
        # 测试交易执行
        trade_data = {
            'action': 'buy',
            'stock_code': '000001',
            'quantity': 100,
            'price': 13.80
        }
        
        try:
            self.log("🧪 测试交易执行...")
            response = self.session.post(
                f"{self.config['cloud_server']}/trade",
                json=trade_data,
                timeout=20
            )
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    
                    # 检查交易结果
                    if result.get('success'):
                        trade_id = result.get('trade_id')
                        status = result.get('status')
                        message = result.get('message')
                        
                        self.log(f"   ✅ 交易执行成功: {trade_id}", "SUCCESS")
                        self.log(f"   📊 状态: {status}, 消息: {message}", "INFO")
                        
                        trading_result = {
                            'success': True,
                            'trade_id': trade_id,
                            'status': status,
                            'response_complete': True
                        }
                    else:
                        self.log(f"   ⚠️ 交易执行失败: {result.get('message', '未知错误')}", "WARNING")
                        trading_result = {
                            'success': False,
                            'error': result.get('message', '未知错误')
                        }
                
                except json.JSONDecodeError:
                    self.log("   ❌ 交易响应JSON解析失败", "ERROR")
                    trading_result = {'success': False, 'error': 'json_parse_error'}
            
            else:
                self.log(f"   ❌ 交易请求失败: HTTP {response.status_code}", "ERROR")
                trading_result = {'success': False, 'status_code': response.status_code}
        
        except Exception as e:
            self.log(f"   ❌ 交易功能异常: {e}", "ERROR")
            trading_result = {'success': False, 'error': str(e)}
        
        self.verification_results['trading_functionality'] = trading_result
        return trading_result
    
    def verify_data_consistency(self):
        """验证数据一致性"""
        self.log("🔍 验证数据一致性...", "INFO")
        
        # 多次获取同一数据,检查一致性
        consistency_tests = ['/balance', '/positions', '/trades']
        consistency_results = {}
        
        for endpoint in consistency_tests:
            self.log(f"🧪 测试数据一致性: {endpoint}")
            
            responses = []
            for i in range(3):
                try:
                    response = self.session.get(f"{self.config['cloud_server']}{endpoint}", timeout=10)
                    if response.status_code == 200:
                        responses.append(response.json())
                    time.sleep(1)  # 间隔1秒
                except Exception as e:
                    self.log(f"   ❌ 第{i+1}次请求失败: {e}", "ERROR")
            
            if len(responses) >= 2:
                # 检查数据结构是否一致
                first_keys = set(responses[0].keys()) if isinstance(responses[0], dict) else set()
                all_consistent = True
                
                for response in responses[1:]:
                    if isinstance(response, dict):
                        current_keys = set(response.keys())
                        if current_keys != first_keys:
                            all_consistent = False
                            break
                
                if all_consistent:
                    self.log(f"   ✅ {endpoint}: 数据结构一致", "SUCCESS")
                    consistency_results[endpoint] = {'consistent': True}
                else:
                    self.log(f"   ⚠️ {endpoint}: 数据结构不一致", "WARNING")
                    consistency_results[endpoint] = {'consistent': False}
                    self.warnings.append(f"{endpoint}数据结构不一致")
            else:
                self.log(f"   ❌ {endpoint}: 无法获取足够的响应进行比较", "ERROR")
                consistency_results[endpoint] = {'consistent': False, 'error': 'insufficient_responses'}
        
        self.verification_results['data_consistency'] = consistency_results
        return consistency_results
    
    def generate_verification_report(self):
        """生成验证报告"""
        self.log("📋 生成验证报告...", "INFO")
        
        # 统计结果
        total_tests = 0
        passed_tests = 0
        
        # 服务可用性
        if self.verification_results.get('service_availability', {}).get('both_available'):
            passed_tests += 1
        total_tests += 1
        
        # 数据端点
        data_endpoints = self.verification_results.get('data_endpoints', {})
        for endpoint, result in data_endpoints.items():
            total_tests += 1
            if result.get('accessible') and result.get('data_complete', True):
                passed_tests += 1
        
        # 导出功能
        export_functionality = self.verification_results.get('export_functionality', {})
        for export, result in export_functionality.items():
            total_tests += 1
            if result.get('success'):
                passed_tests += 1
        
        # 交易功能
        trading = self.verification_results.get('trading_functionality', {})
        total_tests += 1
        if trading.get('success'):
            passed_tests += 1
        
        # 计算成功率
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        return {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'success_rate': success_rate,
            'critical_failures': self.critical_failures,
            'warnings': self.warnings
        }
    
    def display_final_verification_result(self, report):
        """显示最终验证结果"""
        self.log("🎯 最终验证结果", "SUCCESS")
        self.log("=" * 60, "SUCCESS")
        
        # 总体结果
        success_rate = report['success_rate']
        if success_rate >= 90:
            overall_status = "🏆 优秀"
            status_color = "SUCCESS"
        elif success_rate >= 80:
            overall_status = "✅ 良好"
            status_color = "SUCCESS"
        elif success_rate >= 60:
            overall_status = "⚠️ 一般"
            status_color = "WARNING"
        else:
            overall_status = "❌ 需要改进"
            status_color = "ERROR"
        
        self.log(f"📊 总体评估: {overall_status} ({success_rate:.1f}%)", status_color)
        self.log(f"📈 通过测试: {report['passed_tests']}/{report['total_tests']}", "INFO")
        
        # 关键失败
        if report['critical_failures']:
            self.log("🚨 关键问题:", "CRITICAL")
            for failure in report['critical_failures']:
                self.log(f"   ❌ {failure}", "ERROR")
        else:
            self.log("✅ 无关键问题", "SUCCESS")
        
        # 警告
        if report['warnings']:
            self.log("⚠️ 警告信息:", "WARNING")
            for warning in report['warnings']:
                self.log(f"   ⚠️ {warning}", "WARNING")
        
        # 最终结论
        print()
        if success_rate >= 85 and not report['critical_failures']:
            self.log("🎉 验证通过!云端Agent可以完全获取本地交易数据!", "SUCCESS")
            return True
        elif success_rate >= 70:
            self.log("⚠️ 基本可用,但有一些问题需要解决", "WARNING")
            return False
        else:
            self.log("❌ 验证失败,存在严重问题需要修复", "ERROR")
            return False
    
    def run_comprehensive_verification(self):
        """运行全面验证"""
        self.log("🚀 开始全面验证测试", "INFO")
        self.log("=" * 60, "INFO")
        
        # 1. 验证服务可用性
        if not self.verify_service_availability():
            self.log("🚨 服务不可用,停止验证", "CRITICAL")
            return False
        print()
        
        # 2. 验证数据端点
        self.verify_data_endpoints()
        print()
        
        # 3. 验证导出功能
        self.verify_export_functionality()
        print()
        
        # 4. 验证交易功能
        self.verify_trading_functionality()
        print()
        
        # 5. 验证数据一致性
        self.verify_data_consistency()
        print()
        
        # 6. 生成报告
        report = self.generate_verification_report()
        
        # 7. 显示最终结果
        verification_passed = self.display_final_verification_result(report)
        
        self.log("🎉 全面验证测试完成!", "SUCCESS")
        return verification_passed

if __name__ == "__main__":
    verifier = ComprehensiveVerificationTest()
    success = verifier.run_comprehensive_verification()
    
    # 退出码
    sys.exit(0 if success else 1)
