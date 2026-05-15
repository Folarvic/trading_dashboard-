from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
import json
from datetime import datetime
import redis
import os

# Import our modules
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_fetcher import LiveDataFetcher
from signal_engine import EnsembleSignalEngine
from risk_manager import PortfolioRiskManager

app = FastAPI(title="AI Trading Dashboard API", version="1.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔑 THIS IS THE FIX: Mount static files
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# 🔑 THIS IS THE FIX: Serve HTML at root
@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    try:
        with open("frontend/templates/index.html", "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Dashboard loading...</h1>")

# Keep your existing API routes...
@app.get("/api/portfolio/latest")
async def get_latest_portfolio():

# Redis cache
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# Global state
fetcher = LiveDataFetcher()
signal_engine = EnsembleSignalEngine()
risk_manager = PortfolioRiskManager(portfolio_value=100000)

class PortfolioSnapshot(BaseModel):
    timestamp: str
    prices: Dict
    signals: Dict
    positions: Dict
    portfolio_risk: Dict

@app.get("/")
async def root():
    return {"status": "AI Trading Dashboard API", "version": "1.0"}

@app.get("/api/portfolio/latest")
async def get_latest_portfolio():
    """Get latest portfolio snapshot"""
    try:
        cached = redis_client.get('latest_portfolio')
        if cached:
            return json.loads(cached)

        # Fetch fresh data
        prices = fetcher.fetch_prices()

        # Fetch historical for each asset
        historical = {}
        for asset in prices:
            if prices[asset]:
                historical[asset] = fetcher.fetch_historical(asset)

        # Generate signals
        signals = signal_engine.generate_signals(prices, historical)

        # Calculate positions
        weights = risk_manager.calculate_optimal_weights(signals, historical)
        positions = risk_manager.calculate_positions(weights)

        # Check portfolio risk
        portfolio_risk = risk_manager.check_portfolio_risk(positions)

        snapshot = {
            'timestamp': datetime.utcnow().isoformat(),
            'prices': prices,
            'signals': signals,
            'positions': positions,
            'portfolio_risk': portfolio_risk,
            'portfolio_value': risk_manager.portfolio_value
        }

        # Cache for 5 minutes
        redis_client.setex('latest_portfolio', 300, json.dumps(snapshot))

        return snapshot

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/prices")
async def get_prices():
    """Get current prices only"""
    prices = fetcher.fetch_prices()
    return {'prices': prices, 'timestamp': datetime.utcnow().isoformat()}

@app.get("/api/signals")
async def get_signals():
    """Get current signals only"""
    prices = fetcher.fetch_prices()
    historical = {asset: fetcher.fetch_historical(asset) for asset in prices if prices[asset]}
    signals = signal_engine.generate_signals(prices, historical)
    return {'signals': signals, 'timestamp': datetime.utcnow().isoformat()}

@app.get("/api/assets/{asset}")
async def get_asset_detail(asset: str):
    """Get detailed info for specific asset"""
    hist = fetcher.fetch_historical(asset, period='6mo')
    if hist is None or hist.empty:
        raise HTTPException(status_code=404, detail=f"Asset {asset} not found")

    from technical_indicators import TechnicalIndicators
    hist = TechnicalIndicators.calculate_all(hist)

    latest = hist.iloc[-1]
    return {
        'asset': asset,
        'price': round(latest['Close'], 4),
        'rsi': round(latest['RSI'], 1) if not pd.isna(latest['RSI']) else None,
        'macd': round(latest['MACD'], 4) if not pd.isna(latest['MACD']) else None,
        'bb_upper': round(latest['BB_Upper'], 4) if not pd.isna(latest['BB_Upper']) else None,
        'bb_lower': round(latest['BB_Lower'], 4) if not pd.isna(latest['BB_Lower']) else None,
        'atr': round(latest['ATR'], 4) if not pd.isna(latest['ATR']) else None,
        'sma_20': round(latest['SMA_20'], 4) if not pd.isna(latest['SMA_20']) else None,
        'sma_50': round(latest['SMA_50'], 4) if not pd.isna(latest['SMA_50']) else None,
    }

@app.get("/api/history")
async def get_portfolio_history(hours: int = 24):
    """Get portfolio history from database"""
    # This would query PostgreSQL
    # Placeholder return
    return {'history': [], 'hours': hours}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
