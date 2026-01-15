"""
MetaTrader 5 Quotes Fetcher Module

Downloads historical quotes from MetaTrader 5 terminal.
"""

from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd

try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False


class MT5QuotesFetcher:
    """Fetches historical price quotes from MetaTrader 5."""

    TIMEFRAMES = {
        'M1': 1,    # 1 minute
        'M5': 5,    # 5 minutes
        'M15': 15,  # 15 minutes
        'M30': 30,  # 30 minutes
        'H1': 60,   # 1 hour
        'H4': 240,  # 4 hours
        'D1': 16408,  # Daily
        'W1': 32769,  # Weekly
        'MN1': 49153  # Monthly
    }

    def __init__(self, terminal_path: str = None, output_dir: str = "data/quotes"):
        """
        Initialize the fetcher.

        Args:
            terminal_path: Path to MetaTrader 5 terminal executable
            output_dir: Directory to save quote files
        """
        if not MT5_AVAILABLE:
            raise ImportError(
                "MetaTrader5 package not available. "
                "Install it with: pip install MetaTrader5 (Windows only)"
            )
        
        self.terminal_path = terminal_path or r"C:\Program Files\MetaTrader 5\terminal64.exe"
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._connected = False

    def connect(self) -> bool:
        """
        Connect to MetaTrader 5 terminal.

        Returns:
            True if connection successful, False otherwise
        """
        if not mt5.initialize(self.terminal_path):
            error = mt5.last_error()
            print(f"✗ Failed to connect to MT5: {error}")
            return False
        
        self._connected = True
        print("✓ Connected to MetaTrader 5")
        return True

    def disconnect(self) -> None:
        """Disconnect from MetaTrader 5 terminal."""
        if self._connected:
            mt5.shutdown()
            self._connected = False
            print("✓ Disconnected from MetaTrader 5")

    def get_symbols(self) -> list[str]:
        """
        Get list of available symbols.

        Returns:
            List of symbol names
        """
        if not self._connected:
            raise ConnectionError("Not connected to MT5. Call connect() first.")
        
        symbols = mt5.symbols_get()
        return [s.name for s in symbols] if symbols else []

    def fetch_quotes(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime = None,
        timeframe: str = 'D1'
    ) -> Optional[pd.DataFrame]:
        """
        Fetch historical quotes for a symbol.

        Args:
            symbol: Symbol name (e.g., 'PETR4', 'VALE3')
            start_date: Start date for historical data
            end_date: End date (defaults to now)
            timeframe: Timeframe (M1, M5, M15, M30, H1, H4, D1, W1, MN1)

        Returns:
            DataFrame with OHLCV data or None if failed
        """
        if not self._connected:
            raise ConnectionError("Not connected to MT5. Call connect() first.")
        
        if end_date is None:
            end_date = datetime.now()
        
        tf = self.TIMEFRAMES.get(timeframe.upper())
        if tf is None:
            raise ValueError(f"Invalid timeframe: {timeframe}")
        
        # Fetch rates
        rates = mt5.copy_rates_range(symbol, tf, start_date, end_date)
        
        if rates is None or len(rates) == 0:
            print(f"✗ No data for {symbol}")
            return None
        
        # Convert to DataFrame
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df = df.rename(columns={
            'time': 'datetime',
            'open': 'open',
            'high': 'high',
            'low': 'low',
            'close': 'close',
            'tick_volume': 'volume',
            'spread': 'spread',
            'real_volume': 'real_volume'
        })
        
        print(f"✓ Fetched {len(df)} candles for {symbol}")
        return df

    def fetch_multiple(
        self,
        symbols: list[str],
        start_date: datetime,
        end_date: datetime = None,
        timeframe: str = 'D1'
    ) -> dict[str, pd.DataFrame]:
        """
        Fetch historical quotes for multiple symbols.

        Args:
            symbols: List of symbol names
            start_date: Start date for historical data
            end_date: End date (defaults to now)
            timeframe: Timeframe

        Returns:
            Dictionary mapping symbol to DataFrame
        """
        results = {}
        
        for symbol in symbols:
            df = self.fetch_quotes(symbol, start_date, end_date, timeframe)
            if df is not None:
                results[symbol] = df
        
        return results

    def save_to_parquet(self, df: pd.DataFrame, symbol: str) -> Path:
        """
        Save quotes DataFrame to Parquet file.

        Args:
            df: DataFrame with quotes
            symbol: Symbol name (used in filename)

        Returns:
            Path to saved file
        """
        filename = f"{symbol.lower()}_quotes.parquet"
        filepath = self.output_dir / filename
        df.to_parquet(filepath, index=False)
        print(f"✓ Saved: {filepath}")
        return filepath

    def save_to_csv(self, df: pd.DataFrame, symbol: str) -> Path:
        """
        Save quotes DataFrame to CSV file.

        Args:
            df: DataFrame with quotes
            symbol: Symbol name (used in filename)

        Returns:
            Path to saved file
        """
        filename = f"{symbol.lower()}_quotes.csv"
        filepath = self.output_dir / filename
        df.to_csv(filepath, index=False)
        print(f"✓ Saved: {filepath}")
        return filepath


if __name__ == "__main__":
    # Example usage
    print("=== MetaTrader 5 Quotes Fetcher ===\n")
    
    if not MT5_AVAILABLE:
        print("MetaTrader5 package not available.")
        print("This module only works on Windows with MT5 installed.")
        exit(1)
    
    fetcher = MT5QuotesFetcher()
    
    if fetcher.connect():
        # Fetch quotes for a single symbol
        symbols = ["PETR4", "VALE3", "ABEV3", "ITUB4"]
        start = datetime(2020, 1, 1)
        
        for symbol in symbols:
            df = fetcher.fetch_quotes(symbol, start)
            if df is not None:
                fetcher.save_to_parquet(df, symbol)
        
        fetcher.disconnect()
