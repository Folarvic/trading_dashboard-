import yfinance as yf
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time

class LiveDataFetcher:
    """Fetches live market data every 15 minutes"""

    def __init__(self):
        self.assets = {
            'EURUSD': 'EURUSD=X',
            'GBPUSD': 'GBPUSD=X',
            'USDJPY': 'USDJPY=X',
            'AUDUSD': 'AUDUSD=X',
            'USDCAD': 'USDCAD=X',
            'XAUUSD': 'GC=F',
            'US30': '^DJI',
        }
        self.last_update = None

    def fetch_prices(self):
        """Fetch live prices for all assets"""
        prices = {}
        for asset, ticker in self.assets.items():
            try:
                data = yf.Ticker(ticker).history(period='1d', interval='15m')
                if not data.empty:
                    latest = data.iloc[-1]
                    prices[asset] = {
                        'price': round(float(latest['Close']), 4),
                        'open': round(float(latest['Open']), 4),
                        'high': round(float(latest['High']), 4),
                        'low': round(float(latest['Low']), 4),
                        'volume': int(latest['Volume']),
                        'timestamp': datetime.utcnow().isoformat()
                    }
                time.sleep(0.5)  # Rate limit protection
            except Exception as e:
                print(f"[ERROR] Fetching {asset}: {e}")
                prices[asset] = None

        self.last_update = datetime.utcnow()
        return prices

    def fetch_historical(self, asset, period='3mo'):
        """Fetch historical data for ML models"""
        ticker = self.assets.get(asset)
        if not ticker:
            return None
        try:
            data = yf.Ticker(ticker).history(period=period, interval='1d')
            return data
        except Exception as e:
            print(f"[ERROR] Historical fetch {asset}: {e}")
            return None

    def fetch_economic_calendar(self):
        """Fetch upcoming economic events"""
        # Using ForexFactory or similar API
        # Placeholder - integrate with actual API
        events = [
            {'time': '12:30', 'event': 'US CPI', 'impact': 'HIGH'},
            {'time': '14:00', 'event': 'Fed Chair Vote', 'impact': 'HIGH'},
        ]
        return events
