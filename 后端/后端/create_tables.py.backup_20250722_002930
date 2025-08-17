"""
在Supabase中创建数据库表
"""
import sys
import os

# 添加backend目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.config.supabase import get_admin_client

def create_tables():
    """创建数据库表"""
    print("🏗️ 开始创建数据库表...")
    
    client = get_admin_client()
    
    # SQL建表脚本
    sql_script = """
    -- AI股票交易系统 - Supabase数据库表结构
    
    -- 1. 创建用户扩展表 (Supabase已有auth.users，这里创建扩展信息)
    CREATE TABLE IF NOT EXISTS user_profiles (
        id UUID REFERENCES auth.users(id) PRIMARY KEY,
        username TEXT UNIQUE,
        display_name TEXT,
        avatar_url TEXT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    
    -- 2. 创建投资组合表
    CREATE TABLE IF NOT EXISTS portfolios (
        id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        user_id UUID REFERENCES auth.users(id) NOT NULL,
        name TEXT NOT NULL,
        total_value DECIMAL(15,2) DEFAULT 0,
        cash DECIMAL(15,2) DEFAULT 0,
        stock_value DECIMAL(15,2) DEFAULT 0,
        is_default BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    
    -- 3. 创建股票基础信息表
    CREATE TABLE IF NOT EXISTS stocks (
        code TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        market TEXT NOT NULL, -- 'SH', 'SZ', 'BJ'
        sector TEXT,
        industry TEXT,
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    
    -- 4. 创建持仓表
    CREATE TABLE IF NOT EXISTS holdings (
        id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        portfolio_id UUID REFERENCES portfolios(id) NOT NULL,
        stock_code TEXT REFERENCES stocks(code) NOT NULL,
        shares INTEGER NOT NULL CHECK (shares >= 0),
        cost_price DECIMAL(10,3) NOT NULL,
        current_price DECIMAL(10,3),
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        UNIQUE(portfolio_id, stock_code)
    );
    
    -- 5. 创建交易记录表
    CREATE TABLE IF NOT EXISTS transactions (
        id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        portfolio_id UUID REFERENCES portfolios(id) NOT NULL,
        stock_code TEXT REFERENCES stocks(code) NOT NULL,
        transaction_type TEXT NOT NULL CHECK (transaction_type IN ('buy', 'sell')),
        shares INTEGER NOT NULL CHECK (shares > 0),
        price DECIMAL(10,3) NOT NULL,
        total_amount DECIMAL(15,2) NOT NULL,
        commission DECIMAL(10,2) DEFAULT 0,
        notes TEXT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    
    -- 6. 创建AI分析结果表
    CREATE TABLE IF NOT EXISTS ai_analysis (
        id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        stock_code TEXT REFERENCES stocks(code) NOT NULL,
        analysis_type TEXT NOT NULL, -- 'technical', 'sentiment', 'fundamental'
        recommendation TEXT CHECK (recommendation IN ('strong_buy', 'buy', 'hold', 'sell', 'strong_sell')),
        confidence DECIMAL(3,2) CHECK (confidence >= 0 AND confidence <= 1),
        reasoning TEXT,
        target_price DECIMAL(10,3),
        risk_level TEXT CHECK (risk_level IN ('low', 'medium', 'high')),
        analysis_data JSONB,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    
    -- 7. 创建系统配置表
    CREATE TABLE IF NOT EXISTS system_config (
        key TEXT PRIMARY KEY,
        value JSONB NOT NULL,
        description TEXT,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    
    -- 8. 启用行级安全策略
    ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
    ALTER TABLE portfolios ENABLE ROW LEVEL SECURITY;
    ALTER TABLE holdings ENABLE ROW LEVEL SECURITY;
    ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;
    
    -- 9. 创建安全策略
    DROP POLICY IF EXISTS "Users can view own profile" ON user_profiles;
    CREATE POLICY "Users can view own profile" ON user_profiles FOR SELECT USING (auth.uid() = id);
    
    DROP POLICY IF EXISTS "Users can update own profile" ON user_profiles;
    CREATE POLICY "Users can update own profile" ON user_profiles FOR UPDATE USING (auth.uid() = id);
    
    DROP POLICY IF EXISTS "Users can view own portfolios" ON portfolios;
    CREATE POLICY "Users can view own portfolios" ON portfolios FOR SELECT USING (auth.uid() = user_id);
    
    DROP POLICY IF EXISTS "Users can manage own portfolios" ON portfolios;
    CREATE POLICY "Users can manage own portfolios" ON portfolios FOR ALL USING (auth.uid() = user_id);
    """
    
    try:
        # 执行SQL脚本
        result = client.rpc('exec_sql', {'sql': sql_script}).execute()
        print("✅ 数据库表创建成功！")
        return True
        
    except Exception as e:
        print(f"❌ 创建表失败，尝试逐个创建: {str(e)}")
        
        # 如果批量执行失败，尝试逐个创建表
        tables = [
            ("user_profiles", """
                CREATE TABLE IF NOT EXISTS user_profiles (
                    id UUID REFERENCES auth.users(id) PRIMARY KEY,
                    username TEXT UNIQUE,
                    display_name TEXT,
                    avatar_url TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
            """),
            ("stocks", """
                CREATE TABLE IF NOT EXISTS stocks (
                    code TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    market TEXT NOT NULL,
                    sector TEXT,
                    industry TEXT,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
            """),
            ("system_config", """
                CREATE TABLE IF NOT EXISTS system_config (
                    key TEXT PRIMARY KEY,
                    value JSONB NOT NULL,
                    description TEXT,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
            """)
        ]
        
        success_count = 0
        for table_name, sql in tables:
            try:
                client.rpc('exec_sql', {'sql': sql}).execute()
                print(f"✅ 表 {table_name} 创建成功")
                success_count += 1
            except Exception as table_error:
                print(f"❌ 表 {table_name} 创建失败: {str(table_error)}")
        
        return success_count > 0

if __name__ == "__main__":
    create_tables()
