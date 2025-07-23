-- Agent智能交易系统 - Supabase数据表创建脚本
-- 请在Supabase SQL编辑器中执行此脚本

-- 1. 股票基础信息表
CREATE TABLE IF NOT EXISTS stocks (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(10) UNIQUE NOT NULL,  -- 股票代码 SH600000
    name VARCHAR(50) NOT NULL,           -- 股票名称
    exchange VARCHAR(10) NOT NULL,       -- 交易所 SH/SZ
    industry VARCHAR(50),                -- 行业分类
    market_cap BIGINT,                   -- 市值
    listing_date DATE,                   -- 上市日期
    is_active BOOLEAN DEFAULT true,      -- 是否活跃
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. 实时行情数据表
CREATE TABLE IF NOT EXISTS stock_quotes (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    trade_time TIMESTAMP WITH TIME ZONE NOT NULL,
    price DECIMAL(10,3) NOT NULL,       -- 当前价格
    change_percent DECIMAL(8,4),        -- 涨跌幅
    volume BIGINT,                      -- 成交量
    amount DECIMAL(15,2),               -- 成交额
    high_price DECIMAL(10,3),           -- 最高价
    low_price DECIMAL(10,3),            -- 最低价
    open_price DECIMAL(10,3),           -- 开盘价
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. 日K线数据表
CREATE TABLE IF NOT EXISTS daily_klines (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    trade_date DATE NOT NULL,
    open_price DECIMAL(10,3) NOT NULL,
    high_price DECIMAL(10,3) NOT NULL,
    low_price DECIMAL(10,3) NOT NULL,
    close_price DECIMAL(10,3) NOT NULL,
    volume BIGINT NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    change_percent DECIMAL(8,4),
    turnover_rate DECIMAL(8,4),
    -- 技术指标
    ma5 DECIMAL(10,3),                  -- 5日均线
    ma10 DECIMAL(10,3),                 -- 10日均线
    ma20 DECIMAL(10,3),                 -- 20日均线
    ma60 DECIMAL(10,3),                 -- 60日均线
    macd_dif DECIMAL(10,6),             -- MACD DIF
    macd_dea DECIMAL(10,6),             -- MACD DEA
    macd_histogram DECIMAL(10,6),       -- MACD柱状图
    rsi DECIMAL(8,4),                   -- RSI指标
    kdj_k DECIMAL(8,4),                 -- KDJ K值
    kdj_d DECIMAL(8,4),                 -- KDJ D值
    kdj_j DECIMAL(8,4),                 -- KDJ J值
    bb_upper DECIMAL(10,3),             -- 布林带上轨
    bb_middle DECIMAL(10,3),            -- 布林带中轨
    bb_lower DECIMAL(10,3),             -- 布林带下轨
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(symbol, trade_date)
);

-- 4. Agent决策记录表
CREATE TABLE IF NOT EXISTS agent_decisions (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    decision_time TIMESTAMP WITH TIME ZONE NOT NULL,
    action VARCHAR(10) NOT NULL,        -- BUY/SELL/HOLD
    price DECIMAL(10,3) NOT NULL,       -- 决策时价格
    confidence INTEGER NOT NULL,        -- 信心度 0-100
    reason TEXT,                        -- 决策理由
    technical_score DECIMAL(5,2),       -- 技术面评分
    fundamental_score DECIMAL(5,2),     -- 基本面评分
    market_sentiment DECIMAL(5,2),      -- 市场情绪评分
    -- 技术指标信号
    technical_signals JSONB,            -- 技术指标详情
    -- 预测结果
    predicted_return_1d DECIMAL(8,4),   -- 预测1天收益率
    predicted_return_3d DECIMAL(8,4),   -- 预测3天收益率
    predicted_trend VARCHAR(10),        -- 预测趋势
    model_confidence DECIMAL(5,2),      -- 模型置信度
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5. Agent学习样本表
CREATE TABLE IF NOT EXISTS agent_learning_samples (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    sample_date DATE NOT NULL,
    -- 输入特征 (技术指标等)
    features JSONB NOT NULL,            -- 特征向量
    -- 输出标签 (未来收益率)
    label_1d DECIMAL(8,4),              -- 1天后收益率
    label_3d DECIMAL(8,4),              -- 3天后收益率
    label_5d DECIMAL(8,4),              -- 5天后收益率
    label_10d DECIMAL(8,4),             -- 10天后收益率
    -- 分类标签
    trend_1d VARCHAR(10),               -- 1天趋势 UP/DOWN/FLAT
    trend_3d VARCHAR(10),               -- 3天趋势
    trend_5d VARCHAR(10),               -- 5天趋势
    -- 标注信息
    is_validated BOOLEAN DEFAULT false, -- 是否已验证
    validation_date DATE,               -- 验证日期
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 6. Agent策略回测表
CREATE TABLE IF NOT EXISTS agent_backtests (
    id BIGSERIAL PRIMARY KEY,
    strategy_name VARCHAR(100) NOT NULL,
    strategy_version VARCHAR(20),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    initial_capital DECIMAL(15,2) NOT NULL,
    final_capital DECIMAL(15,2) NOT NULL,
    total_return DECIMAL(8,4) NOT NULL,  -- 总收益率
    annual_return DECIMAL(8,4),          -- 年化收益率
    max_drawdown DECIMAL(8,4),           -- 最大回撤
    sharpe_ratio DECIMAL(8,4),           -- 夏普比率
    win_rate DECIMAL(8,4),               -- 胜率
    total_trades INTEGER,                -- 总交易次数
    profitable_trades INTEGER,           -- 盈利交易次数
    avg_profit DECIMAL(8,4),             -- 平均盈利
    avg_loss DECIMAL(8,4),               -- 平均亏损
    max_consecutive_wins INTEGER,        -- 最大连胜
    max_consecutive_losses INTEGER,      -- 最大连败
    config JSONB,                        -- 策略配置
    performance_metrics JSONB,           -- 详细性能指标
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 7. Agent交易记录表
CREATE TABLE IF NOT EXISTS agent_trades (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    action VARCHAR(10) NOT NULL,        -- BUY/SELL
    quantity INTEGER NOT NULL,          -- 交易数量
    price DECIMAL(10,3) NOT NULL,       -- 交易价格
    amount DECIMAL(15,2) NOT NULL,      -- 交易金额
    trade_time TIMESTAMP WITH TIME ZONE NOT NULL,
    decision_id BIGINT REFERENCES agent_decisions(id),
    commission DECIMAL(10,2),           -- 手续费
    slippage DECIMAL(8,4),              -- 滑点
    status VARCHAR(20) DEFAULT 'PENDING', -- PENDING/FILLED/CANCELLED/FAILED
    fill_time TIMESTAMP WITH TIME ZONE, -- 成交时间
    notes TEXT,                         -- 备注
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 8. 市场情绪指标表
CREATE TABLE IF NOT EXISTS market_sentiment (
    id BIGSERIAL PRIMARY KEY,
    trade_date DATE NOT NULL UNIQUE,
    -- 市场整体指标
    advance_decline_ratio DECIMAL(8,4), -- 涨跌比
    limit_up_count INTEGER,             -- 涨停数量
    limit_down_count INTEGER,           -- 跌停数量
    new_high_count INTEGER,             -- 创新高数量
    new_low_count INTEGER,              -- 创新低数量
    total_volume BIGINT,                -- 总成交量
    total_amount DECIMAL(20,2),         -- 总成交额
    -- 情绪指标
    fear_greed_index DECIMAL(5,2),      -- 恐惧贪婪指数
    vix_index DECIMAL(8,4),             -- 波动率指数
    sentiment_score DECIMAL(5,2),       -- 综合情绪评分
    market_trend VARCHAR(20),           -- 市场趋势
    -- 板块数据
    sector_performance JSONB,           -- 板块表现
    hot_concepts JSONB,                 -- 热门概念
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 9. Agent模型管理表
CREATE TABLE IF NOT EXISTS agent_models (
    id BIGSERIAL PRIMARY KEY,
    model_name VARCHAR(100) NOT NULL,
    model_type VARCHAR(50) NOT NULL,    -- classification/regression
    symbol VARCHAR(10),                 -- 特定股票模型，NULL表示通用模型
    model_version VARCHAR(20) NOT NULL,
    model_path TEXT,                    -- 模型文件路径
    training_data_size INTEGER,         -- 训练数据量
    validation_accuracy DECIMAL(8,4),   -- 验证准确率
    validation_r2_score DECIMAL(8,4),   -- R²分数
    feature_importance JSONB,           -- 特征重要性
    hyperparameters JSONB,              -- 超参数
    training_date DATE NOT NULL,
    is_active BOOLEAN DEFAULT true,     -- 是否启用
    performance_metrics JSONB,          -- 性能指标
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建索引优化查询性能
CREATE INDEX IF NOT EXISTS idx_stock_quotes_symbol_time ON stock_quotes(symbol, trade_time DESC);
CREATE INDEX IF NOT EXISTS idx_stock_quotes_time ON stock_quotes(trade_time DESC);
CREATE INDEX IF NOT EXISTS idx_daily_klines_symbol_date ON daily_klines(symbol, trade_date DESC);
CREATE INDEX IF NOT EXISTS idx_daily_klines_date ON daily_klines(trade_date DESC);
CREATE INDEX IF NOT EXISTS idx_agent_decisions_symbol_time ON agent_decisions(symbol, decision_time DESC);
CREATE INDEX IF NOT EXISTS idx_agent_decisions_action ON agent_decisions(action);
CREATE INDEX IF NOT EXISTS idx_agent_decisions_time ON agent_decisions(decision_time DESC);
CREATE INDEX IF NOT EXISTS idx_agent_learning_samples_symbol_date ON agent_learning_samples(symbol, sample_date DESC);
CREATE INDEX IF NOT EXISTS idx_agent_trades_symbol_time ON agent_trades(symbol, trade_time DESC);
CREATE INDEX IF NOT EXISTS idx_agent_trades_status ON agent_trades(status);
CREATE INDEX IF NOT EXISTS idx_market_sentiment_date ON market_sentiment(trade_date DESC);
CREATE INDEX IF NOT EXISTS idx_agent_models_active ON agent_models(is_active, model_type);

-- 创建有用的视图
CREATE OR REPLACE VIEW v_latest_quotes AS
SELECT DISTINCT ON (symbol) 
    symbol, trade_time, price, change_percent, volume, amount
FROM stock_quotes 
ORDER BY symbol, trade_time DESC;

CREATE OR REPLACE VIEW v_agent_performance_daily AS
SELECT 
    DATE(decision_time) as trade_date,
    action,
    COUNT(*) as decision_count,
    AVG(confidence) as avg_confidence,
    COUNT(CASE WHEN at.status = 'FILLED' THEN 1 END) as executed_count,
    AVG(CASE WHEN at.status = 'FILLED' THEN at.amount END) as avg_trade_amount
FROM agent_decisions ad
LEFT JOIN agent_trades at ON ad.id = at.decision_id
GROUP BY DATE(decision_time), action
ORDER BY trade_date DESC;

CREATE OR REPLACE VIEW v_top_performing_stocks AS
SELECT 
    symbol,
    COUNT(*) as decision_count,
    AVG(confidence) as avg_confidence,
    COUNT(CASE WHEN action = 'BUY' THEN 1 END) as buy_signals,
    COUNT(CASE WHEN action = 'SELL' THEN 1 END) as sell_signals,
    MAX(decision_time) as last_decision_time
FROM agent_decisions 
WHERE decision_time >= NOW() - INTERVAL '7 days'
GROUP BY symbol
HAVING COUNT(*) >= 2
ORDER BY avg_confidence DESC, decision_count DESC;

-- 创建RLS (Row Level Security) 策略
ALTER TABLE stocks ENABLE ROW LEVEL SECURITY;
ALTER TABLE stock_quotes ENABLE ROW LEVEL SECURITY;
ALTER TABLE daily_klines ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_decisions ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_learning_samples ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_backtests ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_trades ENABLE ROW LEVEL SECURITY;
ALTER TABLE market_sentiment ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_models ENABLE ROW LEVEL SECURITY;

-- 创建允许匿名访问的策略 (根据需要调整)
CREATE POLICY "Allow anonymous access" ON stocks FOR ALL USING (true);
CREATE POLICY "Allow anonymous access" ON stock_quotes FOR ALL USING (true);
CREATE POLICY "Allow anonymous access" ON daily_klines FOR ALL USING (true);
CREATE POLICY "Allow anonymous access" ON agent_decisions FOR ALL USING (true);
CREATE POLICY "Allow anonymous access" ON agent_learning_samples FOR ALL USING (true);
CREATE POLICY "Allow anonymous access" ON agent_backtests FOR ALL USING (true);
CREATE POLICY "Allow anonymous access" ON agent_trades FOR ALL USING (true);
CREATE POLICY "Allow anonymous access" ON market_sentiment FOR ALL USING (true);
CREATE POLICY "Allow anonymous access" ON agent_models FOR ALL USING (true);

-- 插入一些示例数据
INSERT INTO stocks (symbol, name, exchange, industry) VALUES
('SH600519', '贵州茅台', 'SH', '白酒'),
('SZ000858', '五粮液', 'SZ', '白酒'),
('SZ002594', '比亚迪', 'SZ', '汽车'),
('SZ300750', '宁德时代', 'SZ', '电池'),
('SH600036', '招商银行', 'SH', '银行')
ON CONFLICT (symbol) DO NOTHING;

-- 创建函数用于自动更新技术指标
CREATE OR REPLACE FUNCTION update_technical_indicators()
RETURNS TRIGGER AS $$
BEGIN
    -- 这里可以添加自动计算技术指标的逻辑
    -- 当插入新的K线数据时自动计算MA、MACD等指标
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 创建触发器
CREATE TRIGGER trigger_update_technical_indicators
    AFTER INSERT ON daily_klines
    FOR EACH ROW
    EXECUTE FUNCTION update_technical_indicators();

-- 完成提示
SELECT 'Agent智能交易系统数据表创建完成！' as message;
