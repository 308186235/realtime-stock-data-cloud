-- 创建实时股票数据表
CREATE TABLE IF NOT EXISTS real_time_stock_data (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    stock_name VARCHAR(100),
    current_price DECIMAL(10,3),
    yesterday_close DECIMAL(10,3),
    today_open DECIMAL(10,3),
    high_price DECIMAL(10,3),
    low_price DECIMAL(10,3),
    volume BIGINT,
    amount BIGINT,
    turnover_rate DECIMAL(5,2),
    pe_ratio DECIMAL(8,2),
    pb_ratio DECIMAL(8,2),
    market_cap DECIMAL(15,2),
    change_amount DECIMAL(10,3),
    change_percent DECIMAL(5,2),
    bid_price_1 DECIMAL(10,3),
    bid_price_2 DECIMAL(10,3),
    bid_price_3 DECIMAL(10,3),
    bid_price_4 DECIMAL(10,3),
    bid_price_5 DECIMAL(10,3),
    ask_price_1 DECIMAL(10,3),
    ask_price_2 DECIMAL(10,3),
    ask_price_3 DECIMAL(10,3),
    ask_price_4 DECIMAL(10,3),
    ask_price_5 DECIMAL(10,3),
    bid_volume_1 INTEGER,
    bid_volume_2 INTEGER,
    bid_volume_3 INTEGER,
    bid_volume_4 INTEGER,
    bid_volume_5 INTEGER,
    ask_volume_1 INTEGER,
    ask_volume_2 INTEGER,
    ask_volume_3 INTEGER,
    ask_volume_4 INTEGER,
    ask_volume_5 INTEGER,
    amplitude DECIMAL(5,2),
    volume_ratio DECIMAL(5,2),
    limit_up DECIMAL(10,3),
    limit_down DECIMAL(10,3),
    data_source VARCHAR(50),
    data_quality_score INTEGER,
    market_status VARCHAR(20),
    trading_date DATE,
    data_timestamp TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_real_time_stock_symbol ON real_time_stock_data(symbol);
CREATE INDEX IF NOT EXISTS idx_real_time_stock_timestamp ON real_time_stock_data(data_timestamp);
CREATE INDEX IF NOT EXISTS idx_real_time_stock_created ON real_time_stock_data(created_at);

-- 创建股票推送日志表
CREATE TABLE IF NOT EXISTS stock_push_logs (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    price DECIMAL(10,3),
    volume BIGINT,
    push_timestamp TIMESTAMP,
    received_at TIMESTAMP DEFAULT NOW(),
    api_key_used VARCHAR(50),
    batch_id INTEGER,
    file_path VARCHAR(255),
    processed BOOLEAN DEFAULT FALSE,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_push_logs_symbol ON stock_push_logs(symbol);
CREATE INDEX IF NOT EXISTS idx_push_logs_timestamp ON stock_push_logs(push_timestamp);
CREATE INDEX IF NOT EXISTS idx_push_logs_processed ON stock_push_logs(processed);

-- 更新stocks表结构
ALTER TABLE stocks ADD COLUMN IF NOT EXISTS stock_code VARCHAR(20);
ALTER TABLE stocks ADD COLUMN IF NOT EXISTS stock_name VARCHAR(100);
ALTER TABLE stocks ADD COLUMN IF NOT EXISTS market VARCHAR(10);
ALTER TABLE stocks ADD COLUMN IF NOT EXISTS sector VARCHAR(50);
ALTER TABLE stocks ADD COLUMN IF NOT EXISTS industry VARCHAR(50);
ALTER TABLE stocks ADD COLUMN IF NOT EXISTS listing_date DATE;
ALTER TABLE stocks ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;
ALTER TABLE stocks ADD COLUMN IF NOT EXISTS last_updated TIMESTAMP DEFAULT NOW();

-- 创建数据质量监控表
CREATE TABLE IF NOT EXISTS data_quality_monitor (
    id SERIAL PRIMARY KEY,
    check_type VARCHAR(50) NOT NULL,
    check_result JSONB,
    issues_found INTEGER DEFAULT 0,
    critical_issues INTEGER DEFAULT 0,
    overall_score INTEGER,
    recommendations TEXT[],
    check_timestamp TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

-- 创建系统健康监控表
CREATE TABLE IF NOT EXISTS system_health_monitor (
    id SERIAL PRIMARY KEY,
    component VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    metrics JSONB,
    error_count INTEGER DEFAULT 0,
    last_error TEXT,
    uptime_seconds INTEGER,
    check_timestamp TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

-- 插入基础股票数据
INSERT INTO stocks (stock_code, stock_name, market, sector, is_active) VALUES
('sz000001', '平安银行', 'SZSE', '金融', TRUE),
('sz000002', '万科A', 'SZSE', '房地产', TRUE),
('sh600000', '浦发银行', 'SSE', '金融', TRUE),
('sh600036', '招商银行', 'SSE', '金融', TRUE),
('sh600519', '贵州茅台', 'SSE', '食品饮料', TRUE),
('sz002415', '海康威视', 'SZSE', '科技', TRUE),
('sz300750', '宁德时代', 'SZSE', '新能源', TRUE),
('sh688599', '天合光能', 'SSE', '新能源', TRUE),
('sh601318', '中国平安', 'SSE', '金融', TRUE),
('bj430047', '诺思兰德', 'BSE', '医药', TRUE)
ON CONFLICT (stock_code) DO NOTHING;
