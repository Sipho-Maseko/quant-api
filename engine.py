import requests
import numpy as np
import pandas as pd

def fetch_binance_data(symbol: str, interval: str, limit: int = 1000) -> pd.DataFrame:
    """Fetches historical klines from the Binance API and formats them."""
    url = "https://api.binance.com/api/v3/klines"
    params = {"symbol": symbol.upper(), "interval": interval, "limit": limit}
    
    response = requests.get(url, params=params)
    response.raise_for_status() 
    
    data = response.json()
    df = pd.DataFrame(data, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'number_of_trades',
        'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
    ])
    
    df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    
    numeric_cols = ['open', 'high', 'low', 'close', 'volume']
    df[numeric_cols] = df[numeric_cols].astype(float)
    
    return df

class PandasBacktestEngine:
    def __init__(self, df: pd.DataFrame, initial_capital: float = 10000.0, risk_pct: float = 1.0):
        self.df = df.copy()
        self.initial_capital = initial_capital
        self.risk_pct = risk_pct / 100.0

    def run_strategy(self):
        """
        Executes a vectorized Smart Money Concepts (SMC) backtest 
        identifying Bullish and Bearish Fair Value Gaps (FVG).
        """
        # Vectorized Bullish FVG Detection: Current Low > High from 2 candles ago
        self.df['bullish_fvg'] = (self.df['low'] > self.df['high'].shift(2)) & (self.df['close'].shift(1) > self.df['high'].shift(2))
        
        # Vectorized Bearish FVG Detection: Current High < Low from 2 candles ago
        self.df['bearish_fvg'] = (self.df['high'] < self.df['low'].shift(2)) & (self.df['close'].shift(1) < self.df['low'].shift(2))

        # Generate directional signals: 1 for Long, -1 for Short, 0 for Flat
        self.df['signal'] = 0
        self.df.loc[self.df['bullish_fvg'], 'signal'] = 1
        self.df.loc[self.df['bearish_fvg'], 'signal'] = -1
        
        # Shift signal by 1 to represent entering the trade on the *next* candle open
        self.df['position'] = self.df['signal'].shift(1).fillna(0)

        # Calculate market returns and strategy returns
        self.df['market_return'] = self.df['close'].pct_change()
        self.df['strategy_return'] = self.df['market_return'] * self.df['position']
        
        # Portfolio equity curve
        self.df['portfolio_value'] = self.initial_capital * (1 + self.df['strategy_return'].fillna(0)).cumprod()

        return self.compute_metrics()

    def compute_metrics(self) -> dict:
        portfolio = self.df['portfolio_value']
        returns = self.df['strategy_return'].dropna()

        final_val = portfolio.iloc[-1]
        total_return_pct = ((final_val - self.initial_capital) / self.initial_capital) * 100

        rolling_max = portfolio.cummax()
        drawdown = (portfolio - rolling_max) / rolling_max
        max_drawdown_pct = drawdown.min() * 100

        # Annualized Sharpe Ratio (assuming 15m intervals -> 35,040 periods/year)
        sharpe_ratio = 0.0
        if returns.std() > 0:
            sharpe_ratio = (returns.mean() / returns.std()) * np.sqrt(35040)

        winning_trades = returns[returns > 0].count()
        total_trades = returns[returns != 0].count()
        win_rate_pct = (winning_trades / total_trades * 100) if total_trades > 0 else 0.0

        return {
            "final_portfolio_value": round(final_val, 2),
            "total_return_pct": round(total_return_pct, 2),
            "max_drawdown_pct": round(max_drawdown_pct, 2),
            "sharpe_ratio": round(sharpe_ratio, 2),
            "win_rate_pct": round(win_rate_pct, 2),
            "total_trades": int(total_trades)
        }