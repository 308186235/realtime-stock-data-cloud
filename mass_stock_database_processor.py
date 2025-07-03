#!/usr/bin/env python3
"""
4000+股票推送数据库处理器
专门处理开盘时间大量股票数据推送到数据库的高性能系统
"""

import asyncio
import aiohttp
import json
import os
import time
import pickle
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any
import logging
from concurrent.futures import ThreadPoolExecutor
import queue
import threading

# 配置
SUPABASE_URL = 'https://zzukfxwavknskqcepsjb.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp6dWtmeHdhdmtuc2txY2Vwc2piIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEyOTg1MDYsImV4cCI6MjA2Njg3NDUwNn0.AMGkJSre3QtRBQK_Lh2Iga4dUzSPvuO1G9s6fF2QPaw'

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MassStockDatabaseProcessor:
    def __init__(self):
        self.data_dir = Path('stock_data')
        self.batch_size = 500  # 每批处理500只股票
        self.max_concurrent = 10  # 最大并发数
        self.processed_count = 0
        self.error_count = 0
        self.start_time = None
        
        # 性能统计
        self.stats = {
            'total_files': 0,
            'processed_files': 0,
            'total_stocks': 0,
            'processed_stocks': 0,
            'database_writes': 0,
            'errors': 0,
            'start_time': None,
            'end_time': None
        }
        
        # 数据队列
        self.data_queue = queue.Queue(maxsize=10000)
        self.result_queue = queue.Queue()
        
    async def process_mass_stock_data(self):
        """处理大量股票推送数据"""
        logger.info("🚀 开始处理4000+股票推送数据...")
        self.stats['start_time'] = time.time()
        
        try:
            # 1. 扫描所有推送数据文件
            files = await self.scan_push_data_files()
            self.stats['total_files'] = len(files)
            
            if not files:
                logger.info("📁 没有找到推送数据文件")
                return True
            
            logger.info(f"📊 找到 {len(files)} 个推送数据文件")
            
            # 2. 并行处理文件
            await self.process_files_parallel(files)
            
            # 3. 生成处理报告
            await self.generate_processing_report()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 处理失败: {e}")
            return False
        finally:
            self.stats['end_time'] = time.time()
    
    async def scan_push_data_files(self):
        """扫描推送数据文件"""
        files = []
        
        if not self.data_dir.exists():
            logger.warning(f"📁 数据目录不存在: {self.data_dir}")
            return files
        
        # 扫描.dat文件
        dat_files = list(self.data_dir.glob('*.dat'))
        pkl_files = list(self.data_dir.glob('*.pkl'))
        
        # 按修改时间排序，优先处理最新的文件
        all_files = dat_files + pkl_files
        all_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
        
        logger.info(f"📄 找到 {len(dat_files)} 个.dat文件, {len(pkl_files)} 个.pkl文件")
        
        return all_files
    
    async def process_files_parallel(self, files: List[Path]):
        """并行处理文件"""
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async def process_single_file(file_path):
            async with semaphore:
                return await self.process_single_file(file_path)
        
        # 创建任务
        tasks = [process_single_file(file_path) for file_path in files]
        
        # 并行执行
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 统计结果
        success_count = sum(1 for r in results if r is True)
        error_count = len(results) - success_count
        
        logger.info(f"📊 文件处理完成: 成功 {success_count}, 失败 {error_count}")
    
    async def process_single_file(self, file_path: Path):
        """处理单个文件"""
        try:
            logger.info(f"📄 处理文件: {file_path.name}")
            
            # 读取文件数据
            stock_data_list = await self.read_file_data(file_path)
            
            if not stock_data_list:
                logger.warning(f"⚠️ 文件为空或格式错误: {file_path.name}")
                return True
            
            # 批量处理股票数据
            await self.process_stock_batch(stock_data_list, file_path.name)
            
            self.stats['processed_files'] += 1
            return True
            
        except Exception as e:
            logger.error(f"❌ 处理文件失败 {file_path.name}: {e}")
            self.stats['errors'] += 1
            return False
    
    async def read_file_data(self, file_path: Path) -> List[Dict]:
        """读取文件数据"""
        try:
            if file_path.suffix == '.dat':
                # JSON格式文件
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 如果是单个对象，转换为列表
                    if isinstance(data, dict):
                        return [data]
                    elif isinstance(data, list):
                        return data
                    else:
                        return []
            
            elif file_path.suffix == '.pkl':
                # Pickle格式文件
                with open(file_path, 'rb') as f:
                    data = pickle.load(f)
                    if isinstance(data, dict):
                        return [data]
                    elif isinstance(data, list):
                        return data
                    else:
                        return []
            
            else:
                logger.warning(f"⚠️ 不支持的文件格式: {file_path.suffix}")
                return []
                
        except Exception as e:
            logger.error(f"❌ 读取文件失败 {file_path.name}: {e}")
            return []
    
    async def process_stock_batch(self, stock_data_list: List[Dict], source_file: str):
        """批量处理股票数据"""
        try:
            # 分批处理
            for i in range(0, len(stock_data_list), self.batch_size):
                batch = stock_data_list[i:i + self.batch_size]
                
                # 转换数据格式
                db_records = self.convert_to_db_format(batch, source_file)
                
                # 写入数据库
                success = await self.batch_write_to_database(db_records)
                
                if success:
                    self.stats['processed_stocks'] += len(batch)
                    self.stats['database_writes'] += 1
                    logger.info(f"✅ 批量写入成功: {len(batch)} 条记录 (来源: {source_file})")
                else:
                    self.stats['errors'] += 1
                    logger.error(f"❌ 批量写入失败: {len(batch)} 条记录")
                
                # 避免过于频繁的请求
                await asyncio.sleep(0.1)
                
        except Exception as e:
            logger.error(f"❌ 批量处理失败: {e}")
            self.stats['errors'] += 1
    
    def convert_to_db_format(self, stock_data_list: List[Dict], source_file: str) -> List[Dict]:
        """转换为数据库格式"""
        db_records = []
        
        for stock_data in stock_data_list:
            try:
                # 使用system_config表存储，因为专门的表不存在
                record = {
                    'key': f'mass_stock_{stock_data.get("symbol", "unknown")}_{int(time.time())}',
                    'value': json.dumps({
                        'symbol': stock_data.get('symbol', ''),
                        'stock_name': stock_data.get('name', ''),
                        'price': float(stock_data.get('price', 0)),
                        'volume': int(stock_data.get('volume', 0)),
                        'change': float(stock_data.get('change', 0)),
                        'change_percent': float(stock_data.get('change_percent', 0)),
                        'timestamp': stock_data.get('timestamp', time.time()),
                        'source_file': source_file,
                        'processed_at': datetime.now().isoformat(),
                        'data_type': 'mass_push_data'
                    }),
                    'description': f'大量推送数据 - {stock_data.get("symbol", "unknown")}'
                }
                
                db_records.append(record)
                
            except Exception as e:
                logger.error(f"❌ 转换数据格式失败: {e}")
                continue
        
        return db_records
    
    async def batch_write_to_database(self, db_records: List[Dict]) -> bool:
        """批量写入数据库"""
        try:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {SUPABASE_KEY}',
                'apikey': SUPABASE_KEY,
                'Prefer': 'return=minimal'  # 减少返回数据量
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f'{SUPABASE_URL}/rest/v1/system_config',
                    headers=headers,
                    json=db_records,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    if response.status in [200, 201]:
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ 数据库写入失败: {response.status} - {error_text}")
                        return False
                        
        except Exception as e:
            logger.error(f"❌ 数据库写入异常: {e}")
            return False
    
    async def generate_processing_report(self):
        """生成处理报告"""
        duration = self.stats['end_time'] - self.stats['start_time']
        
        report = f"""
🚀 4000+股票推送数据处理报告
{'=' * 50}

📊 处理统计:
  - 总文件数: {self.stats['total_files']}
  - 已处理文件: {self.stats['processed_files']}
  - 总股票数: {self.stats['total_stocks']}
  - 已处理股票: {self.stats['processed_stocks']}
  - 数据库写入次数: {self.stats['database_writes']}
  - 错误次数: {self.stats['errors']}

⏱️ 性能指标:
  - 总耗时: {duration:.2f} 秒
  - 处理速度: {self.stats['processed_stocks'] / duration:.2f} 股票/秒
  - 成功率: {(self.stats['processed_stocks'] / max(self.stats['total_stocks'], 1)) * 100:.2f}%

🎯 系统状态:
  - 批量大小: {self.batch_size}
  - 最大并发: {self.max_concurrent}
  - 数据库: Supabase (system_config表)
  - 存储格式: JSON in system_config.value

{'=' * 50}
"""
        
        logger.info(report)
        
        # 保存报告到文件
        report_file = f'mass_stock_processing_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info(f"📄 处理报告已保存: {report_file}")
    
    async def cleanup_old_files(self, days_old: int = 1):
        """清理旧文件"""
        try:
            cutoff_time = datetime.now() - timedelta(days=days_old)
            cleaned_count = 0
            
            for file_path in self.data_dir.iterdir():
                if file_path.is_file():
                    file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if file_time < cutoff_time:
                        file_path.unlink()
                        cleaned_count += 1
            
            if cleaned_count > 0:
                logger.info(f"🧹 清理了 {cleaned_count} 个旧文件")
            
        except Exception as e:
            logger.error(f"❌ 清理文件失败: {e}")

async def main():
    """主函数"""
    processor = MassStockDatabaseProcessor()
    
    logger.info("🚀 启动4000+股票推送数据库处理器...")
    
    # 处理大量股票数据
    success = await processor.process_mass_stock_data()
    
    if success:
        logger.info("🎉 大量股票数据处理完成！")
        
        # 清理旧文件
        await processor.cleanup_old_files()
        
    else:
        logger.error("❌ 大量股票数据处理失败")
    
    return success

if __name__ == '__main__':
    asyncio.run(main())
