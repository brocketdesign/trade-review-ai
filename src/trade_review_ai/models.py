"""Data models for market data and trades."""

from datetime import datetime
from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class OHLCV(BaseModel):
    """Open, High, Low, Close, Volume candlestick data."""
    
    timestamp: datetime = Field(..., description="Candlestick timestamp")
    open: float = Field(..., description="Opening price")
    high: float = Field(..., description="Highest price")
    low: float = Field(..., description="Lowest price")
    close: float = Field(..., description="Closing price")
    volume: float = Field(..., description="Trading volume")
    

class Trade(BaseModel):
    """Individual trade record."""
    
    trade_id: str = Field(..., description="Unique trade identifier")
    timestamp: datetime = Field(..., description="Trade execution timestamp")
    symbol: str = Field(..., description="Trading symbol/instrument")
    side: Literal["buy", "sell"] = Field(..., description="Trade side")
    entry_price: float = Field(..., description="Entry price")
    exit_price: Optional[float] = Field(None, description="Exit price (if closed)")
    exit_timestamp: Optional[datetime] = Field(None, description="Exit timestamp (if closed)")
    quantity: float = Field(..., description="Trade quantity/size")
    stop_loss: Optional[float] = Field(None, description="Stop loss price")
    take_profit: Optional[float] = Field(None, description="Take profit price")
    pnl: Optional[float] = Field(None, description="Realized profit/loss")
    notes: Optional[str] = Field(None, description="Trade notes or strategy")
    

class MarketContext(BaseModel):
    """Market context analysis for a time period."""
    
    symbol: str = Field(..., description="Trading symbol")
    start_date: datetime = Field(..., description="Analysis start date")
    end_date: datetime = Field(..., description="Analysis end date")
    trend: Literal["bullish", "bearish", "neutral"] = Field(..., description="Overall trend direction")
    trend_strength: float = Field(..., ge=0, le=1, description="Trend strength (0-1)")
    volatility: float = Field(..., description="Average True Range or volatility metric")
    support_levels: List[float] = Field(default_factory=list, description="Key support levels")
    resistance_levels: List[float] = Field(default_factory=list, description="Key resistance levels")
    average_volume: float = Field(..., description="Average trading volume")
    

class TradeEvaluation(BaseModel):
    """Evaluation of a single trade."""
    
    trade_id: str = Field(..., description="Trade identifier")
    entry_quality: Literal["good", "acceptable", "poor"] = Field(..., description="Entry quality")
    exit_quality: Optional[Literal["good", "acceptable", "poor"]] = Field(None, description="Exit quality")
    risk_reward_ratio: Optional[float] = Field(None, description="Risk/reward ratio")
    aligned_with_trend: bool = Field(..., description="Whether trade aligned with trend")
    execution_discipline: Literal["high", "medium", "low"] = Field(..., description="Execution discipline score")
    key_observations: List[str] = Field(default_factory=list, description="Key observations")
    

class TradeReview(BaseModel):
    """Complete trade review with AI commentary."""
    
    period_start: datetime = Field(..., description="Review period start")
    period_end: datetime = Field(..., description="Review period end")
    symbol: str = Field(..., description="Trading symbol")
    market_context: MarketContext = Field(..., description="Market context analysis")
    trades: List[Trade] = Field(..., description="Trades in period")
    evaluations: List[TradeEvaluation] = Field(..., description="Trade evaluations")
    ai_commentary: str = Field(..., description="AI-generated pedagogical commentary")
    overall_performance: dict = Field(..., description="Overall performance metrics")
