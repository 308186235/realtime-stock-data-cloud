-- 茶股帮股票数据表结构
-- 在Supabase中创建用于存储茶股帮实时股票数据的表

-- 1. 创建股票实时数据表
CREATE TABLE IF NOT EXISTS stock_realtime (
    id BIGSERIAL PRIMARY KEY,
    stock_code VARCHAR(10) NOT NULL,
    stock_name VARCHAR(100),
    last_price DECIMAL(10,3),
    open_price DECIMAL(10,3),
    high_price DECIMAL(10,3),
    low_price DECIMAL(10,3),
    volume BIGINT,
    amount DECIMAL(15,2),
    last_close DECIMAL(10,3),
    change_pct DECIMAL(8,3),
    market VARCHAR(10),
    data_source VARCHAR(20) DEFAULT 'chagubang',
    update_time TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- 索引
    UNIQUE(stock_code)
);

-- 2. 创建索引
CREATE INDEX IF NOT EXISTS idx_stock_realtime_code ON stock_realtime(stock_code);
CREATE INDEX IF NOT EXISTS idx_stock_realtime_change_pct ON stock_realtime(change_pct DESC);
CREATE INDEX IF NOT EXISTS idx_stock_realtime_volume ON stock_realtime(volume DESC);
CREATE INDEX IF NOT EXISTS idx_stock_realtime_amount ON stock_realtime(amount DESC);
CREATE INDEX IF NOT EXISTS idx_stock_realtime_update_time ON stock_realtime(update_time DESC);
CREATE INDEX IF NOT EXISTS idx_stock_realtime_market ON stock_realtime(market);

-- 3. 创建茶股帮Token管理表
CREATE TABLE IF NOT EXISTS chagubang_tokens (
    id BIGSERIAL PRIMARY KEY,
    token_value VARCHAR(500) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    is_valid BOOLEAN DEFAULT false,
    last_test_time TIMESTAMP WITH TIME ZONE,
    test_result TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(token_value)
);

-- 4. 创建数据同步日志表
CREATE TABLE IF NOT EXISTS chagubang_sync_log (
    id BIGSERIAL PRIMARY KEY,
    sync_time TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    records_processed INTEGER DEFAULT 0,
    records_success INTEGER DEFAULT 0,
    records_failed INTEGER DEFAULT 0,
    sync_duration_ms INTEGER,
    error_message TEXT,
    token_used VARCHAR(100),
    status VARCHAR(20) DEFAULT 'running' -- running, success, failed
);

-- 5. 创建市场统计表
CREATE TABLE IF NOT EXISTS market_statistics (
    id BIGSERIAL PRIMARY KEY,
    stat_date DATE DEFAULT CURRENT_DATE,
    total_stocks INTEGER DEFAULT 0,
    rising_stocks INTEGER DEFAULT 0,
    falling_stocks INTEGER DEFAULT 0,
    flat_stocks INTEGER DEFAULT 0,
    avg_price DECIMAL(10,3),
    avg_change_pct DECIMAL(8,3),
    total_volume BIGINT DEFAULT 0,
    total_amount DECIMAL(20,2) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(stat_date)
);

-- 6. 创建热门股票视图
CREATE OR REPLACE VIEW hot_stocks_by_change AS
SELECT 
    stock_code,
    stock_name,
    last_price,
    change_pct,
    volume,
    amount,
    market,
    update_time,
    ABS(change_pct) as abs_change
FROM stock_realtime 
WHERE last_price > 0 
ORDER BY abs_change DESC, volume DESC
LIMIT 50;

-- 7. 创建热门股票按成交量视图
CREATE OR REPLACE VIEW hot_stocks_by_volume AS
SELECT 
    stock_code,
    stock_name,
    last_price,
    change_pct,
    volume,
    amount,
    market,
    update_time
FROM stock_realtime 
WHERE volume > 0 
ORDER BY volume DESC
LIMIT 50;

-- 8. 创建市场概览视图
CREATE OR REPLACE VIEW market_overview AS
SELECT 
    COUNT(*) as total_stocks,
    AVG(last_price) as avg_price,
    AVG(change_pct) as avg_change,
    COUNT(CASE WHEN change_pct > 0 THEN 1 END) as rising_stocks,
    COUNT(CASE WHEN change_pct < 0 THEN 1 END) as falling_stocks,
    COUNT(CASE WHEN change_pct = 0 THEN 1 END) as flat_stocks,
    SUM(volume) as total_volume,
    SUM(amount) as total_amount,
    MAX(update_time) as last_update
FROM stock_realtime 
WHERE last_price > 0;

-- 9. 创建触发器函数：更新时间戳
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 10. 创建触发器：自动更新updated_at
CREATE TRIGGER update_chagubang_tokens_updated_at 
    BEFORE UPDATE ON chagubang_tokens 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- 11. 创建函数：插入或更新股票数据
CREATE OR REPLACE FUNCTION upsert_stock_data(
    p_stock_code VARCHAR(10),
    p_stock_name VARCHAR(100),
    p_last_price DECIMAL(10,3),
    p_open_price DECIMAL(10,3),
    p_high_price DECIMAL(10,3),
    p_low_price DECIMAL(10,3),
    p_volume BIGINT,
    p_amount DECIMAL(15,2),
    p_last_close DECIMAL(10,3),
    p_change_pct DECIMAL(8,3),
    p_market VARCHAR(10)
)
RETURNS VOID AS $$
BEGIN
    INSERT INTO stock_realtime (
        stock_code, stock_name, last_price, open_price, high_price, 
        low_price, volume, amount, last_close, change_pct, market
    ) VALUES (
        p_stock_code, p_stock_name, p_last_price, p_open_price, p_high_price,
        p_low_price, p_volume, p_amount, p_last_close, p_change_pct, p_market
    )
    ON CONFLICT (stock_code) 
    DO UPDATE SET
        stock_name = EXCLUDED.stock_name,
        last_price = EXCLUDED.last_price,
        open_price = EXCLUDED.open_price,
        high_price = EXCLUDED.high_price,
        low_price = EXCLUDED.low_price,
        volume = EXCLUDED.volume,
        amount = EXCLUDED.amount,
        last_close = EXCLUDED.last_close,
        change_pct = EXCLUDED.change_pct,
        market = EXCLUDED.market,
        update_time = NOW();
END;
$$ LANGUAGE plpgsql;

-- 12. 创建函数：批量插入股票数据
CREATE OR REPLACE FUNCTION batch_upsert_stock_data(stock_data JSONB)
RETURNS INTEGER AS $$
DECLARE
    stock_record JSONB;
    processed_count INTEGER := 0;
BEGIN
    FOR stock_record IN SELECT * FROM jsonb_array_elements(stock_data)
    LOOP
        PERFORM upsert_stock_data(
            (stock_record->>'stock_code')::VARCHAR(10),
            (stock_record->>'stock_name')::VARCHAR(100),
            (stock_record->>'last_price')::DECIMAL(10,3),
            (stock_record->>'open_price')::DECIMAL(10,3),
            (stock_record->>'high_price')::DECIMAL(10,3),
            (stock_record->>'low_price')::DECIMAL(10,3),
            (stock_record->>'volume')::BIGINT,
            (stock_record->>'amount')::DECIMAL(15,2),
            (stock_record->>'last_close')::DECIMAL(10,3),
            (stock_record->>'change_pct')::DECIMAL(8,3),
            (stock_record->>'market')::VARCHAR(10)
        );
        processed_count := processed_count + 1;
    END LOOP;
    
    RETURN processed_count;
END;
$$ LANGUAGE plpgsql;

-- 13. 创建RLS策略（行级安全）
ALTER TABLE stock_realtime ENABLE ROW LEVEL SECURITY;
ALTER TABLE chagubang_tokens ENABLE ROW LEVEL SECURITY;
ALTER TABLE chagubang_sync_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE market_statistics ENABLE ROW LEVEL SECURITY;

-- 14. 创建公开读取策略
CREATE POLICY "Allow public read access on stock_realtime" 
    ON stock_realtime FOR SELECT 
    USING (true);

CREATE POLICY "Allow public read access on market_statistics" 
    ON market_statistics FOR SELECT 
    USING (true);

-- 15. 创建服务角色写入策略
CREATE POLICY "Allow service role write access on stock_realtime" 
    ON stock_realtime FOR ALL 
    USING (auth.role() = 'service_role');

CREATE POLICY "Allow service role write access on chagubang_tokens" 
    ON chagubang_tokens FOR ALL 
    USING (auth.role() = 'service_role');

CREATE POLICY "Allow service role write access on chagubang_sync_log" 
    ON chagubang_sync_log FOR ALL 
    USING (auth.role() = 'service_role');

CREATE POLICY "Allow service role write access on market_statistics" 
    ON market_statistics FOR ALL 
    USING (auth.role() = 'service_role');

-- 16. 插入示例数据
INSERT INTO chagubang_tokens (token_value, description, is_active) 
VALUES ('demo_token_for_testing', '演示Token', false)
ON CONFLICT (token_value) DO NOTHING;

-- 17. 创建清理旧数据的函数
CREATE OR REPLACE FUNCTION cleanup_old_sync_logs()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM chagubang_sync_log 
    WHERE sync_time < NOW() - INTERVAL '7 days';
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- 完成提示
SELECT 'Chagubang database schema created successfully!' as status;
