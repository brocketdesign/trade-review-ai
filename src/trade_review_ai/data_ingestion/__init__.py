"""Data ingestion module for loading market data and trade logs."""

from datetime import datetime
from typing import List
import pandas as pd
from pathlib import Path

from ..models import OHLCV, Trade


class DataIngestion:
    """
    Handles ingestion of market data and trade logs from CSV files.
    
    Expected CSV formats:
    - Market data: timestamp, open, high, low, close, volume
    - Trade logs: trade_id, timestamp, symbol, side, entry_price, quantity, 
                  exit_price (optional), exit_timestamp (optional), 
                  stop_loss (optional), take_profit (optional), pnl (optional)
    """
    
    @staticmethod
    def load_market_data(file_path: str) -> List[OHLCV]:
        """
        Load OHLCV market data from CSV file.
        
        Args:
            file_path: Path to CSV file with market data
            
        Returns:
            List of OHLCV candlestick data
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If data format is invalid
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Market data file not found: {file_path}")
        
        df = pd.read_csv(file_path)
        
        # Validate required columns
        required_cols = ["timestamp", "open", "high", "low", "close", "volume"]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        # Convert to OHLCV objects
        ohlcv_data = []
        for _, row in df.iterrows():
            ohlcv_data.append(OHLCV(
                timestamp=pd.to_datetime(row["timestamp"]),
                open=float(row["open"]),
                high=float(row["high"]),
                low=float(row["low"]),
                close=float(row["close"]),
                volume=float(row["volume"])
            ))
        
        return ohlcv_data
    
    @staticmethod
    def load_trades(file_path: str) -> List[Trade]:
        """
        Load trade data from CSV file.
        
        Args:
            file_path: Path to CSV file with trade data
            
        Returns:
            List of Trade objects
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If data format is invalid
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Trade data file not found: {file_path}")
        
        df = pd.read_csv(file_path)
        
        # Validate required columns
        required_cols = ["trade_id", "timestamp", "symbol", "side", "entry_price", "quantity"]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        # Convert to Trade objects
        trades = []
        for _, row in df.iterrows():
            trades.append(Trade(
                trade_id=str(row["trade_id"]),
                timestamp=pd.to_datetime(row["timestamp"]),
                symbol=str(row["symbol"]),
                side=str(row["side"]).lower(),
                entry_price=float(row["entry_price"]),
                quantity=float(row["quantity"]),
                exit_price=float(row["exit_price"]) if pd.notna(row.get("exit_price")) else None,
                exit_timestamp=pd.to_datetime(row["exit_timestamp"]) if pd.notna(row.get("exit_timestamp")) else None,
                stop_loss=float(row["stop_loss"]) if pd.notna(row.get("stop_loss")) else None,
                take_profit=float(row["take_profit"]) if pd.notna(row.get("take_profit")) else None,
                pnl=float(row["pnl"]) if pd.notna(row.get("pnl")) else None,
                notes=str(row["notes"]) if pd.notna(row.get("notes")) else None
            ))
        
        return trades
    
    @staticmethod
    def filter_by_date_range(
        data: List[OHLCV] | List[Trade],
        start_date: datetime,
        end_date: datetime
    ) -> List[OHLCV] | List[Trade]:
        """
        Filter data by date range.
        
        Args:
            data: List of OHLCV or Trade objects
            start_date: Start of date range
            end_date: End of date range
            
        Returns:
            Filtered list of objects within date range
        """
        return [
            item for item in data
            if start_date <= item.timestamp <= end_date
        ]
