from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Dict
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

# Mount static files (CSS, JS)
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# Redis cache
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    db=0,
    decode_responses=True
)

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

# ============================================================
# FRONTEND ROUTE — SERVES THE DASHBOARD HTML
# ============================================================

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    """Serve the main dashboard HTML at root path /"""
    try:
        with open("frontend/templates/index.html", "r") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html>
        <head><title>AI Trading Dashboard</title></head>
        <body style="background:#0f0f23;color:white;font-family:monospace;padding:40px;">
            <h1>🤖 AI Trading Dashboard</h1>
            <p>Dashboard template not found.</p>
            <p>API is running at <a href="/api" style="color:#00FF7F;">/api</a></p>
            <p>Make sure frontend/templates/index.html exists in your repo.</p>
        </body>
        </html>
        """)

# ============================================================
# API ROUTES — SERVE JSON DATA
# ============================================================

@app.get("/api")
async def api_root():
    """API info endpoint"""
    return {
        "status": "AI Trading Dashboard API",
        "version": "1.0",
        "endpoints": [
            "/api/portfolio/latest",
            "/api/prices",
            "/api/signals",
            "/api/assets/{asset}"
        ]
    }

@app.get("/api/portfolio/latest")
async def get_latest_portfolio():
    """Get latest portfolio snapshot"""
    try:
        cached = redis_client.get('latest_portfolio')
        if cached:
            return json.loads(cached)
        
        prices = fetcher.fetch_prices()
        
        historical = {}
        for asset in prices:
            if prices[asset]:
                historical[asset] = fetcher.fetch_historical(asset)
        
        signals = signal_engine.generate_signals(prices, historical)
        weights = risk_manager.calculate_optimal_weights(signals, historical)
        positions = risk_manager.calculate_positions(weights)
        portfolio_risk = risk_manager.check_portfolio_risk(positions)
        
        snapshot = {
            'timestamp': datetime.utcnow().isoformat(),
            'prices': prices,
            'signals': signals,
            'positions': positions,
            'portfolio_risk': portfolio_risk,
            'portfolio_value': risk_manager.portfolio_value
        }
        
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
    import pandas as pd
    from technical_indicators import TechnicalIndicators
    
    hist = fetcher.fetch_historical(asset, period='6mo')
    if hist is None or hist.empty:
        raise HTTPException(status_code=404, detail=f"Asset {asset} not found")
    
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
    return {'history': [], 'hours': hours}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))