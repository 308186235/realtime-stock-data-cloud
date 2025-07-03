"""
茶股帮深度诊断工具
基于MCP分析，深入诊断Token鉴权失败的原因
"""

import socket
import struct
import time
import json
from datetime import datetime
import hashlib

class ChaguBangDeepDiagnosis:
    """茶股帮深度诊断器"""
    
    def __init__(self, host='l1.chagubang.com', port=6380):
        self.host = host
        self.port = port
        self.diagnosis_results = {}
    
    def run_complete_diagnosis(self, token):
        """运行完整诊断"""
        print("🔍 茶股帮深度诊断开始")
        print("=" * 60)
        print(f"目标服务器: {self.host}:{self.port}")
        print(f"Token: {token}")
        print(f"诊断时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # 诊断步骤
        tests = [
            ("网络连接测试", self._test_network_connection),
            ("基础TCP连接", self._test_basic_tcp_connection),
            ("Token格式测试", lambda: self._test_token_formats(token)),
            ("协议握手分析", lambda: self._test_protocol_handshake(token)),
            ("服务器响应分析", lambda: self._analyze_server_response(token)),
            ("时间窗口测试", lambda: self._test_time_window(token)),
            ("数据推送检测", lambda: self._test_data_push(token))
        ]
        
        for test_name, test_func in tests:
            print(f"\n🔍 {test_name}")
            print("-" * 40)
            try:
                result = test_func()
                self.diagnosis_results[test_name] = result
                if result.get('success'):
                    print(f"✅ {result.get('message', '测试通过')}")
                else:
                    print(f"❌ {result.get('message', '测试失败')}")
                    if result.get('details'):
                        for detail in result['details']:
                            print(f"   • {detail}")
            except Exception as e:
                print(f"❌ 测试异常: {e}")
                self.diagnosis_results[test_name] = {'success': False, 'error': str(e)}
        
        # 生成诊断报告
        self._generate_diagnosis_report()
    
    def _test_network_connection(self):
        """测试网络连接"""
        try:
            import subprocess
            result = subprocess.run(['ping', '-n', '1', self.host], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                return {
                    'success': True,
                    'message': f'网络连接正常，可以ping通 {self.host}',
                    'ping_result': result.stdout
                }
            else:
                return {
                    'success': False,
                    'message': f'无法ping通 {self.host}',
                    'details': ['检查网络连接', '确认域名解析正常', '检查防火墙设置']
                }
        except Exception as e:
            return {
                'success': False,
                'message': f'网络测试失败: {e}',
                'details': ['网络连接可能有问题']
            }
    
    def _test_basic_tcp_connection(self):
        """测试基础TCP连接"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            
            start_time = time.time()
            sock.connect((self.host, self.port))
            connect_time = time.time() - start_time
            
            sock.close()
            
            return {
                'success': True,
                'message': f'TCP连接成功，耗时 {connect_time:.3f} 秒',
                'connect_time': connect_time
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'TCP连接失败: {e}',
                'details': [
                    '检查服务器是否在线',
                    '确认端口6380是否开放',
                    '检查防火墙是否阻止连接'
                ]
            }
    
    def _test_token_formats(self, token):
        """测试不同Token格式"""
        formats_to_test = [
            ('原始Token', token),
            ('带Bearer前缀', f'Bearer {token}'),
            ('带Token前缀', f'Token {token}'),
            ('JSON格式', json.dumps({'token': token})),
            ('Key-Value格式', f'key={token}'),
            ('API Key格式', f'api_key={token}'),
            ('Authorization格式', f'Authorization: {token}')
        ]
        
        results = []
        for format_name, format_token in formats_to_test:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                sock.connect((self.host, self.port))
                
                # 发送格式化的token
                sock.sendall(format_token.encode('utf-8'))
                
                # 尝试接收响应
                try:
                    sock.settimeout(3)
                    response = sock.recv(1024)
                    if response:
                        response_text = response.decode('utf-8', errors='ignore')
                        results.append(f"{format_name}: 收到响应 '{response_text[:50]}'")
                    else:
                        results.append(f"{format_name}: 无响应")
                except socket.timeout:
                    results.append(f"{format_name}: 响应超时")
                
                sock.close()
                
            except Exception as e:
                results.append(f"{format_name}: 连接失败 - {e}")
        
        return {
            'success': True,
            'message': f'测试了 {len(formats_to_test)} 种Token格式',
            'details': results
        }
    
    def _test_protocol_handshake(self, token):
        """测试协议握手"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect((self.host, self.port))
            
            # 发送token
            sock.sendall(token.encode('utf-8'))
            
            # 等待并分析响应
            responses = []
            sock.settimeout(5)
            
            try:
                # 尝试接收多次响应
                for i in range(3):
                    response = sock.recv(1024)
                    if response:
                        responses.append({
                            'sequence': i + 1,
                            'length': len(response),
                            'content': response.decode('utf-8', errors='ignore'),
                            'hex': response.hex()[:100]
                        })
                    else:
                        break
            except socket.timeout:
                pass
            
            sock.close()
            
            if responses:
                return {
                    'success': True,
                    'message': f'收到 {len(responses)} 个响应',
                    'responses': responses
                }
            else:
                return {
                    'success': False,
                    'message': '未收到任何响应',
                    'details': ['服务器可能不支持该Token', '可能需要特殊的握手流程']
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'协议握手测试失败: {e}'
            }
    
    def _analyze_server_response(self, token):
        """分析服务器响应"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect((self.host, self.port))
            
            # 发送token
            sock.sendall(token.encode('utf-8'))
            
            # 详细分析响应
            sock.settimeout(5)
            response = sock.recv(1024)
            
            if response:
                analysis = {
                    'raw_length': len(response),
                    'raw_hex': response.hex(),
                    'decoded_text': response.decode('utf-8', errors='ignore'),
                    'is_json': False,
                    'contains_error': False,
                    'contains_success': False
                }
                
                # 检查是否是JSON
                try:
                    json.loads(analysis['decoded_text'])
                    analysis['is_json'] = True
                except:
                    pass
                
                # 检查关键词
                text_lower = analysis['decoded_text'].lower()
                if any(word in text_lower for word in ['error', '错误', '失败', 'fail']):
                    analysis['contains_error'] = True
                
                if any(word in text_lower for word in ['success', '成功', 'ok']):
                    analysis['contains_success'] = True
                
                # 特殊分析：Token鉴权失败
                if 'token' in text_lower and ('失败' in analysis['decoded_text'] or 'fail' in text_lower):
                    analysis['auth_failure'] = True
                    analysis['failure_reason'] = 'Token认证被服务器拒绝'
                
                sock.close()
                
                return {
                    'success': True,
                    'message': '成功分析服务器响应',
                    'analysis': analysis
                }
            else:
                return {
                    'success': False,
                    'message': '服务器无响应'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'响应分析失败: {e}'
            }
    
    def _test_time_window(self, token):
        """测试时间窗口"""
        current_time = datetime.now()
        hour = current_time.hour
        minute = current_time.minute
        
        # A股交易时间
        trading_sessions = [
            (9, 30, 11, 30),   # 上午
            (13, 0, 15, 0)     # 下午
        ]
        
        is_trading_time = False
        for start_h, start_m, end_h, end_m in trading_sessions:
            start_minutes = start_h * 60 + start_m
            end_minutes = end_h * 60 + end_m
            current_minutes = hour * 60 + minute
            
            if start_minutes <= current_minutes <= end_minutes:
                is_trading_time = True
                break
        
        return {
            'success': True,
            'message': f'当前时间: {current_time.strftime("%H:%M")}',
            'details': [
                f'是否交易时间: {"是" if is_trading_time else "否"}',
                '交易时间: 9:30-11:30, 13:00-15:00',
                '建议在交易时间内测试数据推送'
            ],
            'is_trading_time': is_trading_time
        }
    
    def _test_data_push(self, token):
        """测试数据推送"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect((self.host, self.port))
            
            # 发送token
            sock.sendall(token.encode('utf-8'))
            
            # 等待数据推送（长时间等待）
            sock.settimeout(30)  # 30秒等待
            
            data_received = []
            start_time = time.time()
            
            try:
                while time.time() - start_time < 30:
                    # 尝试按照长度前缀协议接收
                    raw_msglen = sock.recv(4)
                    if not raw_msglen:
                        break
                    
                    if len(raw_msglen) == 4:
                        msglen = struct.unpack('<I', raw_msglen)[0]
                        if 0 < msglen < 1024 * 1024:  # 合理的消息长度
                            message = sock.recv(msglen)
                            if message:
                                data_received.append({
                                    'length': msglen,
                                    'content': message.decode('utf-8', errors='ignore')[:100],
                                    'timestamp': time.time() - start_time
                                })
                                
                                if len(data_received) >= 5:  # 收到5条数据就够了
                                    break
            except socket.timeout:
                pass
            
            sock.close()
            
            if data_received:
                return {
                    'success': True,
                    'message': f'收到 {len(data_received)} 条数据推送',
                    'data_samples': data_received
                }
            else:
                return {
                    'success': False,
                    'message': '30秒内未收到数据推送',
                    'details': [
                        'Token可能无效或已过期',
                        '可能不在数据推送时间',
                        '服务器可能暂停推送'
                    ]
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'数据推送测试失败: {e}'
            }
    
    def _generate_diagnosis_report(self):
        """生成诊断报告"""
        print("\n" + "=" * 60)
        print("🎯 茶股帮深度诊断报告")
        print("=" * 60)
        
        # 统计结果
        total_tests = len(self.diagnosis_results)
        passed_tests = sum(1 for r in self.diagnosis_results.values() if r.get('success'))
        
        print(f"📊 测试总览: {passed_tests}/{total_tests} 项通过")
        print()
        
        # 关键发现
        print("🔍 关键发现:")
        
        # 网络连接
        if self.diagnosis_results.get('网络连接测试', {}).get('success'):
            print("✅ 网络连接正常")
        else:
            print("❌ 网络连接有问题")
        
        # TCP连接
        if self.diagnosis_results.get('基础TCP连接', {}).get('success'):
            print("✅ TCP连接正常")
        else:
            print("❌ TCP连接失败")
        
        # 服务器响应
        response_analysis = self.diagnosis_results.get('服务器响应分析', {})
        if response_analysis.get('success'):
            analysis = response_analysis.get('analysis', {})
            if analysis.get('auth_failure'):
                print("❌ Token认证被服务器明确拒绝")
                print("   原因: Token无效、过期或权限不足")
            elif analysis.get('contains_error'):
                print("❌ 服务器返回错误信息")
            else:
                print("✅ 服务器有响应，但可能需要进一步分析")
        
        # 时间窗口
        time_test = self.diagnosis_results.get('时间窗口测试', {})
        if time_test.get('is_trading_time'):
            print("✅ 当前在交易时间内")
        else:
            print("⚠️ 当前不在交易时间内")
        
        # 数据推送
        if self.diagnosis_results.get('数据推送检测', {}).get('success'):
            print("✅ 收到数据推送")
        else:
            print("❌ 未收到数据推送")
        
        print()
        print("💡 建议解决方案:")
        
        # 根据诊断结果给出建议
        if not self.diagnosis_results.get('网络连接测试', {}).get('success'):
            print("1. 检查网络连接和DNS解析")
        elif not self.diagnosis_results.get('基础TCP连接', {}).get('success'):
            print("1. 检查防火墙和端口设置")
        elif response_analysis.get('analysis', {}).get('auth_failure'):
            print("1. 联系茶股帮卖家确认Token状态")
            print("2. 检查Token是否需要续费")
            print("3. 确认Token格式是否正确")
        elif not time_test.get('is_trading_time'):
            print("1. 在交易时间内重新测试 (9:30-11:30, 13:00-15:00)")
        else:
            print("1. Token可能需要特殊激活步骤")
            print("2. 联系卖家确认服务状态")
        
        print("\n📞 联系卖家时提供以下信息:")
        print(f"- Token: {self.diagnosis_results.get('token', 'N/A')}")
        print(f"- 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"- 连接状态: {'成功' if self.diagnosis_results.get('基础TCP连接', {}).get('success') else '失败'}")
        print(f"- 服务器响应: {response_analysis.get('analysis', {}).get('decoded_text', '无响应')[:50]}")


def main():
    """主函数"""
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python chagubang_deep_diagnosis.py <token>")
        return
    
    token = sys.argv[1]
    
    diagnosis = ChaguBangDeepDiagnosis()
    diagnosis.run_complete_diagnosis(token)


if __name__ == "__main__":
    main()
