-- 🗄️ 股票交易数据库设计 - 用于复盘分析和Agent学习
-- 创建时间: 2025-07-03
-- 用途: 数据保存、复盘分析、云端Agent学习、盈利率提升

-- ================================
-- 1. 股票基础数据表
-- ================================

-- 股票基本信息表
CREATE TABLE IF NOT EXISTS stocks (
    id SERIAL PRIMARY KEY,
    stock_code VARCHAR(10) NOT NULL UNIQUE,
    stock_name VARCHAR(100) NOT NULL,
    market VARCHAR(10) NOT NULL, -- SH/SZ/BJ
    industry VARCHAR(50),
    sector VARCHAR(50),
    listing_date DATE,
    total_shares BIGINT,
    circulating_shares BIGINT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 股票实时行情数据表
CREATE TABLE IF NOT EXISTS stock_quotes (
    id SERIAL PRIMARY KEY,
    stock_code VARCHAR(10) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    open_price DECIMAL(10,3),
    high_price DECIMAL(10,3),
    low_price DECIMAL(10,3),
    close_price DECIMAL(10,3),
    volume BIGINT,
    turnover DECIMAL(15,2),
    change_amount DECIMAL(10,3),
    change_percent DECIMAL(8,4),
    bid_prices DECIMAL(10,3)[5], -- 买1-5价格
    ask_prices DECIMAL(10,3)[5], -- 卖1-5价格
    bid_volumes INTEGER[5], -- 买1-5量
    ask_volumes INTEGER[5], -- 卖1-5量
    data_source VARCHAR(20) DEFAULT 'chagubang',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT fk_stock_quotes_code FOREIGN KEY (stock_code) REFERENCES stocks(stock_code)
);

-- 创建索引优化查询性能
CREATE INDEX IF NOT EXISTS idx_stock_quotes_code_time ON stock_quotes(stock_code, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_stock_quotes_timestamp ON stock_quotes(timestamp DESC);

-- ================================
-- 2. 交易记录表
-- ================================

-- 交易账户表
CREATE TABLE IF NOT EXISTS trading_accounts (
    id SERIAL PRIMARY KEY,
    account_id VARCHAR(50) NOT NULL UNIQUE,
    account_name VARCHAR(100),
    broker VARCHAR(50), -- 券商
    account_type VARCHAR(20) DEFAULT 'stock', -- stock/futures/options
    initial_capital DECIMAL(15,2),
    current_balance DECIMAL(15,2),
    total_assets DECIMAL(15,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 交易记录表
CREATE TABLE IF NOT EXISTS trading_records (
    id SERIAL PRIMARY KEY,
    account_id VARCHAR(50) NOT NULL,
    stock_code VARCHAR(10) NOT NULL,
    trade_type VARCHAR(10) NOT NULL, -- BUY/SELL
    trade_price DECIMAL(10,3) NOT NULL,
    trade_quantity INTEGER NOT NULL,
    trade_amount DECIMAL(15,2) NOT NULL,
    commission DECIMAL(10,2) DEFAULT 0,
    stamp_tax DECIMAL(10,2) DEFAULT 0,
    transfer_fee DECIMAL(10,2) DEFAULT 0,
    total_fee DECIMAL(10,2) DEFAULT 0,
    trade_time TIMESTAMP WITH TIME ZONE NOT NULL,
    order_id VARCHAR(50),
    strategy_id VARCHAR(50), -- 关联策略
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT fk_trading_records_account FOREIGN KEY (account_id) REFERENCES trading_accounts(account_id),
    CONSTRAINT fk_trading_records_stock FOREIGN KEY (stock_code) REFERENCES stocks(stock_code)
);

-- 持仓记录表
CREATE TABLE IF NOT EXISTS positions (
    id SERIAL PRIMARY KEY,
    account_id VARCHAR(50) NOT NULL,
    stock_code VARCHAR(10) NOT NULL,
    position_quantity INTEGER NOT NULL,
    average_cost DECIMAL(10,3) NOT NULL,
    current_price DECIMAL(10,3),
    market_value DECIMAL(15,2),
    unrealized_pnl DECIMAL(15,2),
    unrealized_pnl_percent DECIMAL(8,4),
    position_date DATE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT fk_positions_account FOREIGN KEY (account_id) REFERENCES trading_accounts(account_id),
    CONSTRAINT fk_positions_stock FOREIGN KEY (stock_code) REFERENCES stocks(stock_code),
    UNIQUE(account_id, stock_code, position_date)
);

-- ================================
-- 3. 复盘分析表
-- ================================

-- 交易复盘分析表
CREATE TABLE IF NOT EXISTS trade_analysis (
    id SERIAL PRIMARY KEY,
    account_id VARCHAR(50) NOT NULL,
    analysis_date DATE NOT NULL,
    total_trades INTEGER DEFAULT 0,
    winning_trades INTEGER DEFAULT 0,
    losing_trades INTEGER DEFAULT 0,
    win_rate DECIMAL(8,4),
    total_pnl DECIMAL(15,2),
    total_return_percent DECIMAL(8,4),
    max_drawdown DECIMAL(8,4),
    sharpe_ratio DECIMAL(8,4),
    profit_factor DECIMAL(8,4),
    avg_win_amount DECIMAL(15,2),
    avg_loss_amount DECIMAL(15,2),
    largest_win DECIMAL(15,2),
    largest_loss DECIMAL(15,2),
    holding_period_avg DECIMAL(8,2), -- 平均持仓天数
    analysis_data JSONB, -- 详细分析数据
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT fk_trade_analysis_account FOREIGN KEY (account_id) REFERENCES trading_accounts(account_id),
    UNIQUE(account_id, analysis_date)
);

-- 策略表现分析表
CREATE TABLE IF NOT EXISTS strategy_performance (
    id SERIAL PRIMARY KEY,
    strategy_id VARCHAR(50) NOT NULL,
    strategy_name VARCHAR(100),
    strategy_type VARCHAR(50), -- 策略类型
    analysis_period VARCHAR(20), -- daily/weekly/monthly
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    total_trades INTEGER DEFAULT 0,
    win_rate DECIMAL(8,4),
    total_return DECIMAL(8,4),
    annualized_return DECIMAL(8,4),
    max_drawdown DECIMAL(8,4),
    volatility DECIMAL(8,4),
    sharpe_ratio DECIMAL(8,4),
    calmar_ratio DECIMAL(8,4),
    performance_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(strategy_id, analysis_period, start_date, end_date)
);

-- ================================
-- 4. Agent学习系统表
-- ================================

-- 市场特征表
CREATE TABLE IF NOT EXISTS market_features (
    id SERIAL PRIMARY KEY,
    feature_date DATE NOT NULL,
    market_index VARCHAR(20) NOT NULL, -- SH000001/SZ399001
    market_trend VARCHAR(20), -- BULL/BEAR/SIDEWAYS
    volatility DECIMAL(8,4),
    volume_ratio DECIMAL(8,4),
    advance_decline_ratio DECIMAL(8,4),
    sector_rotation JSONB, -- 板块轮动数据
    sentiment_score DECIMAL(8,4), -- 市场情绪分数
    technical_indicators JSONB, -- 技术指标
    macro_factors JSONB, -- 宏观因子
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(feature_date, market_index)
);

-- Agent决策记录表
CREATE TABLE IF NOT EXISTS agent_decisions (
    id SERIAL PRIMARY KEY,
    agent_id VARCHAR(50) NOT NULL,
    agent_version VARCHAR(20),
    decision_time TIMESTAMP WITH TIME ZONE NOT NULL,
    stock_code VARCHAR(10) NOT NULL,
    decision_type VARCHAR(20) NOT NULL, -- BUY/SELL/HOLD
    confidence_score DECIMAL(8,4),
    predicted_return DECIMAL(8,4),
    predicted_risk DECIMAL(8,4),
    input_features JSONB, -- 输入特征
    decision_reasoning TEXT, -- 决策理由
    actual_return DECIMAL(8,4), -- 实际收益(事后填入)
    decision_accuracy DECIMAL(8,4), -- 决策准确度
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Agent学习记录表
CREATE TABLE IF NOT EXISTS agent_learning_logs (
    id SERIAL PRIMARY KEY,
    agent_id VARCHAR(50) NOT NULL,
    learning_session_id VARCHAR(50) NOT NULL,
    learning_type VARCHAR(30) NOT NULL, -- TRAINING/VALIDATION/TESTING
    dataset_period_start DATE,
    dataset_period_end DATE,
    model_parameters JSONB,
    training_metrics JSONB, -- 训练指标
    validation_metrics JSONB, -- 验证指标
    feature_importance JSONB, -- 特征重要性
    model_version VARCHAR(20),
    learning_duration INTEGER, -- 学习耗时(秒)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ================================
-- 5. 数据分析视图
-- ================================

-- 每日收益汇总视图
CREATE OR REPLACE VIEW daily_returns AS
SELECT 
    account_id,
    DATE(trade_time) as trade_date,
    SUM(CASE WHEN trade_type = 'SELL' THEN trade_amount - total_fee ELSE -(trade_amount + total_fee) END) as daily_pnl,
    COUNT(*) as trade_count
FROM trading_records
GROUP BY account_id, DATE(trade_time)
ORDER BY account_id, trade_date;

-- 股票表现汇总视图
CREATE OR REPLACE VIEW stock_performance AS
SELECT 
    stock_code,
    DATE(timestamp) as quote_date,
    FIRST_VALUE(close_price) OVER (PARTITION BY stock_code, DATE(timestamp) ORDER BY timestamp) as open_price,
    MAX(high_price) as high_price,
    MIN(low_price) as low_price,
    LAST_VALUE(close_price) OVER (PARTITION BY stock_code, DATE(timestamp) ORDER BY timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) as close_price,
    SUM(volume) as total_volume,
    SUM(turnover) as total_turnover
FROM stock_quotes
GROUP BY stock_code, DATE(timestamp), close_price, timestamp
ORDER BY stock_code, quote_date;

-- ================================
-- 6. 创建索引优化性能
-- ================================

-- 交易记录索引
CREATE INDEX IF NOT EXISTS idx_trading_records_account_time ON trading_records(account_id, trade_time DESC);
CREATE INDEX IF NOT EXISTS idx_trading_records_stock_time ON trading_records(stock_code, trade_time DESC);
CREATE INDEX IF NOT EXISTS idx_trading_records_strategy ON trading_records(strategy_id);

-- 持仓记录索引
CREATE INDEX IF NOT EXISTS idx_positions_account_date ON positions(account_id, position_date DESC);
CREATE INDEX IF NOT EXISTS idx_positions_stock_date ON positions(stock_code, position_date DESC);

-- Agent相关索引
CREATE INDEX IF NOT EXISTS idx_agent_decisions_agent_time ON agent_decisions(agent_id, decision_time DESC);
CREATE INDEX IF NOT EXISTS idx_agent_decisions_stock_time ON agent_decisions(stock_code, decision_time DESC);
CREATE INDEX IF NOT EXISTS idx_market_features_date ON market_features(feature_date DESC);

-- ================================
-- 7. 数据保留策略
-- ================================

-- 创建分区表(按月分区)
-- 注意：需要在Supabase中手动创建分区

COMMENT ON TABLE stocks IS '股票基本信息表';
COMMENT ON TABLE stock_quotes IS '股票实时行情数据表，用于技术分析和回测';
COMMENT ON TABLE trading_records IS '交易记录表，记录所有买卖操作';
COMMENT ON TABLE positions IS '持仓记录表，每日持仓快照';
COMMENT ON TABLE trade_analysis IS '交易复盘分析表，用于策略评估';
COMMENT ON TABLE strategy_performance IS '策略表现分析表';
COMMENT ON TABLE market_features IS '市场特征表，用于机器学习';
COMMENT ON TABLE agent_decisions IS 'Agent决策记录表，用于学习和改进';
COMMENT ON TABLE agent_learning_logs IS 'Agent学习记录表，追踪模型训练过程';
