"""
AI Trading Dashboard Configuration
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Portfolio Settings
PORTFOLIO_VALUE = float(os.getenv('PORTFOLIO_VALUE', 100000))
MAX_DAILY_RISK = float(os.getenv('MAX_DAILY_RISK', 0.02))
MAX_POSITION_SIZE = float(os.getenv('MAX_POSITION_SIZE', 0.25))
MIN_POSITION_SIZE = float(os.getenv('MIN_POSITION_SIZE', 0.05))

# Risk Management
STOP_LOSS_ATR_MULTIPLIER = float(os.getenv('STOP_LOSS_ATR_MULTIPLIER', 2.0))
TAKE_PROFIT_ATR_MULTIPLIER = float(os.getenv('TAKE_PROFIT_ATR_MULTIPLIER', 3.0))
TRAILING_STOP_ATR_MULTIPLIER = float(os.getenv('TRAILING_STOP_ATR_MULTIPLIER', 1.0))

# Update Intervals
UPDATE_INTERVAL_SECONDS = int(os.getenv('UPDATE_INTERVAL_SECONDS', 900))  # 15 minutes
HIGH_VOLATILITY_INTERVAL = int(os.getenv('HIGH_VOLATILITY_INTERVAL', 60))  # 1 minute

# Data Sources
YAHOO_FINANCE_ENABLED = os.getenv('YAHOO_FINANCE_ENABLED', 'true').lower() == 'true'
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY', '')
NEWSAPI_KEY = os.getenv('NEWSAPI_KEY', '')

# Database
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://user:pass@localhost/trading')
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

# API
API_HOST = os.getenv('API_HOST', '0.0.0.0')
API_PORT = int(os.getenv('API_PORT', 8000))
CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')

# Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'logs/trading.log')

# Assets Configuration
ASSETS = {
    'EURUSD': {'ticker': 'EURUSD=X', 'type': 'forex', 'pip_value': 0.0001},
    'GBPUSD': {'ticker': 'GBPUSD=X', 'type': 'forex', 'pip_value': 0.0001},
    'USDJPY': {'ticker': 'USDJPY=X', 'type': 'forex', 'pip_value': 0.01},
    'AUDUSD': {'ticker': 'AUDUSD=X', 'type': 'forex', 'pip_value': 0.0001},
    'USDCAD': {'ticker': 'USDCAD=X', 'type': 'forex', 'pip_value': 0.0001},
    'XAUUSD': {'ticker': 'GC=F', 'type': 'commodity', 'pip_value': 0.1},
    'US30': {'ticker': '^DJI', 'type': 'index', 'pip_value': 1.0},
}

# ML Model Weights
MODEL_WEIGHTS = {
    'lstm': 0.30,
    'xgboost': 0.25,
    'transformer': 0.25,
    'garch': 0.20
}

# Signal Thresholds
SIGNAL_THRESHOLDS = {
    'strong_buy': 0.5,
    'buy': 0.2,
    'hold': -0.2,
    'sell': -0.5
}
