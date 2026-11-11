from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from datetime import datetime

# Local imports
import models
from database import engine, get_db
from engine import PandasBacktestEngine, fetch_binance_data

# Create database tables automatically on startup
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="QuantBacktest API",
    description="Production-grade algorithmic trading backtesting and risk analysis engine.",
    version="1.0.0"
)

class BacktestRequest(BaseModel):
    symbol: str = Field(..., example="BTCUSDT")
    timeframe: str = Field(..., example="15m")
    initial_capital: float = Field(10000.0, gt=0)
    risk_per_trade_pct: float = Field(1.0, gt=0, le=5.0)

class BacktestResponse(BaseModel):
    backtest_id: int
    symbol: str
    total_return_pct: float
    max_drawdown_pct: float
    sharpe_ratio: float
    win_rate_pct: float
    total_trades: int

@app.post("/api/v1/backtest/run", response_model=BacktestResponse, status_code=status.HTTP_201_CREATED)
def run_backtest_endpoint(payload: BacktestRequest, db: Session = Depends(get_db)):
    """
    Fetches real historical market data from Binance, executes a vectorized 
    Smart Money Concepts backtest simulation, and persists risk metrics to PostgreSQL.
    """
    try:
        # 1. Fetch live historical data
        df = fetch_binance_data(symbol=payload.symbol, interval=payload.timeframe, limit=1000)
        
        # 2. Execute Pandas backtesting engine logic
        engine_runner = PandasBacktestEngine(
            df=df, 
            initial_capital=payload.initial_capital, 
            risk_pct=payload.risk_per_trade_pct
        )
        metrics = engine_runner.run_strategy()
        
        # 3. Save the results to PostgreSQL
        new_run = models.BacktestRun(
            symbol=payload.symbol,
            timeframe=payload.timeframe,
            initial_capital=payload.initial_capital,
            final_portfolio_value=metrics["final_portfolio_value"],
            total_return_pct=metrics["total_return_pct"],
            max_drawdown_pct=metrics["max_drawdown_pct"],
            sharpe_ratio=metrics["sharpe_ratio"],
            win_rate_pct=metrics["win_rate_pct"],
            strategy_params={"strategy": "SMC_FVG", "risk_pct": payload.risk_per_trade_pct}
        )
        db.add(new_run)
        db.commit()
        db.refresh(new_run)
        
        # 4. Return API response
        return {
            "backtest_id": new_run.id,
            "symbol": new_run.symbol,
            "total_return_pct": metrics["total_return_pct"],
            "max_drawdown_pct": metrics["max_drawdown_pct"],
            "sharpe_ratio": metrics["sharpe_ratio"],
            "win_rate_pct": metrics["win_rate_pct"],
            "total_trades": metrics["total_trades"]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))