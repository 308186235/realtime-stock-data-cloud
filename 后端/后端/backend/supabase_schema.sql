-- AI股票交易系统数据库表结构
-- 在Supabase SQL编辑器中运行此脚本

-- 1. 用户表
CREATE TABLE IF NOT EXISTS users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    phone VARCHAR(20),
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. 股票基础信息表
CREATE TABLE IF NOT EXISTS stocks (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    stock_code VARCHAR(10) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    market VARCHAR(10) NOT NULL, -- SH, SZ, BJ
    industry VARCHAR(50),
    sector VARCHAR(50),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. 股票价格表
CREATE TABLE IF NOT EXISTS stock_prices (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    stock_code VARCHAR(10) NOT NULL,
    price DECIMAL(10,3) NOT NULL,
    open_price DECIMAL(10,3),
    high_price DECIMAL(10,3),
    low_price DECIMAL(10,3),
    close_price DECIMAL(10,3),
    volume BIGINT,
    turnover DECIMAL(15,2),
    change_amount DECIMAL(10,3),
    change_percent DECIMAL(5,2),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. 投资组合表
CREATE TABLE IF NOT EXISTS portfolios (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    total_value DECIMAL(15,2) DEFAULT 0,
    cash_balance DECIMAL(15,2) DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5. 持仓表
CREATE TABLE IF NOT EXISTS holdings (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    portfolio_id UUID NOT NULL REFERENCES portfolios(id) ON DELETE CASCADE,
    stock_code VARCHAR(10) NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 0,
    avg_cost DECIMAL(10,3) NOT NULL DEFAULT 0,
    current_price DECIMAL(10,3),
    market_value DECIMAL(15,2),
    unrealized_pnl DECIMAL(15,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (stock_code) REFERENCES stocks(stock_code)
);

-- 6. 交易记录表
CREATE TABLE IF NOT EXISTS transactions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    portfolio_id UUID NOT NULL REFERENCES portfolios(id) ON DELETE CASCADE,
    stock_code VARCHAR(10) NOT NULL,
    transaction_type VARCHAR(10) NOT NULL, -- BUY, SELL
    quantity INTEGER NOT NULL,
    price DECIMAL(10,3) NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    commission DECIMAL(10,2) DEFAULT 0,
    tax DECIMAL(10,2) DEFAULT 0,
    net_amount DECIMAL(15,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'PENDING', -- PENDING, COMPLETED, CANCELLED
    order_id VARCHAR(50),
    executed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (stock_code) REFERENCES stocks(stock_code)
);

-- 7. AI分析结果表
CREATE TABLE IF NOT EXISTS ai_analysis (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    stock_code VARCHAR(10),
    analysis_type VARCHAR(50) NOT NULL, -- TECHNICAL, FUNDAMENTAL, SENTIMENT
    score DECIMAL(5,2), -- 0-100分
    recommendation VARCHAR(20), -- BUY, SELL, HOLD
    confidence DECIMAL(5,2), -- 置信度0-100
    analysis_data JSONB, -- 详细分析数据
    summary TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (stock_code) REFERENCES stocks(stock_code)
);

-- 8. 交易策略表
CREATE TABLE IF NOT EXISTS strategies (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    strategy_type VARCHAR(50) NOT NULL, -- MOMENTUM, MEAN_REVERSION, etc.
    parameters JSONB, -- 策略参数
    is_active BOOLEAN DEFAULT true,
    performance_data JSONB, -- 策略表现数据
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 9. 系统配置表
CREATE TABLE IF NOT EXISTS system_config (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value TEXT,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 10. 交易日历表
CREATE TABLE IF NOT EXISTS trading_calendar (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    trade_date DATE UNIQUE NOT NULL,
    is_trading_day BOOLEAN NOT NULL DEFAULT true,
    market VARCHAR(10) NOT NULL DEFAULT 'A', -- A股市场
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建索引以提高查询性能
CREATE INDEX IF NOT EXISTS idx_stock_prices_code_time ON stock_prices(stock_code, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_holdings_portfolio ON holdings(portfolio_id);
CREATE INDEX IF NOT EXISTS idx_transactions_portfolio ON transactions(portfolio_id);
CREATE INDEX IF NOT EXISTS idx_transactions_stock ON transactions(stock_code);
CREATE INDEX IF NOT EXISTS idx_ai_analysis_stock ON ai_analysis(stock_code);
CREATE INDEX IF NOT EXISTS idx_ai_analysis_time ON ai_analysis(created_at DESC);

-- 插入一些基础数据
INSERT INTO system_config (config_key, config_value, description) VALUES
('market_open_time', '09:30', '市场开盘时间'),
('market_close_time', '15:00', '市场收盘时间'),
('trading_fee_rate', '0.0003', '交易手续费率'),
('stamp_tax_rate', '0.001', '印花税率'),
('min_trade_amount', '100', '最小交易金额'),
('max_positions', '10', '最大持仓数量')
ON CONFLICT (config_key) DO NOTHING;

-- 插入一些示例股票数据
INSERT INTO stocks (stock_code, name, market, industry) VALUES
('000001', '平安银行', 'SZ', '银行'),
('000002', '万科A', 'SZ', '房地产'),
('600000', '浦发银行', 'SH', '银行'),
('600036', '招商银行', 'SH', '银行'),
('600519', '贵州茅台', 'SH', '食品饮料'),
('000858', '五粮液', 'SZ', '食品饮料'),
('002415', '海康威视', 'SZ', '电子'),
('300059', '东方财富', 'SZ', '非银金融')
ON CONFLICT (stock_code) DO NOTHING;

-- 启用行级安全性(RLS)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE portfolios ENABLE ROW LEVEL SECURITY;
ALTER TABLE holdings ENABLE ROW LEVEL SECURITY;
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE strategies ENABLE ROW LEVEL SECURITY;

-- 创建RLS策略(用户只能访问自己的数据)
CREATE POLICY "Users can view own data" ON users FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users can update own data" ON users FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users can view own portfolios" ON portfolios FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can manage own portfolios" ON portfolios FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can view own holdings" ON holdings FOR SELECT USING (
    auth.uid() IN (SELECT user_id FROM portfolios WHERE id = portfolio_id)
);
CREATE POLICY "Users can manage own holdings" ON holdings FOR ALL USING (
    auth.uid() IN (SELECT user_id FROM portfolios WHERE id = portfolio_id)
);

CREATE POLICY "Users can view own transactions" ON transactions FOR SELECT USING (
    auth.uid() IN (SELECT user_id FROM portfolios WHERE id = portfolio_id)
);
CREATE POLICY "Users can manage own transactions" ON transactions FOR ALL USING (
    auth.uid() IN (SELECT user_id FROM portfolios WHERE id = portfolio_id)
);

CREATE POLICY "Users can view own strategies" ON strategies FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can manage own strategies" ON strategies FOR ALL USING (auth.uid() = user_id);
