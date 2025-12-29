"""Utility functions for Trade Review AI."""

from typing import List, Dict, Any
from datetime import datetime
import json

from ..models import TradeReview, Trade, TradeEvaluation


def format_trade_review_report(review: TradeReview) -> str:
    """
    Format a TradeReview object into a human-readable text report.
    
    Args:
        review: TradeReview object to format
        
    Returns:
        Formatted text report
    """
    lines = []
    
    # Header
    lines.append("=" * 80)
    lines.append("TRADE REVIEW REPORT")
    lines.append("=" * 80)
    lines.append("")
    
    # Period info
    lines.append(f"Symbol: {review.symbol}")
    lines.append(f"Period: {review.period_start.date()} to {review.period_end.date()}")
    lines.append("")
    
    # Market context
    lines.append("MARKET CONTEXT")
    lines.append("-" * 80)
    mc = review.market_context
    lines.append(f"Trend: {mc.trend.upper()} (strength: {mc.trend_strength:.1%})")
    lines.append(f"Volatility (ATR): ${mc.volatility:.2f}")
    if mc.support_levels:
        lines.append(f"Support Levels: {', '.join([f'${l:.2f}' for l in mc.support_levels])}")
    if mc.resistance_levels:
        lines.append(f"Resistance Levels: {', '.join([f'${l:.2f}' for l in mc.resistance_levels])}")
    lines.append(f"Average Volume: {mc.average_volume:,.0f}")
    lines.append("")
    
    # Performance summary
    lines.append("PERFORMANCE SUMMARY")
    lines.append("-" * 80)
    perf = review.overall_performance
    lines.append(f"Total Trades: {perf['total_trades']}")
    lines.append(f"Closed: {perf['closed_trades']} | Open: {perf['open_trades']}")
    lines.append(f"Win Rate: {perf['win_rate']:.1f}% ({perf['winning_trades']} wins, {perf['losing_trades']} losses)")
    lines.append(f"Total P&L: ${perf['total_pnl']:.2f}")
    lines.append(f"Avg P&L per Trade: ${perf['avg_pnl']:.2f}")
    lines.append(f"Trend Alignment: {perf['trades_with_trend']} with / {perf['trades_against_trend']} against")
    lines.append("")
    
    # Individual trades
    lines.append("TRADE DETAILS")
    lines.append("-" * 80)
    for trade, evaluation in zip(review.trades, review.evaluations):
        lines.append(f"\n{trade.trade_id} - {trade.side.upper()} @ ${trade.entry_price:.2f}")
        if trade.exit_price:
            lines.append(f"  Exit: ${trade.exit_price:.2f} | P&L: ${trade.pnl:.2f}")
        lines.append(f"  Entry: {evaluation.entry_quality} | Discipline: {evaluation.execution_discipline}")
        if evaluation.risk_reward_ratio:
            lines.append(f"  Risk/Reward: {evaluation.risk_reward_ratio:.2f}")
    lines.append("")
    
    # AI Commentary
    lines.append("AI PEDAGOGICAL COMMENTARY")
    lines.append("-" * 80)
    lines.append(review.ai_commentary)
    lines.append("")
    lines.append("=" * 80)
    
    return "\n".join(lines)


def export_to_json(review: TradeReview, filepath: str) -> None:
    """
    Export TradeReview to JSON file.
    
    Args:
        review: TradeReview object to export
        filepath: Path to save JSON file
    """
    # Convert to dict using Pydantic
    data = review.model_dump(mode='json')
    
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2, default=str)


def calculate_additional_metrics(trades: List[Trade]) -> Dict[str, Any]:
    """
    Calculate additional performance metrics.
    
    Args:
        trades: List of trades
        
    Returns:
        Dictionary of additional metrics
    """
    closed_trades = [t for t in trades if t.pnl is not None]
    
    if not closed_trades:
        return {
            "max_drawdown": 0.0,
            "avg_win": 0.0,
            "avg_loss": 0.0,
            "profit_factor": 0.0,
            "largest_win": 0.0,
            "largest_loss": 0.0
        }
    
    wins = [t.pnl for t in closed_trades if t.pnl > 0]
    losses = [abs(t.pnl) for t in closed_trades if t.pnl < 0]
    
    # Calculate metrics
    avg_win = sum(wins) / len(wins) if wins else 0.0
    avg_loss = sum(losses) / len(losses) if losses else 0.0
    
    total_wins = sum(wins)
    total_losses = sum(losses)
    profit_factor = total_wins / total_losses if total_losses > 0 else float('inf')
    
    largest_win = max(wins) if wins else 0.0
    largest_loss = max(losses) if losses else 0.0
    
    # Calculate max drawdown
    cumulative_pnl = 0.0
    peak = 0.0
    max_dd = 0.0
    
    for trade in closed_trades:
        cumulative_pnl += trade.pnl
        if cumulative_pnl > peak:
            peak = cumulative_pnl
        drawdown = peak - cumulative_pnl
        if drawdown > max_dd:
            max_dd = drawdown
    
    return {
        "max_drawdown": max_dd,
        "avg_win": avg_win,
        "avg_loss": avg_loss,
        "profit_factor": profit_factor,
        "largest_win": largest_win,
        "largest_loss": largest_loss
    }


def validate_trade_data(trades: List[Trade]) -> List[str]:
    """
    Validate trade data and return warnings.
    
    Args:
        trades: List of trades to validate
        
    Returns:
        List of warning messages
    """
    warnings = []
    
    for trade in trades:
        # Check for missing risk management
        if trade.stop_loss is None:
            warnings.append(f"Trade {trade.trade_id}: No stop loss defined")
        
        if trade.take_profit is None:
            warnings.append(f"Trade {trade.trade_id}: No take profit defined")
        
        # Check for inconsistent data
        if trade.exit_price is not None and trade.pnl is None:
            warnings.append(f"Trade {trade.trade_id}: Exit price set but P&L not calculated")
        
        if trade.exit_price is not None and trade.exit_timestamp is None:
            warnings.append(f"Trade {trade.trade_id}: Exit price set but no exit timestamp")
        
        # Check for invalid prices
        if trade.side == "buy":
            if trade.stop_loss is not None and trade.stop_loss >= trade.entry_price:
                warnings.append(f"Trade {trade.trade_id}: Buy stop loss should be below entry")
            if trade.take_profit is not None and trade.take_profit <= trade.entry_price:
                warnings.append(f"Trade {trade.trade_id}: Buy take profit should be above entry")
        else:  # sell
            if trade.stop_loss is not None and trade.stop_loss <= trade.entry_price:
                warnings.append(f"Trade {trade.trade_id}: Sell stop loss should be above entry")
            if trade.take_profit is not None and trade.take_profit >= trade.entry_price:
                warnings.append(f"Trade {trade.trade_id}: Sell take profit should be below entry")
    
    return warnings
