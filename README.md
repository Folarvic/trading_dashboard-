# 🤖 AI Trading Dashboard

Real-time forex, gold, and index trading dashboard with ML/DL ensemble signals, automated risk management, and 15-minute auto-updates.

## Features

- **7 Asset Portfolio**: EURUSD, GBPUSD, USDJPY, AUDUSD, USDCAD, XAUUSD (Gold), US30 (Dow Jones)
- **ML/DL Ensemble**: LSTM (30%) + XGBoost (25%) + Transformer (25%) + GARCH (20%)
- **Auto-Risk Management**: Kelly Criterion + Risk Parity + ATR-based stops
- **15-Minute Auto-Update**: Celery scheduler with Redis backend
- **Real-Time Dashboard**: FastAPI backend + responsive frontend
- **WebSocket Support**: Live push updates to browser

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup Environment
```bash
cp .env.example .env
# Edit .env with your API keys
```

### 3. Start Redis
```bash
redis-server
```

### 4. Initialize Database
```bash
psql -U your_user -d trading -f database/schema.sql
```

### 5. Start Services

Terminal 1 - API Server:
```bash
cd backend/api
uvicorn main:app --reload
```

Terminal 2 - Celery Worker:
```bash
cd backend/tasks
celery -A scheduler worker --loglevel=info
```

Terminal 3 - Celery Beat (Scheduler):
```bash
cd backend/tasks
celery -A scheduler beat --loglevel=info
```

Terminal 4 - Frontend:
```bash
cd frontend
python -m http.server 8080
```

### 6. Open Dashboard
Navigate to `http://localhost:8080`

## Architecture

```
ai_trading_dashboard/
├── backend/
│   ├── api/              # FastAPI REST endpoints
│   ├── data/             # Data fetchers
│   ├── models/           # ML/DL models
│   ├── tasks/            # Celery scheduled tasks
│   ├── technical_indicators.py
│   ├── signal_engine.py
│   ├── risk_manager.py
│   └── data_fetcher.py
├── frontend/
│   ├── templates/        # HTML templates
│   └── static/
│       ├── css/          # Stylesheets
│       └── js/           # Dashboard logic
├── database/
│   └── schema.sql        # PostgreSQL schema
├── config/
│   └── settings.py       # Configuration
├── scripts/
│   └── deploy.sh         # Deployment script
└── tests/                # Unit tests
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/portfolio/latest` | GET | Full portfolio snapshot |
| `/api/prices` | GET | Current prices only |
| `/api/signals` | GET | ML signals only |
| `/api/assets/{asset}` | GET | Detailed asset info |
| `/api/history` | GET | Portfolio history |

## ML/DL Signal Engine

The ensemble combines 4 models:

1. **LSTM (30%)**: Trend-following using price momentum
2. **XGBoost (25%)**: Mean-reversion using RSI and Bollinger Bands
3. **Transformer (25%)**: Sentiment analysis using price position within bands
4. **GARCH (20%)**: Volatility-adjusted directional signals

## Risk Management

- **Kelly Criterion**: Half-Kelly position sizing
- **Risk Parity**: Inverse volatility weighting
- **ATR Stops**: 2x ATR stop-loss, 3x ATR take-profit
- **Portfolio Limit**: Max 2% daily risk, 25% single position

## Data Sources

- **Yahoo Finance**: Free stocks, FX, futures data
- **Alpha Vantage**: Alternative FX data
- **NewsAPI**: News sentiment (optional)
- **FRED**: Economic indicators

## Deployment

### Docker (Recommended)
```bash
docker-compose up -d
```

### Cloud (AWS/DigitalOcean)
```bash
./scripts/deploy.sh
```

## License

MIT License - Educational purposes only. Not financial advice.
