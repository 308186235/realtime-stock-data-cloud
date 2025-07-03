#!/usr/bin/env python3
"""
开盘时间4000+股票推送监控器
专门监控和处理开盘时间的大量股票数据推送
"""

import asyncio
import time
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import logging
import requests
from typing import Dict, List, Any

# 配置
SUPABASE_URL = 'https://zzukfxwavknskqcepsjb.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp6dWtmeHdhdmtuc2txY2Vwc2piIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEyOTg1MDYsImV4cCI6MjA2Njg3NDUwNn0.AMGkJSre3QtRBQK_Lh2Iga4dUzSPvuO1G9s6fF2QPaw'

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OpeningTimeMonitor:
    def __init__(self):
        self.data_dir = Path('stock_data')
        self.monitoring = False
        self.stats = {
            'monitoring_start': None,
            'total_files_detected': 0,
            'total_stocks_processed': 0,
            'database_writes': 0,
            'errors': 0,
            'peak_files_per_minute': 0,
            'peak_stocks_per_minute': 0
        }
        
        # 开盘时间配置
        self.market_open_times = {
            'morning_open': '09:30',
            'morning_close': '11:30',
            'afternoon_open': '13:00',
            'afternoon_close': '15:00'
        }
        
    def is_market_open(self) -> bool:
        """检查是否在开盘时间"""
        now = datetime.now()
        current_time = now.strftime('%H:%M')
        
        # 检查是否在交易时间内
        morning_open = self.market_open_times['morning_open']
        morning_close = self.market_open_times['morning_close']
        afternoon_open = self.market_open_times['afternoon_open']
        afternoon_close = self.market_open_times['afternoon_close']
        
        is_morning_session = morning_open <= current_time <= morning_close
        is_afternoon_session = afternoon_open <= current_time <= afternoon_close
        
        return is_morning_session or is_afternoon_session
    
    def is_opening_time(self) -> bool:
        """检查是否是开盘时间（前5分钟）"""
        now = datetime.now()
        current_time = now.strftime('%H:%M')
        
        # 开盘前5分钟到开盘后5分钟
        opening_times = ['09:25', '09:35', '12:55', '13:05']
        
        for open_time in opening_times:
            open_dt = datetime.strptime(open_time, '%H:%M').replace(
                year=now.year, month=now.month, day=now.day
            )
            time_diff = abs((now - open_dt).total_seconds())
            
            if time_diff <= 300:  # 5分钟内
                return True
        
        return False
    
    async def start_monitoring(self):
        """开始监控"""
        logger.info("🔍 开始监控开盘时间股票推送...")
        self.monitoring = True
        self.stats['monitoring_start'] = time.time()
        
        try:
            while self.monitoring:
                current_time = datetime.now().strftime('%H:%M:%S')
                
                if self.is_opening_time():
                    logger.info(f"🚨 检测到开盘时间 {current_time} - 启动高频监控")
                    await self.high_frequency_monitoring()
                elif self.is_market_open():
                    logger.info(f"📊 交易时间 {current_time} - 正常监控")
                    await self.normal_monitoring()
                else:
                    logger.info(f"😴 非交易时间 {current_time} - 低频监控")
                    await self.low_frequency_monitoring()
                
                # 短暂休息
                await asyncio.sleep(10)
                
        except KeyboardInterrupt:
            logger.info("⏹️ 监控被用户中断")
        except Exception as e:
            logger.error(f"❌ 监控异常: {e}")
        finally:
            self.monitoring = False
            await self.generate_monitoring_report()
    
    async def high_frequency_monitoring(self):
        """高频监控（开盘时间）"""
        logger.info("🚀 启动高频监控模式...")
        
        start_time = time.time()
        files_detected = 0
        stocks_processed = 0
        
        # 连续监控5分钟
        while time.time() - start_time < 300:  # 5分钟
            # 检查新文件
            new_files = await self.detect_new_files()
            
            if new_files:
                files_detected += len(new_files)
                logger.info(f"📄 检测到 {len(new_files)} 个新文件")
                
                # 立即处理
                processed = await self.process_files_immediately(new_files)
                stocks_processed += processed
                
                # 更新统计
                self.stats['total_files_detected'] += len(new_files)
                self.stats['total_stocks_processed'] += processed
            
            # 高频检查（每秒）
            await asyncio.sleep(1)
        
        # 更新峰值统计
        files_per_minute = files_detected / 5
        stocks_per_minute = stocks_processed / 5
        
        if files_per_minute > self.stats['peak_files_per_minute']:
            self.stats['peak_files_per_minute'] = files_per_minute
        
        if stocks_per_minute > self.stats['peak_stocks_per_minute']:
            self.stats['peak_stocks_per_minute'] = stocks_per_minute
        
        logger.info(f"📊 高频监控完成: {files_detected} 文件, {stocks_processed} 股票")
    
    async def normal_monitoring(self):
        """正常监控（交易时间）"""
        # 每30秒检查一次
        new_files = await self.detect_new_files()
        
        if new_files:
            logger.info(f"📄 检测到 {len(new_files)} 个新文件")
            processed = await self.process_files_immediately(new_files)
            
            self.stats['total_files_detected'] += len(new_files)
            self.stats['total_stocks_processed'] += processed
        
        await asyncio.sleep(30)
    
    async def low_frequency_monitoring(self):
        """低频监控（非交易时间）"""
        # 每5分钟检查一次
        new_files = await self.detect_new_files()
        
        if new_files:
            logger.info(f"📄 非交易时间检测到 {len(new_files)} 个文件")
            # 非交易时间可以延迟处理
            await asyncio.sleep(60)  # 等待1分钟再处理
            
            processed = await self.process_files_immediately(new_files)
            self.stats['total_files_detected'] += len(new_files)
            self.stats['total_stocks_processed'] += processed
        
        await asyncio.sleep(300)  # 5分钟
    
    async def detect_new_files(self) -> List[Path]:
        """检测新文件"""
        try:
            if not self.data_dir.exists():
                return []
            
            # 获取最近1分钟内的文件
            cutoff_time = time.time() - 60
            new_files = []
            
            for file_path in self.data_dir.iterdir():
                if file_path.is_file() and file_path.suffix in ['.dat', '.pkl']:
                    if file_path.stat().st_mtime > cutoff_time:
                        new_files.append(file_path)
            
            return new_files
            
        except Exception as e:
            logger.error(f"❌ 检测新文件失败: {e}")
            return []
    
    async def process_files_immediately(self, files: List[Path]) -> int:
        """立即处理文件"""
        total_processed = 0
        
        try:
            # 导入大量股票处理器
            from mass_stock_database_processor import MassStockDatabaseProcessor
            
            processor = MassStockDatabaseProcessor()
            
            for file_path in files:
                try:
                    # 读取文件数据
                    stock_data_list = await processor.read_file_data(file_path)
                    
                    if stock_data_list:
                        # 批量处理
                        await processor.process_stock_batch(stock_data_list, file_path.name)
                        total_processed += len(stock_data_list)
                        
                        logger.info(f"✅ 处理完成: {file_path.name} ({len(stock_data_list)} 股票)")
                    
                except Exception as e:
                    logger.error(f"❌ 处理文件失败 {file_path.name}: {e}")
                    self.stats['errors'] += 1
            
            return total_processed
            
        except Exception as e:
            logger.error(f"❌ 立即处理失败: {e}")
            self.stats['errors'] += 1
            return 0
    
    async def check_database_status(self):
        """检查数据库状态"""
        try:
            headers = {
                'Authorization': f'Bearer {SUPABASE_KEY}',
                'apikey': SUPABASE_KEY
            }
            
            # 检查最近的数据写入
            response = requests.get(
                f'{SUPABASE_URL}/rest/v1/system_config?key=like.mass_stock_%&order=key.desc&limit=10',
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                recent_data = response.json()
                logger.info(f"📊 数据库状态正常，最近有 {len(recent_data)} 条记录")
                return True
            else:
                logger.warning(f"⚠️ 数据库查询异常: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 数据库状态检查失败: {e}")
            return False
    
    async def generate_monitoring_report(self):
        """生成监控报告"""
        duration = time.time() - self.stats['monitoring_start']
        
        report = f"""
🔍 开盘时间股票推送监控报告
{'=' * 50}

⏱️ 监控时长: {duration / 3600:.2f} 小时

📊 监控统计:
  - 检测到文件总数: {self.stats['total_files_detected']}
  - 处理股票总数: {self.stats['total_stocks_processed']}
  - 数据库写入次数: {self.stats['database_writes']}
  - 错误次数: {self.stats['errors']}

🚀 峰值性能:
  - 峰值文件/分钟: {self.stats['peak_files_per_minute']:.2f}
  - 峰值股票/分钟: {self.stats['peak_stocks_per_minute']:.2f}

📈 平均性能:
  - 平均文件/小时: {self.stats['total_files_detected'] / (duration / 3600):.2f}
  - 平均股票/小时: {self.stats['total_stocks_processed'] / (duration / 3600):.2f}

🎯 系统状态:
  - 监控模式: 开盘时间高频 + 交易时间正常 + 非交易时间低频
  - 数据存储: Supabase system_config表
  - 处理策略: 实时检测 + 立即处理

{'=' * 50}
"""
        
        logger.info(report)
        
        # 保存报告
        report_file = f'opening_time_monitoring_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info(f"📄 监控报告已保存: {report_file}")
    
    def stop_monitoring(self):
        """停止监控"""
        self.monitoring = False
        logger.info("⏹️ 监控已停止")

async def main():
    """主函数"""
    monitor = OpeningTimeMonitor()
    
    logger.info("🚀 启动开盘时间股票推送监控器...")
    
    try:
        # 检查数据库连接
        db_ok = await monitor.check_database_status()
        if not db_ok:
            logger.warning("⚠️ 数据库连接异常，但继续监控")
        
        # 开始监控
        await monitor.start_monitoring()
        
    except KeyboardInterrupt:
        logger.info("👋 监控被用户中断")
    except Exception as e:
        logger.error(f"❌ 监控异常: {e}")
    finally:
        monitor.stop_monitoring()

if __name__ == '__main__':
    asyncio.run(main())
