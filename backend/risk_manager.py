import numpy as np
import pandas as pd

class PortfolioRiskManager:
    """Kelly Criterion + Risk Parity portfolio optimization"""

    def __init__(self, portfolio_value=100000):
        self.portfolio_value = portfolio_value
        self.max_risk = 0.02  # 2% max daily portfolio risk
        self.max_position = 0.25  # 25% max single position
        self.min_position = 0.05  # 5% min if active

    def calculate_atr_stop(self, price, atr, multiplier=2):
        """Calculate stop-loss based on ATR"""
        return price - (atr * multiplier)

    def calculate_target(self, price, atr, multiplier=3):
        """Calculate take-profit based on ATR"""
        return price + (atr * multiplier)

    def calculate_optimal_weights(self, signals, historical_data):
        """Calculate risk-adjusted position weights"""
        weights = {}

        for asset, signal_data in signals.items():
            signal = signal_data['ensemble']

            # Skip weak signals
            if abs(signal) < 0.2:
                continue

            # Get historical volatility
            hist = historical_data.get(asset)
            if hist is None or hist.empty:
                continue

            atr = hist['ATR'].iloc[-1] if 'ATR' in hist.columns else 0
            price = signal_data['price']

            if price == 0 or pd.isna(atr):
                continue

            # Risk per trade (2x ATR as % of price)
            risk_pct = (atr * 2) / price

            # Expected return estimate
            expected_return = abs(signal) * risk_pct * 1.5

            # Kelly fraction (simplified)
            if risk_pct > 0:
                kelly = expected_return / (risk_pct ** 2)
                kelly = min(kelly * 0.5, self.max_position)  # Half-Kelly, cap at 25%
            else:
                kelly = 0

            weights[asset] = {
                'weight': kelly,
                'risk_pct': risk_pct,
                'expected_return': expected_return,
                'signal': signal,
                'price': price,
                'atr': atr
            }

        # Normalize weights to sum to 1
        total_weight = sum(w['weight'] for w in weights.values())
        if total_weight > 0:
            for asset in weights:
                weights[asset]['weight'] = weights[asset]['weight'] / total_weight

        return weights

    def calculate_positions(self, weights):
        """Convert weights to dollar values and units"""
        positions = {}

        for asset, data in weights.items():
            weight = data['weight']
            price = data['price']
            atr = data['atr']
            signal = data['signal']

            dollar_value = weight * self.portfolio_value

            # Calculate stop and target
            direction = 1 if signal > 0 else -1
            stop = price - (direction * atr * 2)
            target = price + (direction * atr * 3)

            positions[asset] = {
                'weight': round(weight, 4),
                'dollar_value': round(dollar_value, 2),
                'price': price,
                'stop': round(stop, 4),
                'target': round(target, 4),
                'direction': 'LONG' if signal > 0 else 'SHORT',
                'units': round(dollar_value / price, 4) if price > 0 else 0,
                'risk_amount': round(dollar_value * data['risk_pct'], 2),
                'signal': signal
            }

        return positions

    def check_portfolio_risk(self, positions):
        """Check if portfolio risk is within limits"""
        total_risk = sum(p['risk_amount'] for p in positions.values())
        total_risk_pct = total_risk / self.portfolio_value

        return {
            'total_risk': round(total_risk, 2),
            'total_risk_pct': round(total_risk_pct * 100, 2),
            'within_limit': total_risk_pct <= self.max_risk,
            'max_allowed_pct': self.max_risk * 100
        }
