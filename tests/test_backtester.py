import pytest
import pandas as pd
import numpy as np
from engine import PandasBacktestEngine

@pytest.fixture
def sample_market_data():
    """Generates a synthetic OHLCV DataFrame with a clear upward trend and pullback."""
    np.random.seed(42)
    dates = pd.date_range(start="2026-01-01", periods=100, freq="15min")
    
    # Create price series with a predictable wave
    base_price = 50000.0
    trend = np.linspace(0, 5000, 100)
    noise = np.sin(np.linspace(0, 4 * np.pi, 100)) * 500
    close_prices = base_price + trend + noise
    
    df = pd.DataFrame({
        'timestamp': dates,
        'open': close_prices - 20,
        'high': close_prices + 50,
        'low': close_prices - 50,
        'close': close_prices,
        'volume': np.random.randint(100, 1000, size=100)
    })
    return df

def test_engine_initialization(sample_market_data):
    engine = PandasBacktestEngine(sample_market_data, initial_capital=10000.0, risk_pct=1.0)
    assert engine.initial_capital == 10000.0
    assert len(engine.df) == 100

def test_run_strategy_metrics(sample_market_data):
    engine = PandasBacktestEngine(sample_market_data, initial_capital=10000.0)
    metrics = engine.run_strategy()

    # Assert keys exist in output
    assert "final_portfolio_value" in metrics
    assert "total_return_pct" in metrics
    assert "max_drawdown_pct" in metrics
    assert "sharpe_ratio" in metrics
    assert "win_rate_pct" in metrics
    assert "total_trades" in metrics

    # Assert values are within logical financial bounds
    assert metrics["final_portfolio_value"] > 0
    assert isinstance(metrics["sharpe_ratio"], float)
    assert 0.0 <= metrics["win_rate_pct"] <= 100.0
    assert metrics["max_drawdown_pct"] <= 0.0 # Drawdowns should be 0 or negative