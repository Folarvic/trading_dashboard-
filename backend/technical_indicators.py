import pandas as pd
import numpy as np

class TechnicalIndicators:
    """Calculate technical indicators for signal generation"""

    @staticmethod
    def rsi(prices, period=14):
        """Relative Strength Index"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    @staticmethod
    def macd(prices, fast=12, slow=26, signal=9):
        """MACD indicator"""
        exp1 = prices.ewm(span=fast).mean()
        exp2 = prices.ewm(span=slow).mean()
        macd_line = exp1 - exp2
        signal_line = macd_line.ewm(span=signal).mean()
        histogram = macd_line - signal_line
        return macd_line, signal_line, histogram

    @staticmethod
    def bollinger_bands(prices, period=20, std_dev=2):
        """Bollinger Bands"""
        sma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        upper = sma + (std * std_dev)
        lower = sma - (std * std_dev)
        return upper, sma, lower

    @staticmethod
    def atr(high, low, close, period=14):
        """Average True Range"""
        high_low = high - low
        high_close = np.abs(high - close.shift())
        low_close = np.abs(low - close.shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        return true_range.rolling(period).mean()

    @staticmethod
    def calculate_all(df):
        """Calculate all indicators at once"""
        df['RSI'] = TechnicalIndicators.rsi(df['Close'])
        df['MACD'], df['MACD_Signal'], df['MACD_Hist'] = TechnicalIndicators.macd(df['Close'])
        df['BB_Upper'], df['BB_Middle'], df['BB_Lower'] = TechnicalIndicators.bollinger_bands(df['Close'])
        df['ATR'] = TechnicalIndicators.atr(df['High'], df['Low'], df['Close'])

        # Additional indicators
        df['SMA_20'] = df['Close'].rolling(20).mean()
        df['SMA_50'] = df['Close'].rolling(50).mean()
        df['EMA_12'] = df['Close'].ewm(span=12).mean()
        df['Volume_MA'] = df['Volume'].rolling(20).mean()

        return df
