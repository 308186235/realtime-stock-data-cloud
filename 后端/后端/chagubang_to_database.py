
# 增强数据库错误处理
import logging
from backend.services.unified_error_handler import unified_error_handler, ErrorSeverity, async_error_handler

logger = logging.getLogger(__name__)

@async_error_handler(severity=ErrorSeverity.HIGH)
async def safe_database_operation(func, *args, **kwargs):
    """安全的数据库操作包装器"""
    try:
        return await func(*args, **kwargs)
    except Exception as e:
        logger.error(f"数据库操作异常: {e}")
        # 这里可以添加数据库重连逻辑
        raise

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
茶股帮数据接收并存储到Supabase数据库
"""

import socket
import json
import time
import logging
import threading
from datetime import datetime
from supabase import create_client, Client
import queue

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Supabase配置
SUPABASE_URL = "https://process.env.SUPABASE_URL"
SUPABASE_KEY = "process.env.SUPABASE_ANON_KEY

# 茶股帮配置
CHAGUBANG_HOST = 'l1.chagubang.com'
CHAGUBANG_PORT = 6380
TOKEN = "process.env.STOCK_API_KEY"

class ChaguBangToDatabase:
    def __init__(self):
        self.socket = None
        self.running = False
        self.data_queue = queue.Queue(maxsize=10000)
        self.supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.stats = {
            'received': 0,
            'processed': 0,
            'errors': 0,
            'start_time': time.time()
        }
        
    def connect_to_chagubang(self):
        """连接到茶股帮服务器"""
        try:
            logger.info(f"正在连接茶股帮服务器: {CHAGUBANG_HOST}:{CHAGUBANG_PORT}")
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((CHAGUBANG_HOST, CHAGUBANG_PORT))
            
            # 发送token
            logger.info(f"发送token: {TOKEN}")
            self.socket.send(TOKEN.encode('utf-8'))
            
            logger.info("✅ 成功连接到茶股帮服务器")
            return True
            
        except Exception as e:
            logger.error(f"❌ 连接茶股帮失败: {e}")
            return False
    
    def parse_stock_data(self, data_str):
        """解析股票数据"""
        try:
            # 茶股帮数据格式: symbol,name,price,change,volume,etc...
            parts = data_str.strip().split(',')
            if len(parts) < 4:
                return None
                
            symbol = parts[0].strip()
            name = parts[1].strip() if len(parts) > 1 else ""
            
            try:
                price = float(parts[2]) if len(parts) > 2 and parts[2] else 0.0
            except:
                price = 0.0
                
            try:
                change_percent = float(parts[3]) if len(parts) > 3 and parts[3] else 0.0
            except:
                change_percent = 0.0
                
            try:
                volume = int(parts[4]) if len(parts) > 4 and parts[4] else 0
            except:
                volume = 0
            
            return {
                'symbol': symbol,
                'name': name,
                'price': price,
                'change_percent': change_percent,
                'volume': volume,
                'raw_data': {'original': data_str, 'parts': parts},
                'updated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"解析数据失败: {e}, 原始数据: {data_str}")
            return None
    
    def save_to_database(self, stock_data):
        """保存数据到数据库"""
        try:
            # 使用upsert来插入或更新数据
            result = self.supabase.table('stock_data').upsert(
                stock_data,
                on_conflict='symbol'
            ).execute()
            
            return True
            
        except Exception as e:
            logger.error(f"保存到数据库失败: {e}")
            return False
    
    def database_worker(self):
        """数据库写入工作线程"""
        batch_size = 100
        batch_data = []
        
        while self.running or not self.data_queue.empty():
            try:
                # 获取数据,超时1秒
                try:
                    data = self.data_queue.get(timeout=1)
                    batch_data.append(data)
                except queue.Empty:
                    # 如果队列为空,处理当前批次
                    if batch_data:
                        self.process_batch(batch_data)
                        batch_data = []
                    continue
                
                # 如果批次满了,处理批次
                if len(batch_data) >= batch_size:
                    self.process_batch(batch_data)
                    batch_data = []
                    
            except Exception as e:
                logger.error(f"数据库工作线程错误: {e}")
                
        # 处理剩余数据
        if batch_data:
            self.process_batch(batch_data)
    
    def process_batch(self, batch_data):
        """批量处理数据"""
        try:
            # 批量插入到数据库
            result = self.supabase.table('stock_data').upsert(
                batch_data,
                on_conflict='symbol'
            ).execute()
            
            self.stats['processed'] += len(batch_data)
            logger.info(f"✅ 批量保存 {len(batch_data)} 条数据到数据库")
            
        except Exception as e:
            logger.error(f"批量保存失败: {e}")
            self.stats['errors'] += len(batch_data)
    
    def receive_data(self):
        """接收数据主循环"""
        buffer = ""
        
        while self.running:
            try:
                # 接收数据
                data = self.socket.recv(4096).decode('utf-8', errors='ignore')
                if not data:
                    logger.warning("连接断开,准备重连...")
                    break
                
                buffer += data
                
                # 按行分割数据
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    line = line.strip()
                    
                    if line:
                        self.stats['received'] += 1
                        
                        # 解析股票数据
                        stock_data = self.parse_stock_data(line)
                        if stock_data:
                            # 添加到队列
                            try:
                                self.data_queue.put(stock_data, timeout=0.1)
                            except queue.Full:
                                logger.warning("数据队列已满,丢弃数据")
                        
                        # 每1000条数据打印一次统计
                        if self.stats['received'] % 1000 == 0:
                            self.print_stats()
                            
            except Exception as e:
                logger.error(f"接收数据错误: {e}")
                self.stats['errors'] += 1
                break
    
    def print_stats(self):
        """打印统计信息"""
        elapsed = time.time() - self.stats['start_time']
        rate = self.stats['received'] / elapsed if elapsed > 0 else 0
        
        logger.info(f"📊 统计: 接收{self.stats['received']} 处理{self.stats['processed']} "
                   f"错误{self.stats['errors']} 速率{rate:.1f}/秒 队列{self.data_queue.qsize()}")
    
    def start(self, duration=300):
        """开始接收数据"""
        logger.info(f"🚀 开始茶股帮数据接收,运行{duration}秒...")
        
        if not self.connect_to_chagubang():
            return False
        
        self.running = True
        self.stats['start_time'] = time.time()
        
        # 启动数据库工作线程
        db_thread = threading.Thread(target=self.database_worker)
        db_thread.start()
        
        # 启动数据接收线程
        receive_thread = threading.Thread(target=self.receive_data)
        receive_thread.start()
        
        # 等待指定时间
        time.sleep(duration)
        
        # 停止接收
        self.stop()
        
        # 等待线程结束
        receive_thread.join(timeout=5)
        db_thread.join(timeout=10)
        
        self.print_stats()
        logger.info("✅ 数据接收完成")
        
        return True
    
    def stop(self):
        """停止接收数据"""
        logger.info("正在停止数据接收...")
        self.running = False
        
        if self.socket:
            try:
                self.socket.close()
            except:
                pass

def main():
    """主函数"""
    print("🚀 茶股帮数据接收器 -> Supabase数据库")
    print("=" * 50)
    
    receiver = ChaguBangToDatabase()
    
    try:
        # 运行5分钟
        receiver.start(duration=300)
        
    except KeyboardInterrupt:
        print("\n⏹️  用户中断")
        receiver.stop()
    except Exception as e:
        print(f"❌ 运行错误: {e}")
        receiver.stop()

if __name__ == "__main__":
    main()
