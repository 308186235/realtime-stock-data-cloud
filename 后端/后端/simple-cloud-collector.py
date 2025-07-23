#!/usr/bin/env python3
"""
简单云端数据收集器
连接茶股帮并直接存储到Supabase
"""

import socket
import json
import time
import requests
from datetime import datetime
import threading

# Supabase配置
SUPABASE_CONFIG = {
    'url': 'https://process.env.SUPABASE_URL',
    'anon_key': 'process.env.SUPABASE_ANON_KEY
}

# 茶股帮配置
CHAGUBANG_CONFIG = {
    'host': 'l1.chagubang.com',
    'port': 6380,
    'token': 'process.env.STOCK_API_KEY'
}

class SimpleCloudCollector:
    def __init__(self):
        self.running = False
        self.socket = None
        self.stats = {
            'received': 0,
            'processed': 0,
            'saved': 0,
            'errors': 0,
            'start_time': time.time()
        }
        
    def connect_to_chagubang(self):
        """连接茶股帮"""
        try:
            print(f"🔗 连接茶股帮: {CHAGUBANG_CONFIG['host']}:{CHAGUBANG_CONFIG['port']}")
            
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10)
            self.socket.connect((CHAGUBANG_CONFIG['host'], CHAGUBANG_CONFIG['port']))
            
            # 发送token
            self.socket.send(CHAGUBANG_CONFIG['token'].encode('utf-8'))
            
            print("✅ 茶股帮连接成功")
            return True
            
        except Exception as e:
            print(f"❌ 茶股帮连接失败: {e}")
            return False
    
    def save_to_supabase(self, stock_data):
        """保存数据到Supabase"""
        try:
            headers = {
                'apikey': SUPABASE_CONFIG['anon_key'],
                'Authorization': f"Bearer {SUPABASE_CONFIG['anon_key']}",
                'Content-Type': 'application/json',
                'Prefer': 'return=minimal'
            }
            
            response = requests.post(
                f"{SUPABASE_CONFIG['url']}/rest/v1/stock_quotes",
                headers=headers,
                json=stock_data,
                timeout=5
            )
            
            if response.status_code in [200, 201]:
                self.stats['saved'] += 1
                return True
            else:
                print(f"❌ Supabase保存失败: {response.status_code} - {response.text}")
                self.stats['errors'] += 1
                return False
                
        except Exception as e:
            print(f"❌ Supabase保存错误: {e}")
            self.stats['errors'] += 1
            return False
    
    def parse_stock_data(self, line):
        """解析股票数据"""
        try:
            parts = line.split('|')
            
            if len(parts) >= 10:
                return {
                    'symbol': parts[0],
                    'name': parts[1] or '',
                    'price': float(parts[2]) if parts[2] else 0,
                    'change_percent': float(parts[3]) if parts[3] else 0,
                    'volume': int(parts[4]) if parts[4] else 0,
                    'amount': float(parts[5]) if parts[5] else 0,
                    'high': float(parts[6]) if parts[6] else 0,
                    'low': float(parts[7]) if parts[7] else 0,
                    'open': float(parts[8]) if parts[8] else 0,
                    'prev_close': float(parts[9]) if parts[9] else 0,
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat()
                }
        except Exception as e:
            print(f"❌ 解析数据失败: {e}")
        
        return None
    
    def data_collection_loop(self):
        """数据收集循环"""
        buffer = ""
        
        while self.running:
            try:
                data = self.socket.recv(4096).decode('utf-8', errors='ignore')
                if not data:
                    print("⚠️ 连接断开")
                    break
                
                buffer += data
                self.stats['received'] += 1
                
                # 处理完整的行
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    line = line.strip()
                    
                    if line:
                        stock_data = self.parse_stock_data(line)
                        if stock_data:
                            self.stats['processed'] += 1
                            
                            # 保存到Supabase
                            self.save_to_supabase(stock_data)
                        
                        # 每100条数据打印统计
                        if self.stats['processed'] % 100 == 0:
                            self.print_stats()
                            
            except Exception as e:
                print(f"❌ 数据接收错误: {e}")
                break
    
    def print_stats(self):
        """打印统计信息"""
        uptime = time.time() - self.stats['start_time']
        rate = self.stats['received'] / uptime if uptime > 0 else 0
        
        print(f"📊 统计: 接收{self.stats['received']} 处理{self.stats['processed']} "
              f"保存{self.stats['saved']} 错误{self.stats['errors']} "
              f"速率{rate:.1f}/秒 运行{uptime:.0f}秒")
    
    def start(self):
        """启动收集器"""
        print("🚀 启动简单云端数据收集器...")
        
        if not self.connect_to_chagubang():
            return False
        
        self.running = True
        
        # 启动数据收集线程
        collection_thread = threading.Thread(target=self.data_collection_loop)
        collection_thread.start()
        
        print("✅ 数据收集器启动成功")
        print("📡 开始接收茶股帮数据并存储到Supabase...")
        
        try:
            # 主线程保持运行
            while self.running:
                time.sleep(10)
                self.print_stats()
                
        except KeyboardInterrupt:
            print("\n⏹️ 收到停止信号")
        finally:
            self.stop()
            collection_thread.join(timeout=5)
    
    def stop(self):
        """停止收集器"""
        print("⏹️ 停止数据收集器...")
        self.running = False
        
        if self.socket:
            self.socket.close()
        
        self.print_stats()
        print("✅ 数据收集器已停止")

def main():
    """主函数"""
    collector = SimpleCloudCollector()
    
    try:
        collector.start()
    except Exception as e:
        print(f"❌ 启动失败: {e}")

if __name__ == "__main__":
    main()
