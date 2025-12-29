"""Trade evaluation module for analyzing trade quality."""

from typing import List, Optional
from ..models import Trade, MarketContext, TradeEvaluation, OHLCV


class TradeEvaluator:
    """
    Evaluates individual trades based on market context and execution quality.
    
    Uses deterministic rules to assess trade quality for consistent analysis.
    """
    
    @staticmethod
    def evaluate_entry_quality(
        trade: Trade,
        market_context: MarketContext,
        entry_candle: Optional[OHLCV] = None
    ) -> str:
        """
        Evaluate the quality of a trade entry.
        
        Args:
            trade: Trade to evaluate
            market_context: Market context at time of trade
            entry_candle: OHLCV data at entry time (if available)
            
        Returns:
            Entry quality: "good", "acceptable", or "poor"
        """
        score = 0
        
        # Check if entry aligns with trend
        if market_context.trend == "bullish" and trade.side == "buy":
            score += 2
        elif market_context.trend == "bearish" and trade.side == "sell":
            score += 2
        elif market_context.trend == "neutral":
            score += 1  # Neutral is acceptable but not ideal
        else:
            score -= 1  # Counter-trend
        
        # Check if entry is near support/resistance
        if trade.side == "buy":
            # Good buy entries are near support
            near_support = any(
                abs(trade.entry_price - level) / level < 0.01
                for level in market_context.support_levels
            )
            if near_support:
                score += 2
        else:  # sell
            # Good sell entries are near resistance
            near_resistance = any(
                abs(trade.entry_price - level) / level < 0.01
                for level in market_context.resistance_levels
            )
            if near_resistance:
                score += 2
        
        # Categorize based on score
        if score >= 3:
            return "good"
        elif score >= 1:
            return "acceptable"
        else:
            return "poor"
    
    @staticmethod
    def evaluate_exit_quality(trade: Trade, market_context: MarketContext) -> Optional[str]:
        """
        Evaluate the quality of a trade exit.
        
        Args:
            trade: Trade to evaluate
            market_context: Market context at time of trade
            
        Returns:
            Exit quality: "good", "acceptable", or "poor" (None if still open)
        """
        if trade.exit_price is None:
            return None
        
        score = 0
        
        # Calculate actual profit/loss percentage
        if trade.side == "buy":
            pnl_pct = (trade.exit_price - trade.entry_price) / trade.entry_price
        else:  # sell
            pnl_pct = (trade.entry_price - trade.exit_price) / trade.entry_price
        
        # Good exits have positive P&L
        if pnl_pct > 0.02:  # > 2% profit
            score += 2
        elif pnl_pct > 0:
            score += 1
        elif pnl_pct < -0.02:  # > 2% loss
            score -= 2
        else:
            score -= 1
        
        # Check if stop loss or take profit was used (discipline)
        if trade.stop_loss is not None:
            score += 1
        if trade.take_profit is not None:
            score += 1
        
        # Categorize based on score
        if score >= 3:
            return "good"
        elif score >= 0:
            return "acceptable"
        else:
            return "poor"
    
    @staticmethod
    def calculate_risk_reward(trade: Trade) -> Optional[float]:
        """
        Calculate risk/reward ratio.
        
        Args:
            trade: Trade to evaluate
            
        Returns:
            Risk/reward ratio (reward/risk) or None if incomplete data
        """
        if trade.stop_loss is None or trade.take_profit is None:
            return None
        
        if trade.side == "buy":
            risk = abs(trade.entry_price - trade.stop_loss)
            reward = abs(trade.take_profit - trade.entry_price)
        else:  # sell
            risk = abs(trade.stop_loss - trade.entry_price)
            reward = abs(trade.entry_price - trade.take_profit)
        
        if risk == 0:
            return None
        
        return reward / risk
    
    @staticmethod
    def check_trend_alignment(trade: Trade, market_context: MarketContext) -> bool:
        """
        Check if trade aligns with market trend.
        
        Args:
            trade: Trade to evaluate
            market_context: Market context
            
        Returns:
            True if aligned with trend, False otherwise
        """
        if market_context.trend == "bullish" and trade.side == "buy":
            return True
        elif market_context.trend == "bearish" and trade.side == "sell":
            return True
        elif market_context.trend == "neutral":
            return True  # Neutral market, any direction acceptable
        else:
            return False
    
    @staticmethod
    def evaluate_execution_discipline(trade: Trade) -> str:
        """
        Evaluate execution discipline based on risk management.
        
        Args:
            trade: Trade to evaluate
            
        Returns:
            Discipline level: "high", "medium", or "low"
        """
        score = 0
        
        # Has stop loss
        if trade.stop_loss is not None:
            score += 2
        
        # Has take profit
        if trade.take_profit is not None:
            score += 2
        
        # Has trade notes/strategy
        if trade.notes:
            score += 1
        
        # Check if risk/reward is favorable
        rr = TradeEvaluator.calculate_risk_reward(trade)
        if rr is not None and rr >= 2.0:
            score += 2
        elif rr is not None and rr >= 1.0:
            score += 1
        
        # Categorize
        if score >= 5:
            return "high"
        elif score >= 3:
            return "medium"
        else:
            return "low"
    
    @staticmethod
    def evaluate_trade(trade: Trade, market_context: MarketContext) -> TradeEvaluation:
        """
        Perform comprehensive trade evaluation.
        
        Args:
            trade: Trade to evaluate
            market_context: Market context at time of trade
            
        Returns:
            TradeEvaluation object with assessment results
        """
        entry_quality = TradeEvaluator.evaluate_entry_quality(trade, market_context)
        exit_quality = TradeEvaluator.evaluate_exit_quality(trade, market_context)
        risk_reward = TradeEvaluator.calculate_risk_reward(trade)
        aligned = TradeEvaluator.check_trend_alignment(trade, market_context)
        discipline = TradeEvaluator.evaluate_execution_discipline(trade)
        
        # Generate key observations
        observations = []
        
        if entry_quality == "good":
            observations.append("Entry was well-timed and aligned with market structure")
        elif entry_quality == "poor":
            observations.append("Entry could be improved - consider market context")
        
        if not aligned:
            observations.append("Trade was counter-trend - higher risk strategy")
        
        if risk_reward is not None:
            if risk_reward >= 2.0:
                observations.append(f"Favorable risk/reward ratio of {risk_reward:.2f}")
            else:
                observations.append(f"Risk/reward ratio of {risk_reward:.2f} could be improved")
        else:
            observations.append("No stop loss or take profit set - missing risk management")
        
        if discipline == "low":
            observations.append("Execution discipline needs improvement - use stop losses and take profits")
        
        return TradeEvaluation(
            trade_id=trade.trade_id,
            entry_quality=entry_quality,
            exit_quality=exit_quality,
            risk_reward_ratio=risk_reward,
            aligned_with_trend=aligned,
            execution_discipline=discipline,
            key_observations=observations
        )
    
    @staticmethod
    def evaluate_trades(
        trades: List[Trade],
        market_context: MarketContext
    ) -> List[TradeEvaluation]:
        """
        Evaluate multiple trades.
        
        Args:
            trades: List of trades to evaluate
            market_context: Market context for the period
            
        Returns:
            List of TradeEvaluation objects
        """
        return [
            TradeEvaluator.evaluate_trade(trade, market_context)
            for trade in trades
        ]
