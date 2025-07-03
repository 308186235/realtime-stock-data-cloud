-- 创建交易配置表
CREATE TABLE IF NOT EXISTS trading_config (
    id SERIAL PRIMARY KEY,
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value TEXT NOT NULL,
    description TEXT,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 插入默认配置
INSERT INTO trading_config (config_key, config_value, description) VALUES
('enable_beijing_exchange', 'false', '北交所交易权限开关'),
('trading_start_time', '09:10', '交易开始时间'),
('trading_end_time', '15:00', '交易结束时间'),
('analysis_interval', '40', 'Agent分析间隔(秒)'),
('reconnect_interval', '30', '重连间隔(秒)'),
('max_reconnect_attempts', '10', '最大重连次数')
ON CONFLICT (config_key) DO UPDATE SET
    config_value = EXCLUDED.config_value,
    updated_at = NOW();

-- 查询配置
SELECT * FROM trading_config ORDER BY config_key;
