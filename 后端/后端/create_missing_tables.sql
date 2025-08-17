-- 创建缺失的数据库表
-- 在Supabase SQL编辑器中执行

-- 1. 创建股票推送日志表
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

-- 2. 创建实时股票数据表
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

-- 3. 创建数据质量监控表
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

-- 4. 创建系统健康监控表
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

-- 5. 插入一些测试数据到stock_push_logs表
INSERT INTO stock_push_logs (symbol, price, volume, push_timestamp, api_key_used, processed) VALUES
('sz000001', 12.30, 1000000, NOW(), 'QT_wat5QfcJ6N9pDZM5', true),
('sh600519', 1405.10, 500000, NOW(), 'QT_wat5QfcJ6N9pDZM5', true),
('sz300750', 251.50, 800000, NOW(), 'QT_wat5QfcJ6N9pDZM5', true);

-- 6. 插入一些测试数据到real_time_stock_data表
INSERT INTO real_time_stock_data (
    symbol, stock_name, current_price, volume, data_source, 
    data_quality_score, market_status, data_timestamp
) VALUES
('sz000001', '平安银行', 12.30, 1000000, 'realtime-stock-api', 100, 'trading', NOW()),
('sh600519', '贵州茅台', 1405.10, 500000, 'realtime-stock-api', 100, 'trading', NOW()),
('sz300750', '宁德时代', 251.50, 800000, 'realtime-stock-api', 100, 'trading', NOW());

-- 7. 验证表创建
SELECT 'stock_push_logs' as table_name, COUNT(*) as record_count FROM stock_push_logs
UNION ALL
SELECT 'real_time_stock_data' as table_name, COUNT(*) as record_count FROM real_time_stock_data
UNION ALL
SELECT 'data_quality_monitor' as table_name, COUNT(*) as record_count FROM data_quality_monitor
UNION ALL
SELECT 'system_health_monitor' as table_name, COUNT(*) as record_count FROM system_health_monitor;
