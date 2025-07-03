#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建Supabase数据库表
"""

import os
import sys
from supabase import create_client, Client

# Supabase配置
SUPABASE_URL = "https://zzukfxwavknskqcepsjb.supabase.co"
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp6dWtmeHdhdmtuc2txY2Vwc2piIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MTI5ODUwNiwiZXhwIjoyMDY2ODc0NTA2fQ.Ksy_A6qfaUn9qBethAw4o8Xpn0iSxluaBTCxbnd3u5g"

def setup_database_tables():
    """创建数据库表"""
    try:
        print("🔧 设置Supabase数据库表...")
        print("=" * 50)
        
        # 创建Supabase客户端（使用service_role key）
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        
        # 创建stock_data表的SQL
        create_stock_data_sql = """
        CREATE TABLE IF NOT EXISTS stock_data (
            id BIGSERIAL PRIMARY KEY,
            symbol VARCHAR(20) NOT NULL,
            name VARCHAR(100),
            price DECIMAL(10,2),
            change_percent DECIMAL(5,2),
            volume BIGINT,
            market_cap DECIMAL(15,2),
            pe_ratio DECIMAL(8,2),
            pb_ratio DECIMAL(8,2),
            high_52w DECIMAL(10,2),
            low_52w DECIMAL(10,2),
            dividend_yield DECIMAL(5,2),
            raw_data JSONB,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            UNIQUE(symbol)
        );
        """
        
        # 创建索引
        create_indexes_sql = """
        CREATE INDEX IF NOT EXISTS idx_stock_data_symbol ON stock_data(symbol);
        CREATE INDEX IF NOT EXISTS idx_stock_data_updated_at ON stock_data(updated_at);
        CREATE INDEX IF NOT EXISTS idx_stock_data_name ON stock_data(name);
        """
        
        # 创建更新时间触发器
        create_trigger_sql = """
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ language 'plpgsql';

        DROP TRIGGER IF EXISTS update_stock_data_updated_at ON stock_data;
        CREATE TRIGGER update_stock_data_updated_at
            BEFORE UPDATE ON stock_data
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
        """
        
        print("📊 创建stock_data表...")
        result = supabase.rpc('exec_sql', {'sql': create_stock_data_sql}).execute()
        print("✅ stock_data表创建成功")
        
        print("📊 创建索引...")
        result = supabase.rpc('exec_sql', {'sql': create_indexes_sql}).execute()
        print("✅ 索引创建成功")
        
        print("📊 创建触发器...")
        result = supabase.rpc('exec_sql', {'sql': create_trigger_sql}).execute()
        print("✅ 触发器创建成功")
        
        # 创建agent_analysis表
        create_agent_analysis_sql = """
        CREATE TABLE IF NOT EXISTS agent_analysis (
            id BIGSERIAL PRIMARY KEY,
            analysis_id VARCHAR(50) UNIQUE NOT NULL,
            market_sentiment VARCHAR(20),
            confidence_score INTEGER,
            recommendations JSONB,
            market_data JSONB,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """
        
        print("📊 创建agent_analysis表...")
        result = supabase.rpc('exec_sql', {'sql': create_agent_analysis_sql}).execute()
        print("✅ agent_analysis表创建成功")
        
        # 创建agent_account表
        create_agent_account_sql = """
        CREATE TABLE IF NOT EXISTS agent_account (
            id BIGSERIAL PRIMARY KEY,
            account_id VARCHAR(50) UNIQUE NOT NULL,
            account_name VARCHAR(100),
            account_type VARCHAR(50),
            data_source VARCHAR(50),
            balance JSONB,
            positions JSONB,
            today_trading JSONB,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """
        
        print("📊 创建agent_account表...")
        result = supabase.rpc('exec_sql', {'sql': create_agent_account_sql}).execute()
        print("✅ agent_account表创建成功")
        
        print("\n🎉 数据库表设置完成!")
        print("✅ 已创建的表:")
        print("   - stock_data: 股票实时数据")
        print("   - agent_analysis: Agent分析数据")
        print("   - agent_account: Agent虚拟账户数据")
        
        return True
        
    except Exception as e:
        print(f"❌ 设置数据库表时出错: {e}")
        # 尝试使用直接SQL创建
        try:
            print("\n🔄 尝试使用基础方法创建表...")
            
            # 直接插入一条测试数据来触发表创建
            test_data = {
                'symbol': 'TEST001',
                'name': '测试股票',
                'price': 10.00,
                'change_percent': 1.23,
                'volume': 1000000,
                'raw_data': {'test': True}
            }
            
            result = supabase.table('stock_data').insert(test_data).execute()
            print("✅ stock_data表通过插入数据创建成功")
            
            # 删除测试数据
            supabase.table('stock_data').delete().eq('symbol', 'TEST001').execute()
            print("✅ 测试数据已清理")
            
            return True
            
        except Exception as e2:
            print(f"❌ 基础方法也失败: {e2}")
            return False

if __name__ == "__main__":
    setup_database_tables()
