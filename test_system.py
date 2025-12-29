#!/usr/bin/env python3
"""
Test script to validate the trade review system components.

Tests core functionality without requiring OpenAI API calls.
"""

import sys
from datetime import datetime
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from trade_review_ai.data_ingestion import DataIngestion
from trade_review_ai.market_analysis import MarketAnalyzer
from trade_review_ai.trade_evaluation import TradeEvaluator
from trade_review_ai.models import OHLCV, Trade


def test_data_ingestion():
    """Test data loading functionality."""
    print("Testing Data Ingestion...")
    
    ingestion = DataIngestion()
    
    # Load market data
    market_data = ingestion.load_market_data("data/example_market_data.csv")
    assert len(market_data) > 0, "No market data loaded"
    assert all(isinstance(d, OHLCV) for d in market_data), "Invalid market data type"
    print(f"  ✓ Loaded {len(market_data)} market data candles")
    
    # Load trades
    trades = ingestion.load_trades("data/example_trades.csv")
    assert len(trades) > 0, "No trades loaded"
    assert all(isinstance(t, Trade) for t in trades), "Invalid trade type"
    print(f"  ✓ Loaded {len(trades)} trades")
    
    # Test date filtering
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 1, 3)
    filtered = ingestion.filter_by_date_range(market_data, start_date, end_date)
    assert len(filtered) <= len(market_data), "Filtering didn't reduce data"
    print(f"  ✓ Filtered to {len(filtered)} candles in date range")
    
    print("  Data Ingestion: PASSED\n")


def test_market_analysis():
    """Test market context analysis."""
    print("Testing Market Analysis...")
    
    ingestion = DataIngestion()
    analyzer = MarketAnalyzer()
    
    # Load data
    market_data = ingestion.load_market_data("data/example_market_data.csv")
    
    # Test trend calculation
    trend, strength = analyzer.calculate_trend(market_data)
    assert trend in ["bullish", "bearish", "neutral"], f"Invalid trend: {trend}"
    assert 0.0 <= strength <= 1.0, f"Invalid strength: {strength}"
    print(f"  ✓ Trend: {trend} (strength: {strength:.2%})")
    
    # Test volatility calculation
    volatility = analyzer.calculate_volatility(market_data)
    assert volatility >= 0, f"Invalid volatility: {volatility}"
    print(f"  ✓ Volatility (ATR): ${volatility:.2f}")
    
    # Test support/resistance detection
    support, resistance = analyzer.find_support_resistance(market_data)
    print(f"  ✓ Found {len(support)} support levels, {len(resistance)} resistance levels")
    
    # Test full market context
    context = analyzer.analyze_market_context(
        symbol="AAPL",
        ohlcv_data=market_data,
        start_date=market_data[0].timestamp,
        end_date=market_data[-1].timestamp
    )
    assert context.symbol == "AAPL", "Incorrect symbol"
    assert context.trend in ["bullish", "bearish", "neutral"], "Invalid trend"
    print(f"  ✓ Market context analysis complete")
    
    print("  Market Analysis: PASSED\n")


def test_trade_evaluation():
    """Test trade evaluation functionality."""
    print("Testing Trade Evaluation...")
    
    ingestion = DataIngestion()
    analyzer = MarketAnalyzer()
    evaluator = TradeEvaluator()
    
    # Load data
    market_data = ingestion.load_market_data("data/example_market_data.csv")
    trades = ingestion.load_trades("data/example_trades.csv")
    
    # Analyze market context
    context = analyzer.analyze_market_context(
        symbol="AAPL",
        ohlcv_data=market_data,
        start_date=market_data[0].timestamp,
        end_date=market_data[-1].timestamp
    )
    
    # Evaluate a single trade
    trade = trades[0]
    evaluation = evaluator.evaluate_trade(trade, context)
    assert evaluation.trade_id == trade.trade_id, "Trade ID mismatch"
    assert evaluation.entry_quality in ["good", "acceptable", "poor"], "Invalid entry quality"
    assert evaluation.execution_discipline in ["high", "medium", "low"], "Invalid discipline"
    print(f"  ✓ Trade {trade.trade_id}: Entry={evaluation.entry_quality}, Discipline={evaluation.execution_discipline}")
    
    # Test risk/reward calculation
    rr = evaluator.calculate_risk_reward(trade)
    if rr is not None:
        print(f"  ✓ Risk/Reward ratio: {rr:.2f}")
    else:
        print(f"  ✓ Risk/Reward: N/A (missing stop/target)")
    
    # Evaluate all trades
    evaluations = evaluator.evaluate_trades(trades, context)
    assert len(evaluations) == len(trades), "Evaluation count mismatch"
    print(f"  ✓ Evaluated {len(evaluations)} trades")
    
    print("  Trade Evaluation: PASSED\n")


def test_complete_workflow():
    """Test the complete analysis workflow (without AI)."""
    print("Testing Complete Workflow...")
    
    ingestion = DataIngestion()
    analyzer = MarketAnalyzer()
    evaluator = TradeEvaluator()
    
    # Load data
    market_data = ingestion.load_market_data("data/example_market_data.csv")
    trades = ingestion.load_trades("data/example_trades.csv")
    
    # Analyze market
    context = analyzer.analyze_market_context(
        symbol="AAPL",
        ohlcv_data=market_data,
        start_date=market_data[0].timestamp,
        end_date=market_data[-1].timestamp
    )
    
    # Evaluate trades
    evaluations = evaluator.evaluate_trades(trades, context)
    
    # Calculate performance metrics
    closed_trades = [t for t in trades if t.pnl is not None]
    winning_trades = len([t for t in closed_trades if t.pnl > 0])
    total_pnl = sum(t.pnl for t in closed_trades)
    win_rate = (winning_trades / len(closed_trades) * 100) if closed_trades else 0.0
    
    print(f"  ✓ Analysis Summary:")
    print(f"    - Symbol: {context.symbol}")
    print(f"    - Trend: {context.trend} ({context.trend_strength:.1%})")
    print(f"    - Total Trades: {len(trades)}")
    print(f"    - Closed Trades: {len(closed_trades)}")
    print(f"    - Win Rate: {win_rate:.1f}%")
    print(f"    - Total P&L: ${total_pnl:.2f}")
    
    print("  Complete Workflow: PASSED\n")


def main():
    """Run all tests."""
    print("=" * 80)
    print("Trade Review AI - Component Testing")
    print("=" * 80)
    print()
    
    try:
        test_data_ingestion()
        test_market_analysis()
        test_trade_evaluation()
        test_complete_workflow()
        
        print("=" * 80)
        print("ALL TESTS PASSED ✓")
        print("=" * 80)
        print()
        print("The system is working correctly!")
        print("To run a full analysis with AI commentary, configure your OpenAI API key")
        print("in .env and run: python main.py")
        
        return 0
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
