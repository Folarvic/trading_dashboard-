from celery import Celery
from celery.schedules import crontab
from datetime import datetime
import json
import redis
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_fetcher import LiveDataFetcher
from signal_engine import EnsembleSignalEngine
from risk_manager import PortfolioRiskManager

# Celery app
app = Celery('trading_dashboard')
app.conf.update(
    broker_url='redis://localhost:6379/0',
    result_backend='redis://localhost:6379/0',
    timezone='UTC',
    enable_utc=True,
)

# Redis client
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# Initialize components
fetcher = LiveDataFetcher()
signal_engine = EnsembleSignalEngine()
risk_manager = PortfolioRiskManager(portfolio_value=100000)

@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    """Schedule tasks"""
    # Every 15 minutes during market hours
    sender.add_periodic_task(
        900.0,  # 15 minutes in seconds
        update_portfolio.s(),
        name='portfolio_update_15min'
    )

    # Every minute during high volatility (can be enabled manually)
    # sender.add_periodic_task(60.0, update_portfolio.s(), name='high_freq')

@app.task
def update_portfolio():
    """Main task: fetch data, generate signals, save to cache"""
    print(f"[{datetime.utcnow()}] Updating portfolio...")

    try:
        # 1. Fetch prices
        prices = fetcher.fetch_prices()

        # 2. Fetch historical
        historical = {}
        for asset in prices:
            if prices[asset]:
                historical[asset] = fetcher.fetch_historical(asset)

        # 3. Generate signals
        signals = signal_engine.generate_signals(prices, historical)

        # 4. Calculate positions
        weights = risk_manager.calculate_optimal_weights(signals, historical)
        positions = risk_manager.calculate_positions(weights)

        # 5. Check risk
        portfolio_risk = risk_manager.check_portfolio_risk(positions)

        # 6. Build snapshot
        snapshot = {
            'timestamp': datetime.utcnow().isoformat(),
            'prices': prices,
            'signals': signals,
            'positions': positions,
            'portfolio_risk': portfolio_risk,
            'portfolio_value': risk_manager.portfolio_value
        }

        # 7. Save to Redis cache
        redis_client.setex('latest_portfolio', 900, json.dumps(snapshot))

        # 8. Save to database (optional)
        # save_to_database(snapshot)

        print(f"[{datetime.utcnow()}] Portfolio updated successfully!")
        return snapshot

    except Exception as e:
        print(f"[{datetime.utcnow()}] ERROR: {e}")
        return {'error': str(e)}

@app.task
def fetch_news_sentiment():
    """Fetch and analyze news sentiment"""
    # Integrate with NewsAPI or similar
    print(f"[{datetime.utcnow()}] Fetching news...")
    return {'status': 'completed'}

# Beat schedule (alternative to on_after_configure)
app.conf.beat_schedule = {
    'portfolio-update-15min': {
        'task': 'scheduler.update_portfolio',
        'schedule': 900.0,  # 15 minutes
    },
}
