# 文件操作最佳实践:
# 1. 始终使用 with 语句打开文件
# 2. 避免在循环中重复打开同一文件
# 3. 大文件处理时考虑分块读取
# 4. 异常情况下确保文件正确关闭

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cloudflare Zero Trust 连接监控和自动重连系统
专为移动热点网络环境优化
"""

import os
import sys
import time
import json
import logging
import requests
import subprocess
import threading
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import socket
import ping3

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('zero_trust_monitor.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class ZeroTrustConnectionMonitor:
    """Zero Trust连接监控器"""
    
    def __init__(self):
        self.config = self._load_config()
        self.is_running = False
        self.last_check_time = datetime.now()
        self.connection_stats = {
            'total_checks': 0,
            'failed_checks': 0,
            'reconnections': 0,
            'uptime_start': datetime.now(),
            'last_successful_check': datetime.now()
        }
        
        # 监控目标
        self.monitor_targets = [
            {'name': 'Main API', 'url': 'https://api.aigupiao.me/health', 'timeout': 10},
            {'name': 'Trading API', 'url': 'https://trading.aigupiao.me/health', 'timeout': 15},
            {'name': 'Agent Backend', 'url': 'https://agent.aigupiao.me/health', 'timeout': 10},
            {'name': 'Local API', 'url': 'http://127.0.0.1:8000/health', 'timeout': 5},
            {'name': 'Trading Local', 'url': 'http://127.0.0.1:8888/health', 'timeout': 5},
            {'name': 'Agent Local', 'url': 'http://127.0.0.1:9999/health', 'timeout': 5}
        ]
        
        # 网络质量监控
        self.network_quality = {
            'ping_times': [],
            'packet_loss': 0.0,
            'bandwidth_test': None,
            'connection_type': 'unknown'
        }
        
    def _load_config(self) -> Dict:
        """加载配置"""
        default_config = {
            'check_interval': 30,  # 检查间隔(秒)
            'failure_threshold': 3,  # 失败阈值
            'reconnect_delay': 10,  # 重连延迟(秒)
            'max_reconnect_attempts': 5,  # 最大重连尝试次数
            'cloudflared_path': 'cloudflared.exe',
            'config_file': 'config.yml',
            'tunnel_name': 'aigupiao-tunnel',
            'mobile_optimization': True,
            'network_quality_check': True,
            'auto_restart_services': True
        }
        
        try:
            if os.path.exists('zero_trust_config.json'):
                with open('zero_trust_config.json', 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
        except Exception as e:
            logger.warning(f"加载配置文件失败,使用默认配置: {e}")
            
        return default_config
    
    def check_network_quality(self) -> Dict:
        """检查网络质量"""
        quality_info = {
            'ping_avg': None,
            'ping_loss': 0.0,
            'connection_stable': True,
            'bandwidth_estimate': None
        }
        
        try:
            # Ping测试
            ping_targets = ['1.1.1.1', '8.8.8.8', 'api.aigupiao.me']
            ping_results = []
            
            for target in ping_targets:
                try:
                    ping_time = ping3.ping(target, timeout=5)
                    if ping_time is not None:
                        ping_results.append(ping_time * 1000)  # 转换为毫秒
                except Exception:
                    ping_results.append(None)
            
            # 计算平均延迟
            valid_pings = [p for p in ping_results if p is not None]
            if valid_pings:
                quality_info['ping_avg'] = sum(valid_pings) / len(valid_pings)
                quality_info['ping_loss'] = (len(ping_results) - len(valid_pings)) / len(ping_results) * 100
            
            # 判断连接稳定性
            if quality_info['ping_avg'] and quality_info['ping_avg'] > 1000:  # 延迟超过1秒
                quality_info['connection_stable'] = False
            if quality_info['ping_loss'] > 20:  # 丢包率超过20%
                quality_info['connection_stable'] = False
                
        except Exception as e:
            logger.error(f"网络质量检查失败: {e}")
            quality_info['connection_stable'] = False
            
        return quality_info
    
    def check_cloudflared_process(self) -> bool:
        """检查cloudflared进程是否运行"""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                if 'cloudflared' in proc.info['name'].lower():
                    return True
            return False
        except Exception as e:
            logger.error(f"检查cloudflared进程失败: {e}")
            return False
    
    def check_tunnel_connectivity(self) -> Tuple[bool, List[Dict]]:
        """检查隧道连接性"""
        results = []
        all_success = True
        
        for target in self.monitor_targets:
            result = {
                'name': target['name'],
                'url': target['url'],
                'success': False,
                'response_time': None,
                'error': None
            }
            
            try:
                start_time = time.time()
                response = requests.get(
                    target['url'], 
                    timeout=target['timeout'],
                    headers={'User-Agent': 'ZeroTrust-Monitor/1.0'}
                )
                end_time = time.time()
                
                result['response_time'] = (end_time - start_time) * 1000  # 毫秒
                result['success'] = response.status_code == 200
                
                if not result['success']:
                    result['error'] = f"HTTP {response.status_code}"
                    
            except requests.exceptions.Timeout:
                result['error'] = "请求超时"
                all_success = False
            except requests.exceptions.ConnectionError:
                result['error'] = "连接错误"
                all_success = False
            except Exception as e:
                result['error'] = str(e)
                all_success = False
            
            results.append(result)
            
            if not result['success']:
                all_success = False
        
        return all_success, results
    
    def restart_cloudflared(self) -> bool:
        """重启cloudflared服务"""
        logger.info("🔄 重启cloudflared服务...")
        
        try:
            # 停止现有进程
            logger.info("停止现有cloudflared进程...")
            subprocess.run(['taskkill', '/f', '/im', 'cloudflared.exe'], 
                         capture_output=True, timeout=10)
            time.sleep(3)
            
            # 启动新进程
            logger.info("启动新的cloudflared进程...")
            cmd = [
                self.config['cloudflared_path'],
                'tunnel',
                '--config', self.config['config_file'],
                'run'
            ]
            
            # 在后台启动
            subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
            )
            
            # 等待服务启动
            time.sleep(10)
            
            # 验证启动成功
            if self.check_cloudflared_process():
                logger.info("✅ cloudflared服务重启成功")
                return True
            else:
                logger.error("❌ cloudflared服务重启失败")
                return False
                
        except Exception as e:
            logger.error(f"重启cloudflared失败: {e}")
            return False
    
    def handle_connection_failure(self, failure_count: int) -> bool:
        """处理连接失败"""
        logger.warning(f"⚠️ 连接失败 {failure_count} 次")
        
        # 检查网络质量
        if self.config['network_quality_check']:
            quality = self.check_network_quality()
            logger.info(f"网络质量: 延迟={quality.get('ping_avg', 'N/A')}ms, "
                       f"丢包率={quality.get('ping_loss', 'N/A')}%, "
                       f"稳定={quality.get('connection_stable', False)}")
            
            # 如果网络质量很差,等待更长时间
            if not quality.get('connection_stable', False):
                logger.info("网络质量较差,延长等待时间...")
                time.sleep(30)
        
        # 达到失败阈值,尝试重连
        if failure_count >= self.config['failure_threshold']:
            logger.warning("🚨 达到失败阈值,开始重连流程...")
            
            # 重启cloudflared
            if self.restart_cloudflared():
                self.connection_stats['reconnections'] += 1
                logger.info("✅ 重连成功")
                return True
            else:
                logger.error("❌ 重连失败")
                return False
        
        return False
    
    def generate_status_report(self) -> Dict:
        """生成状态报告"""
        uptime = datetime.now() - self.connection_stats['uptime_start']
        
        return {
            'timestamp': datetime.now().isoformat(),
            'uptime_hours': uptime.total_seconds() / 3600,
            'total_checks': self.connection_stats['total_checks'],
            'failed_checks': self.connection_stats['failed_checks'],
            'success_rate': (1 - self.connection_stats['failed_checks'] / max(1, self.connection_stats['total_checks'])) * 100,
            'reconnections': self.connection_stats['reconnections'],
            'last_successful_check': self.connection_stats['last_successful_check'].isoformat(),
            'cloudflared_running': self.check_cloudflared_process(),
            'network_quality': self.network_quality
        }
    
    def run_monitoring_loop(self):
        """运行监控循环"""
        logger.info("🚀 启动Zero Trust连接监控...")
        logger.info(f"检查间隔: {self.config['check_interval']}秒")
        logger.info(f"失败阈值: {self.config['failure_threshold']}次")
        
        self.is_running = True
        failure_count = 0
        
        while self.is_running:
            try:
                self.connection_stats['total_checks'] += 1
                
                # 检查连接性
                success, results = self.check_tunnel_connectivity()
                
                if success:
                    if failure_count > 0:
                        logger.info("✅ 连接恢复正常")
                    failure_count = 0
                    self.connection_stats['last_successful_check'] = datetime.now()
                else:
                    failure_count += 1
                    self.connection_stats['failed_checks'] += 1
                    
                    # 记录失败详情
                    failed_targets = [r for r in results if not r['success']]
                    logger.warning(f"连接检查失败: {len(failed_targets)}/{len(results)} 个目标失败")
                    
                    for failed in failed_targets:
                        logger.warning(f"  - {failed['name']}: {failed['error']}")
                    
                    # 处理连接失败
                    self.handle_connection_failure(failure_count)
                
                # 每小时生成一次状态报告
                if self.connection_stats['total_checks'] % (3600 // self.config['check_interval']) == 0:
                    report = self.generate_status_report()
                    logger.info(f"📊 状态报告: 成功率={report['success_rate']:.1f}%, "
                               f"运行时间={report['uptime_hours']:.1f}小时, "
                               f"重连次数={report['reconnections']}")
                
                # 等待下次检查
                time.sleep(self.config['check_interval'])
                
            except KeyboardInterrupt:
                logger.info("收到停止信号,正在退出...")
                break
            except Exception as e:
                logger.error(f"监控循环异常: {e}")
                time.sleep(10)  # 异常后短暂等待
        
        self.is_running = False
        logger.info("🛑 监控已停止")
    
    def start(self):
        """启动监控"""
        if self.is_running:
            logger.warning("监控已在运行中")
            return
        
        # 启动监控线程
        monitor_thread = threading.Thread(target=self.run_monitoring_loop)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        return monitor_thread
    
    def stop(self):
        """停止监控"""
        self.is_running = False

def main():
    """主函数"""
    monitor = ZeroTrustConnectionMonitor()
    
    try:
        monitor.run_monitoring_loop()
    except KeyboardInterrupt:
        logger.info("程序被用户中断")
    except Exception as e:
        logger.error(f"程序异常退出: {e}")
    finally:
        monitor.stop()

if __name__ == "__main__":
    main()
