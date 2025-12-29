"""Main orchestration module for trade review analysis."""

from datetime import datetime
from typing import List, Optional

from .models import Trade, OHLCV, TradeReview
from .config import Config, load_config
from .data_ingestion import DataIngestion
from .market_analysis import MarketAnalyzer
from .trade_evaluation import TradeEvaluator
from .ai_integration import AICommentaryGenerator


class TradeReviewSystem:
    """
    Main orchestrator for the trade review analysis system.
    
    Coordinates data ingestion, market analysis, trade evaluation,
    and AI commentary generation.
    """
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the trade review system.
        
        Args:
            config: Optional configuration object. If not provided, loads from environment.
        """
        self.config = config or load_config()
        self.data_ingestion = DataIngestion()
        self.market_analyzer = MarketAnalyzer()
        self.trade_evaluator = TradeEvaluator()
        self.ai_generator = AICommentaryGenerator(self.config)
    
    def analyze_period(
        self,
        symbol: str,
        market_data_path: str,
        trades_path: str,
        start_date: datetime,
        end_date: datetime
    ) -> TradeReview:
        """
        Perform complete analysis for a trading period.
        
        Args:
            symbol: Trading symbol/instrument
            market_data_path: Path to market data CSV file
            trades_path: Path to trades CSV file
            start_date: Start of analysis period
            end_date: End of analysis period
            
        Returns:
            TradeReview object with complete analysis
        """
        # Load data
        all_market_data = self.data_ingestion.load_market_data(market_data_path)
        all_trades = self.data_ingestion.load_trades(trades_path)
        
        # Filter to date range
        market_data = self.data_ingestion.filter_by_date_range(
            all_market_data, start_date, end_date
        )
        trades = self.data_ingestion.filter_by_date_range(
            all_trades, start_date, end_date
        )
        
        # Validate we have data
        if not market_data:
            raise ValueError(f"No market data found for period {start_date} to {end_date}")
        
        if not trades:
            raise ValueError(f"No trades found for period {start_date} to {end_date}")
        
        # Analyze market context
        market_context = self.market_analyzer.analyze_market_context(
            symbol=symbol,
            ohlcv_data=market_data,
            start_date=start_date,
            end_date=end_date
        )
        
        # Evaluate trades
        evaluations = self.trade_evaluator.evaluate_trades(trades, market_context)
        
        # Calculate performance metrics
        performance_metrics = self._calculate_performance_metrics(trades, evaluations)
        
        # Generate AI commentary
        ai_commentary = self.ai_generator.generate_commentary(
            market_context=market_context,
            trades=trades,
            evaluations=evaluations,
            performance_metrics=performance_metrics
        )
        
        # Assemble complete review
        return TradeReview(
            period_start=start_date,
            period_end=end_date,
            symbol=symbol,
            market_context=market_context,
            trades=trades,
            evaluations=evaluations,
            ai_commentary=ai_commentary,
            overall_performance=performance_metrics
        )
    
    @staticmethod
    def _calculate_performance_metrics(
        trades: List[Trade],
        evaluations: List
    ) -> dict:
        """
        Calculate overall performance metrics.
        
        Args:
            trades: List of trades
            evaluations: List of trade evaluations
            
        Returns:
            Dictionary of performance metrics
        """
        total_trades = len(trades)
        
        # Calculate P&L metrics
        closed_trades = [t for t in trades if t.pnl is not None]
        winning_trades = len([t for t in closed_trades if t.pnl > 0])
        losing_trades = len([t for t in closed_trades if t.pnl < 0])
        
        total_pnl = sum(t.pnl for t in closed_trades)
        avg_pnl = total_pnl / len(closed_trades) if closed_trades else 0.0
        
        win_rate = (winning_trades / len(closed_trades) * 100) if closed_trades else 0.0
        
        # Count trend alignment
        trades_with_trend = sum(1 for e in evaluations if e.aligned_with_trend)
        trades_against_trend = total_trades - trades_with_trend
        
        # Execution quality metrics
        high_discipline = sum(1 for e in evaluations if e.execution_discipline == "high")
        good_entries = sum(1 for e in evaluations if e.entry_quality == "good")
        
        return {
            "total_trades": total_trades,
            "closed_trades": len(closed_trades),
            "open_trades": total_trades - len(closed_trades),
            "winning_trades": winning_trades,
            "losing_trades": losing_trades,
            "win_rate": win_rate,
            "total_pnl": total_pnl,
            "avg_pnl": avg_pnl,
            "trades_with_trend": trades_with_trend,
            "trades_against_trend": trades_against_trend,
            "high_discipline_trades": high_discipline,
            "good_entry_trades": good_entries
        }
