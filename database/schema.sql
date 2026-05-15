-- AI Trading Dashboard Database Schema

-- Portfolio snapshots (main table)
CREATE TABLE IF NOT EXISTS portfolio_snapshots (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    portfolio_value DECIMAL(12,2) NOT NULL DEFAULT 100000.00,
    daily_pnl DECIMAL(12,2) DEFAULT 0.00,
    total_return_pct DECIMAL(5,2) DEFAULT 0.00,
    max_drawdown_pct DECIMAL(5,2) DEFAULT 0.00,
    portfolio_risk_pct DECIMAL(5,2) DEFAULT 0.00,
    num_positions INTEGER DEFAULT 0,
    market_regime VARCHAR(20) DEFAULT 'neutral'
);

-- Asset snapshots (per-asset data)
CREATE TABLE IF NOT EXISTS asset_snapshots (
    id SERIAL PRIMARY KEY,
    snapshot_id INTEGER REFERENCES portfolio_snapshots(id) ON DELETE CASCADE,
    asset VARCHAR(10) NOT NULL,
    price DECIMAL(12,4) NOT NULL,
    open_price DECIMAL(12,4),
    high_price DECIMAL(12,4),
    low_price DECIMAL(12,4),
    volume BIGINT,
    signal_score DECIMAL(5,3),
    lstm_signal DECIMAL(5,3),
    xgboost_signal DECIMAL(5,3),
    transformer_signal DECIMAL(5,3),
    garch_signal DECIMAL(5,3),
    rsi DECIMAL(5,2),
    macd DECIMAL(10,4),
    atr DECIMAL(10,4),
    weight DECIMAL(5,4),
    position_value DECIMAL(12,2),
    stop_loss DECIMAL(12,4),
    take_profit DECIMAL(12,4),
    direction VARCHAR(10),
    unrealized_pnl DECIMAL(12,2) DEFAULT 0.00
);

-- Trade history (executed trades)
CREATE TABLE IF NOT EXISTS trades (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    asset VARCHAR(10) NOT NULL,
    action VARCHAR(20) NOT NULL,  -- BUY, SELL, CLOSE
    direction VARCHAR(10),  -- LONG, SHORT
    entry_price DECIMAL(12,4) NOT NULL,
    exit_price DECIMAL(12,4),
    quantity DECIMAL(12,4) NOT NULL,
    stop_loss DECIMAL(12,4),
    take_profit DECIMAL(12,4),
    realized_pnl DECIMAL(12,2),
    pnl_pct DECIMAL(5,2),
    status VARCHAR(20) DEFAULT 'OPEN',  -- OPEN, CLOSED, STOPPED
    close_reason VARCHAR(50)  -- TP, SL, MANUAL, SIGNAL
);

-- Economic calendar events
CREATE TABLE IF NOT EXISTS economic_events (
    id SERIAL PRIMARY KEY,
    event_date DATE NOT NULL,
    event_time TIME,
    currency VARCHAR(3),
    event_name VARCHAR(100) NOT NULL,
    impact VARCHAR(10),  -- LOW, MEDIUM, HIGH
    actual_value DECIMAL(10,4),
    forecast_value DECIMAL(10,4),
    previous_value DECIMAL(10,4),
    status VARCHAR(20) DEFAULT 'UPCOMING'  -- UPCOMING, RELEASED
);

-- Performance metrics (daily)
CREATE TABLE IF NOT EXISTS performance_metrics (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL UNIQUE,
    starting_value DECIMAL(12,2),
    ending_value DECIMAL(12,2),
    daily_return_pct DECIMAL(5,2),
    benchmark_return_pct DECIMAL(5,2),
    sharpe_ratio DECIMAL(5,2),
    sortino_ratio DECIMAL(5,2),
    max_drawdown_pct DECIMAL(5,2),
    win_rate_pct DECIMAL(5,2),
    profit_factor DECIMAL(5,2),
    num_trades INTEGER,
    avg_trade_return DECIMAL(5,2)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_snapshots_timestamp ON portfolio_snapshots(timestamp);
CREATE INDEX IF NOT EXISTS idx_asset_snapshots_asset ON asset_snapshots(asset);
CREATE INDEX IF NOT EXISTS idx_asset_snapshots_snapshot ON asset_snapshots(snapshot_id);
CREATE INDEX IF NOT EXISTS idx_trades_timestamp ON trades(timestamp);
CREATE INDEX IF NOT EXISTS idx_trades_asset ON trades(asset);
CREATE INDEX IF NOT EXISTS idx_events_date ON economic_events(event_date);

-- Views for quick analytics
CREATE OR REPLACE VIEW daily_performance AS
SELECT 
    DATE(timestamp) as date,
    COUNT(*) as updates,
    AVG(portfolio_value) as avg_value,
    MAX(portfolio_value) as max_value,
    MIN(portfolio_value) as min_value,
    MAX(max_drawdown_pct) as max_drawdown
FROM portfolio_snapshots
GROUP BY DATE(timestamp)
ORDER BY date DESC;

CREATE OR REPLACE VIEW asset_performance AS
SELECT 
    asset,
    COUNT(*) as signals_generated,
    AVG(signal_score) as avg_signal,
    AVG(unrealized_pnl) as avg_pnl,
    SUM(CASE WHEN unrealized_pnl > 0 THEN 1 ELSE 0 END) as winning_signals,
    SUM(CASE WHEN unrealized_pnl < 0 THEN 1 ELSE 0 END) as losing_signals
FROM asset_snapshots
GROUP BY asset;
