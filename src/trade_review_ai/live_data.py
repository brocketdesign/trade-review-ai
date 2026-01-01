"""Live market data service using Yahoo Finance API."""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import yfinance as yf
import pandas as pd

from .models import OHLCV, Trade


class LiveDataService:
    """
    Service for fetching live market data from Yahoo Finance.
    
    Supports fetching OHLCV data for any symbol with various intervals
    and time periods.
    """
    
    # Map of period strings to yfinance format
    PERIOD_MAP = {
        '1d': '1d',
        '5d': '5d',
        '1w': '5d',
        '1mo': '1mo',
        '3mo': '3mo',
        '6mo': '6mo',
        '1y': '1y',
        '2y': '2y',
        '5y': '5y',
        'ytd': 'ytd',
        'max': 'max'
    }
    
    # Map of interval strings to yfinance format
    INTERVAL_MAP = {
        '1m': '1m',
        '2m': '2m',
        '5m': '5m',
        '15m': '15m',
        '30m': '30m',
        '1h': '60m',
        '90m': '90m',
        '1d': '1d',
        '5d': '5d',
        '1wk': '1wk',
        '1mo': '1mo',
        '3mo': '3mo'
    }
    
    @classmethod
    def fetch_market_data(
        cls,
        symbol: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        period: Optional[str] = None,
        interval: str = '1d'
    ) -> List[OHLCV]:
        """
        Fetch OHLCV market data for a symbol.
        
        Args:
            symbol: Trading symbol (e.g., 'AAPL', 'MSFT', 'BTC-USD')
            start_date: Start date for data (optional if period is specified)
            end_date: End date for data (defaults to today)
            period: Time period string (e.g., '1mo', '3mo', '1y')
            interval: Data interval (e.g., '1m', '5m', '1h', '1d')
            
        Returns:
            List of OHLCV candlestick data
            
        Raises:
            ValueError: If symbol is invalid or no data available
        """
        try:
            ticker = yf.Ticker(symbol)
            
            # Determine how to fetch data
            if period and period in cls.PERIOD_MAP:
                df = ticker.history(
                    period=cls.PERIOD_MAP[period],
                    interval=cls.INTERVAL_MAP.get(interval, '1d')
                )
            elif start_date:
                end = end_date or datetime.now()
                df = ticker.history(
                    start=start_date,
                    end=end,
                    interval=cls.INTERVAL_MAP.get(interval, '1d')
                )
            else:
                # Default to 1 month of data
                df = ticker.history(period='1mo', interval=cls.INTERVAL_MAP.get(interval, '1d'))
            
            if df.empty:
                raise ValueError(f"No data available for symbol: {symbol}")
            
            # Convert DataFrame to OHLCV list
            ohlcv_data = []
            for idx, row in df.iterrows():
                ohlcv_data.append(OHLCV(
                    timestamp=idx.to_pydatetime() if hasattr(idx, 'to_pydatetime') else idx,
                    open=float(row['Open']),
                    high=float(row['High']),
                    low=float(row['Low']),
                    close=float(row['Close']),
                    volume=float(row['Volume'])
                ))
            
            return ohlcv_data
            
        except Exception as e:
            raise ValueError(f"Error fetching data for {symbol}: {str(e)}")
    
    @classmethod
    def get_symbol_info(cls, symbol: str) -> Dict[str, Any]:
        """
        Get information about a symbol.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Dictionary with symbol information
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            return {
                'symbol': symbol.upper(),
                'name': info.get('longName', info.get('shortName', symbol)),
                'exchange': info.get('exchange', 'Unknown'),
                'currency': info.get('currency', 'USD'),
                'type': info.get('quoteType', 'Unknown'),
                'current_price': info.get('currentPrice', info.get('regularMarketPrice')),
                'previous_close': info.get('previousClose'),
                'market_cap': info.get('marketCap'),
                'volume': info.get('volume'),
                'avg_volume': info.get('averageVolume'),
                'day_high': info.get('dayHigh'),
                'day_low': info.get('dayLow'),
                '52_week_high': info.get('fiftyTwoWeekHigh'),
                '52_week_low': info.get('fiftyTwoWeekLow')
            }
        except Exception as e:
            return {
                'symbol': symbol.upper(),
                'name': symbol.upper(),
                'error': str(e)
            }
    
    @classmethod
    def search_symbols(cls, query: str, limit: int = 10) -> List[Dict[str, str]]:
        """
        Search for symbols matching a query.
        
        Note: yfinance doesn't have a native search, so we provide common symbols
        that match the query or suggest trying the exact symbol.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching symbol dictionaries
        """
        # Common symbols for suggestions
        common_symbols = {
            # Tech stocks
            'AAPL': 'Apple Inc.',
            'MSFT': 'Microsoft Corporation',
            'GOOGL': 'Alphabet Inc.',
            'GOOG': 'Alphabet Inc. Class C',
            'AMZN': 'Amazon.com Inc.',
            'META': 'Meta Platforms Inc.',
            'NVDA': 'NVIDIA Corporation',
            'TSLA': 'Tesla Inc.',
            'AMD': 'Advanced Micro Devices',
            'INTC': 'Intel Corporation',
            'NFLX': 'Netflix Inc.',
            'CRM': 'Salesforce Inc.',
            # Financial
            'JPM': 'JPMorgan Chase & Co.',
            'BAC': 'Bank of America',
            'GS': 'Goldman Sachs',
            'V': 'Visa Inc.',
            'MA': 'Mastercard Inc.',
            # Consumer
            'WMT': 'Walmart Inc.',
            'KO': 'Coca-Cola Company',
            'PEP': 'PepsiCo Inc.',
            'MCD': "McDonald's Corporation",
            'NKE': 'Nike Inc.',
            'DIS': 'Walt Disney Company',
            # Healthcare
            'JNJ': 'Johnson & Johnson',
            'PFE': 'Pfizer Inc.',
            'UNH': 'UnitedHealth Group',
            'MRNA': 'Moderna Inc.',
            # Energy
            'XOM': 'Exxon Mobil',
            'CVX': 'Chevron Corporation',
            # Crypto
            'BTC-USD': 'Bitcoin USD',
            'ETH-USD': 'Ethereum USD',
            'BNB-USD': 'Binance Coin USD',
            'SOL-USD': 'Solana USD',
            'XRP-USD': 'XRP USD',
            # Indices
            'SPY': 'SPDR S&P 500 ETF',
            'QQQ': 'Invesco QQQ Trust',
            'DIA': 'SPDR Dow Jones ETF',
            'IWM': 'iShares Russell 2000 ETF',
            '^GSPC': 'S&P 500 Index',
            '^DJI': 'Dow Jones Industrial Average',
            '^IXIC': 'NASDAQ Composite',
            # Forex
            'EURUSD=X': 'EUR/USD',
            'GBPUSD=X': 'GBP/USD',
            'USDJPY=X': 'USD/JPY',
        }
        
        query_upper = query.upper()
        results = []
        
        # Exact match first
        if query_upper in common_symbols:
            results.append({
                'symbol': query_upper,
                'name': common_symbols[query_upper]
            })
        
        # Partial matches
        for symbol, name in common_symbols.items():
            if symbol != query_upper:  # Skip exact match already added
                if query_upper in symbol or query_upper in name.upper():
                    results.append({
                        'symbol': symbol,
                        'name': name
                    })
        
        # If no results, suggest trying the query as a symbol
        if not results:
            results.append({
                'symbol': query_upper,
                'name': f'Try "{query_upper}" directly'
            })
        
        return results[:limit]
    
    @classmethod
    def validate_symbol(cls, symbol: str) -> bool:
        """
        Check if a symbol is valid by attempting to fetch recent data.
        
        Args:
            symbol: Trading symbol to validate
            
        Returns:
            True if symbol is valid, False otherwise
        """
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period='1d')
            return not hist.empty
        except:
            return False


class ManualTradeManager:
    """
    Manages manually entered trades stored in memory.
    
    Trades persist only for the session. For persistence,
    integrate with a database.
    """
    
    def __init__(self):
        self._trades: List[Trade] = []
        self._trade_counter = 0
    
    def add_trade(
        self,
        symbol: str,
        side: str,
        entry_price: float,
        quantity: float,
        timestamp: Optional[datetime] = None,
        exit_price: Optional[float] = None,
        exit_timestamp: Optional[datetime] = None,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
        notes: Optional[str] = None
    ) -> Trade:
        """
        Add a new manual trade.
        
        Args:
            symbol: Trading symbol
            side: 'buy' or 'sell'
            entry_price: Entry price
            quantity: Trade quantity
            timestamp: Entry timestamp (defaults to now)
            exit_price: Exit price (optional)
            exit_timestamp: Exit timestamp (optional)
            stop_loss: Stop loss price (optional)
            take_profit: Take profit price (optional)
            notes: Trade notes (optional)
            
        Returns:
            Created Trade object
        """
        self._trade_counter += 1
        trade_id = f"MANUAL-{self._trade_counter:04d}"
        
        # Calculate P&L if exit price is provided
        pnl = None
        if exit_price is not None:
            if side.lower() == 'buy':
                pnl = (exit_price - entry_price) * quantity
            else:
                pnl = (entry_price - exit_price) * quantity
        
        trade = Trade(
            trade_id=trade_id,
            timestamp=timestamp or datetime.now(),
            symbol=symbol.upper(),
            side=side.lower(),
            entry_price=entry_price,
            quantity=quantity,
            exit_price=exit_price,
            exit_timestamp=exit_timestamp,
            stop_loss=stop_loss,
            take_profit=take_profit,
            pnl=pnl,
            notes=notes
        )
        
        self._trades.append(trade)
        return trade
    
    def update_trade(
        self,
        trade_id: str,
        exit_price: Optional[float] = None,
        exit_timestamp: Optional[datetime] = None,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
        notes: Optional[str] = None
    ) -> Optional[Trade]:
        """
        Update an existing trade.
        
        Args:
            trade_id: ID of trade to update
            exit_price: New exit price
            exit_timestamp: New exit timestamp
            stop_loss: New stop loss
            take_profit: New take profit
            notes: Updated notes
            
        Returns:
            Updated Trade object or None if not found
        """
        for i, trade in enumerate(self._trades):
            if trade.trade_id == trade_id:
                # Create updated trade
                pnl = trade.pnl
                if exit_price is not None:
                    if trade.side == 'buy':
                        pnl = (exit_price - trade.entry_price) * trade.quantity
                    else:
                        pnl = (trade.entry_price - exit_price) * trade.quantity
                
                updated_trade = Trade(
                    trade_id=trade.trade_id,
                    timestamp=trade.timestamp,
                    symbol=trade.symbol,
                    side=trade.side,
                    entry_price=trade.entry_price,
                    quantity=trade.quantity,
                    exit_price=exit_price if exit_price is not None else trade.exit_price,
                    exit_timestamp=exit_timestamp if exit_timestamp is not None else trade.exit_timestamp,
                    stop_loss=stop_loss if stop_loss is not None else trade.stop_loss,
                    take_profit=take_profit if take_profit is not None else trade.take_profit,
                    pnl=pnl,
                    notes=notes if notes is not None else trade.notes
                )
                
                self._trades[i] = updated_trade
                return updated_trade
        
        return None
    
    def delete_trade(self, trade_id: str) -> bool:
        """
        Delete a trade by ID.
        
        Args:
            trade_id: ID of trade to delete
            
        Returns:
            True if deleted, False if not found
        """
        for i, trade in enumerate(self._trades):
            if trade.trade_id == trade_id:
                del self._trades[i]
                return True
        return False
    
    def get_trades(
        self,
        symbol: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Trade]:
        """
        Get trades with optional filters.
        
        Args:
            symbol: Filter by symbol
            start_date: Filter by start date
            end_date: Filter by end date
            
        Returns:
            List of matching trades
        """
        trades = self._trades.copy()
        
        if symbol:
            trades = [t for t in trades if t.symbol == symbol.upper()]
        
        if start_date:
            trades = [t for t in trades if t.timestamp >= start_date]
        
        if end_date:
            trades = [t for t in trades if t.timestamp <= end_date]
        
        return sorted(trades, key=lambda t: t.timestamp)
    
    def clear_trades(self, symbol: Optional[str] = None):
        """
        Clear all trades or trades for a specific symbol.
        
        Args:
            symbol: Optional symbol to clear trades for
        """
        if symbol:
            self._trades = [t for t in self._trades if t.symbol != symbol.upper()]
        else:
            self._trades = []
            self._trade_counter = 0
