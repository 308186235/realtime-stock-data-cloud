-- Agent智能交易系统数据库设计
-- 支持历史数据学习和模式识别

-- 1. 股票基础信息表
CREATE TABLE stocks (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) UNIQUE NOT NULL,  -- 股票代码 SH600000
    name VARCHAR(50) NOT NULL,           -- 股票名称
    exchange VARCHAR(10) NOT NULL,       -- 交易所 SH/SZ
    industry VARCHAR(50),                -- 行业分类
    market_cap BIGINT,                   -- 市值
    listing_date DATE,                   -- 上市日期
    is_active BOOLEAN DEFAULT true,      -- 是否活跃
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 2. 实时行情数据表 (分区表，按日期分区)
CREATE TABLE stock_quotes (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    trade_date DATE NOT NULL,
    trade_time TIMESTAMP NOT NULL,
    open_price DECIMAL(10,3),           -- 开盘价
    high_price DECIMAL(10,3),           -- 最高价
    low_price DECIMAL(10,3),            -- 最低价
    close_price DECIMAL(10,3),          -- 收盘价/现价
    volume BIGINT,                      -- 成交量
    amount DECIMAL(15,2),               -- 成交额
    change_percent DECIMAL(8,4),        -- 涨跌幅
    turnover_rate DECIMAL(8,4),         -- 换手率
    created_at TIMESTAMP DEFAULT NOW()
) PARTITION BY RANGE (trade_date);

-- 创建分区表 (按月分区)
CREATE TABLE stock_quotes_2025_01 PARTITION OF stock_quotes
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');
CREATE TABLE stock_quotes_2025_02 PARTITION OF stock_quotes
    FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');

-- 3. 日K线数据表
CREATE TABLE daily_klines (
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
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(symbol, trade_date)
);

-- 4. Agent决策记录表
CREATE TABLE agent_decisions (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    decision_time TIMESTAMP NOT NULL,
    action VARCHAR(10) NOT NULL,        -- BUY/SELL/HOLD
    price DECIMAL(10,3) NOT NULL,       -- 决策时价格
    confidence DECIMAL(5,2) NOT NULL,   -- 信心度 0-100
    reason TEXT,                        -- 决策理由
    technical_score DECIMAL(5,2),       -- 技术面评分
    fundamental_score DECIMAL(5,2),     -- 基本面评分
    market_sentiment DECIMAL(5,2),      -- 市场情绪评分
    -- 决策依据的技术指标
    ma_signal VARCHAR(20),              -- 均线信号
    macd_signal VARCHAR(20),            -- MACD信号
    rsi_signal VARCHAR(20),             -- RSI信号
    volume_signal VARCHAR(20),          -- 成交量信号
    created_at TIMESTAMP DEFAULT NOW()
);

-- 5. Agent学习样本表
CREATE TABLE agent_learning_samples (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    sample_date DATE NOT NULL,
    -- 输入特征 (前N天的数据)
    features JSONB NOT NULL,            -- 技术指标特征向量
    -- 输出标签 (后续N天的收益率)
    label_1d DECIMAL(8,4),              -- 1天后收益率
    label_3d DECIMAL(8,4),              -- 3天后收益率
    label_5d DECIMAL(8,4),              -- 5天后收益率
    label_10d DECIMAL(8,4),             -- 10天后收益率
    -- 分类标签
    trend_1d VARCHAR(10),               -- 1天趋势 UP/DOWN/FLAT
    trend_3d VARCHAR(10),               -- 3天趋势
    trend_5d VARCHAR(10),               -- 5天趋势
    created_at TIMESTAMP DEFAULT NOW()
);

-- 6. Agent策略回测表
CREATE TABLE agent_backtests (
    id BIGSERIAL PRIMARY KEY,
    strategy_name VARCHAR(100) NOT NULL,
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
    config JSONB,                        -- 策略配置
    created_at TIMESTAMP DEFAULT NOW()
);

-- 7. Agent交易记录表
CREATE TABLE agent_trades (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    action VARCHAR(10) NOT NULL,        -- BUY/SELL
    quantity INTEGER NOT NULL,          -- 交易数量
    price DECIMAL(10,3) NOT NULL,       -- 交易价格
    amount DECIMAL(15,2) NOT NULL,      -- 交易金额
    trade_time TIMESTAMP NOT NULL,
    decision_id BIGINT REFERENCES agent_decisions(id),
    commission DECIMAL(10,2),           -- 手续费
    status VARCHAR(20) DEFAULT 'PENDING', -- PENDING/FILLED/CANCELLED
    created_at TIMESTAMP DEFAULT NOW()
);

-- 8. 市场情绪指标表
CREATE TABLE market_sentiment (
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
    created_at TIMESTAMP DEFAULT NOW()
);

-- 创建索引优化查询性能
CREATE INDEX idx_stock_quotes_symbol_time ON stock_quotes(symbol, trade_time);
CREATE INDEX idx_daily_klines_symbol_date ON daily_klines(symbol, trade_date);
CREATE INDEX idx_agent_decisions_symbol_time ON agent_decisions(symbol, decision_time);
CREATE INDEX idx_agent_decisions_action ON agent_decisions(action);
CREATE INDEX idx_agent_learning_samples_symbol_date ON agent_learning_samples(symbol, sample_date);
CREATE INDEX idx_agent_trades_symbol_time ON agent_trades(symbol, trade_time);
CREATE INDEX idx_market_sentiment_date ON market_sentiment(trade_date);

-- 创建视图简化查询
CREATE VIEW v_latest_quotes AS
SELECT DISTINCT ON (symbol) 
    symbol, trade_time, close_price, change_percent, volume, amount
FROM stock_quotes 
ORDER BY symbol, trade_time DESC;

CREATE VIEW v_agent_performance AS
SELECT 
    DATE(decision_time) as trade_date,
    action,
    COUNT(*) as decision_count,
    AVG(confidence) as avg_confidence,
    COUNT(CASE WHEN at.status = 'FILLED' THEN 1 END) as executed_count
FROM agent_decisions ad
LEFT JOIN agent_trades at ON ad.id = at.decision_id
GROUP BY DATE(decision_time), action
ORDER BY trade_date DESC;
