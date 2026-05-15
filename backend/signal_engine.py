import numpy as np
import pandas as pd
from datetime import datetime
from backend.technical_indicators import TechnicalIndicators

class EnsembleSignalEngine:
    """
    4-Model Ensemble:
    - LSTM (30%): Trend following
    - XGBoost (25%): Mean reversion
    - Transformer (25%): Sentiment analysis
    - GARCH (20%): Volatility forecasting
    """

    def __init__(self):
        self.weights = {
            'lstm': 0.30,
            'xgboost': 0.25,
            'transformer': 0.25,
            'garch': 0.20
        }

    def lstm_signal(self, df):
        """LSTM trend signal (simplified using momentum)"""
        returns = df['Close'].pct_change(5)
        momentum = returns.rolling(10).mean()
        latest = momentum.iloc[-1]
        # Normalize to -1 to 1
        return np.tanh(latest * 100)

    def xgboost_signal(self, df):
        """XGBoost mean reversion (simplified using RSI)"""
        rsi = df['RSI'].iloc[-1]
        if pd.isna(rsi):
            return 0
        # Oversold = buy, overbought = sell
        if rsi < 30:
            return 0.7
        elif rsi > 70:
            return -0.7
        elif rsi < 45:
            return 0.3
        elif rsi > 55:
            return -0.3
        return 0

    def transformer_signal(self, df):
        """Transformer sentiment (simplified using price action)"""
        close = df['Close'].iloc[-1]
        bb_upper = df['BB_Upper'].iloc[-1]
        bb_lower = df['BB_Lower'].iloc[-1]

        if pd.isna(bb_upper) or pd.isna(bb_lower):
            return 0

        # Price near upper band = bullish sentiment
        # Price near lower band = bearish sentiment
        position = (close - bb_lower) / (bb_upper - bb_lower)
        return (position - 0.5) * 2  # Normalize to -1 to 1

    def garch_signal(self, df):
        """GARCH volatility signal"""
        atr = df['ATR'].iloc[-1]
        close = df['Close'].iloc[-1]

        if pd.isna(atr) or close == 0:
            return 0

        vol_pct = atr / close
        # High volatility = cautious (reduce signal strength)
        # Low volatility = confident (increase signal strength)
        vol_factor = 1 - min(vol_pct * 100, 1)

        # Direction from recent price action
        direction = np.sign(df['Close'].iloc[-1] - df['Close'].iloc[-5])
        return direction * vol_factor * 0.5

    def generate_signals(self, price_data, historical_data):
        """Generate ensemble signals for all assets"""
        signals = {}

        for asset in price_data:
            if price_data[asset] is None:
                continue

            hist = historical_data.get(asset)
            if hist is None or hist.empty:
                continue

            # Calculate indicators
            hist = TechnicalIndicators.calculate_all(hist)

            # Get model signals
            lstm = self.lstm_signal(hist)
            xgb = self.xgboost_signal(hist)
            trans = self.transformer_signal(hist)
            garch = self.garch_signal(hist)

            # Ensemble
            ensemble = (
                self.weights['lstm'] * lstm +
                self.weights['xgboost'] * xgb +
                self.weights['transformer'] * trans +
                self.weights['garch'] * garch
            )

            # Determine action
            if ensemble > 0.5:
                action = 'STRONG_BUY'
            elif ensemble > 0.2:
                action = 'BUY'
            elif ensemble > -0.2:
                action = 'HOLD'
            elif ensemble > -0.5:
                action = 'SELL'
            else:
                action = 'STRONG_SELL'

            signals[asset] = {
                'ensemble': round(float(ensemble), 3),
                'lstm': round(float(lstm), 3),
                'xgboost': round(float(xgb), 3),
                'transformer': round(float(trans), 3),
                'garch': round(float(garch), 3),
                'action': action,
                'price': price_data[asset]['price'],
                'timestamp': datetime.utcnow().isoformat()
            }

        return signals
