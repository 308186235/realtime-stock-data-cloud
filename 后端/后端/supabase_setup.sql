-- AI股票交易系统 - Supabase数据库表结构
-- 在Supabase SQL编辑器中运行此脚本

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

-- 6. 创建策略表
CREATE TABLE IF NOT EXISTS strategies (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    strategy_type TEXT NOT NULL, -- 'technical', 'fundamental', 'ai', 'custom'
    parameters JSONB,
    status TEXT DEFAULT 'inactive' CHECK (status IN ('active', 'inactive', 'paused')),
    profit_pct DECIMAL(8,4) DEFAULT 0,
    total_trades INTEGER DEFAULT 0,
    win_rate DECIMAL(5,4) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 7. 创建实时股票数据表 (用于历史数据，实时数据用KV缓存)
CREATE TABLE IF NOT EXISTS stock_prices (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    stock_code TEXT REFERENCES stocks(code) NOT NULL,
    price DECIMAL(10,3) NOT NULL,
    change_amount DECIMAL(10,3),
    change_pct DECIMAL(8,4),
    volume BIGINT,
    turnover DECIMAL(20,2),
    high DECIMAL(10,3),
    low DECIMAL(10,3),
    open DECIMAL(10,3),
    prev_close DECIMAL(10,3),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    INDEX (stock_code, timestamp)
);

-- 8. 创建AI分析结果表
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

-- 9. 创建系统配置表
CREATE TABLE IF NOT EXISTS system_config (
    key TEXT PRIMARY KEY,
    value JSONB NOT NULL,
    description TEXT,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 插入示例股票数据
INSERT INTO stocks (code, name, market, sector, industry) VALUES
('600000', '浦发银行', 'SH', '金融', '银行'),
('000001', '平安银行', 'SZ', '金融', '银行'),
('000002', '万科A', 'SZ', '房地产', '房地产开发'),
('600036', '招商银行', 'SH', '金融', '银行'),
('000858', '五粮液', 'SZ', '消费', '白酒'),
('600519', '贵州茅台', 'SH', '消费', '白酒'),
('000858', '五粮液', 'SZ', '消费', '白酒')
ON CONFLICT (code) DO NOTHING;

-- 插入系统配置
INSERT INTO system_config (key, value, description) VALUES
('market_hours', '{"open": "09:30", "close": "15:00", "lunch_break": {"start": "11:30", "end": "13:00"}}', '交易时间配置'),
('data_sources', '{"primary": "tushare", "backup": "tdx", "realtime": "websocket"}', '数据源配置'),
('trading_rules', '{"min_amount": 100, "max_position": 0.1, "stop_loss": 0.05}', '交易规则配置')
ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, updated_at = NOW();

-- 创建RLS (Row Level Security) 策略
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE portfolios ENABLE ROW LEVEL SECURITY;
ALTER TABLE holdings ENABLE ROW LEVEL SECURITY;
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE strategies ENABLE ROW LEVEL SECURITY;

-- 用户只能访问自己的数据
CREATE POLICY "Users can view own profile" ON user_profiles FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users can update own profile" ON user_profiles FOR UPDATE USING (auth.uid() = id);

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
CREATE POLICY "Users can create own transactions" ON transactions FOR INSERT WITH CHECK (
    auth.uid() IN (SELECT user_id FROM portfolios WHERE id = portfolio_id)
);

CREATE POLICY "Users can view own strategies" ON strategies FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can manage own strategies" ON strategies FOR ALL USING (auth.uid() = user_id);

-- 股票数据和AI分析对所有认证用户可读
CREATE POLICY "Authenticated users can view stocks" ON stocks FOR SELECT TO authenticated USING (true);
CREATE POLICY "Authenticated users can view stock prices" ON stock_prices FOR SELECT TO authenticated USING (true);
CREATE POLICY "Authenticated users can view AI analysis" ON ai_analysis FOR SELECT TO authenticated USING (true);
CREATE POLICY "Authenticated users can view system config" ON system_config FOR SELECT TO authenticated USING (true);

-- 创建更新时间触发器函数
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 为需要的表添加更新时间触发器
CREATE TRIGGER update_user_profiles_updated_at BEFORE UPDATE ON user_profiles FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_portfolios_updated_at BEFORE UPDATE ON portfolios FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_holdings_updated_at BEFORE UPDATE ON holdings FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_strategies_updated_at BEFORE UPDATE ON strategies FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_stocks_updated_at BEFORE UPDATE ON stocks FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
