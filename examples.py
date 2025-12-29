#!/usr/bin/env python3
"""
Advanced examples demonstrating various features of Trade Review AI.

This script shows:
1. Basic analysis workflow
2. Using utility functions
3. Exporting results to JSON
4. Data validation
5. Custom date ranges
"""

import sys
from datetime import datetime
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from trade_review_ai.analyzer import TradeReviewSystem
from trade_review_ai.data_ingestion import DataIngestion
from trade_review_ai.utils import (
    format_trade_review_report,
    export_to_json,
    calculate_additional_metrics,
    validate_trade_data
)


def example_basic_analysis():
    """Example 1: Basic analysis workflow."""
    print("\n" + "=" * 80)
    print("EXAMPLE 1: Basic Analysis Workflow")
    print("=" * 80)
    
    # Note: This requires OPENAI_API_KEY to be set
    # For testing without API key, see test_system.py
    
    try:
        system = TradeReviewSystem()
        
        review = system.analyze_period(
            symbol="AAPL",
            market_data_path="data/example_market_data.csv",
            trades_path="data/example_trades.csv",
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 5)
        )
        
        print("\n✓ Analysis complete!")
        print(f"Trend: {review.market_context.trend}")
        print(f"Win Rate: {review.overall_performance['win_rate']:.1f}%")
        
    except ValueError as e:
        print(f"\nNote: {e}")
        print("Set OPENAI_API_KEY in .env to run this example")


def example_data_validation():
    """Example 2: Validate trade data for issues."""
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Data Validation")
    print("=" * 80)
    
    ingestion = DataIngestion()
    trades = ingestion.load_trades("data/example_trades.csv")
    
    warnings = validate_trade_data(trades)
    
    if warnings:
        print(f"\n⚠ Found {len(warnings)} warnings:")
        for warning in warnings:
            print(f"  - {warning}")
    else:
        print("\n✓ No data validation warnings")


def example_additional_metrics():
    """Example 3: Calculate advanced performance metrics."""
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Additional Performance Metrics")
    print("=" * 80)
    
    ingestion = DataIngestion()
    trades = ingestion.load_trades("data/example_trades.csv")
    
    metrics = calculate_additional_metrics(trades)
    
    print(f"\nAdvanced Metrics:")
    print(f"  Max Drawdown: ${metrics['max_drawdown']:.2f}")
    print(f"  Average Win: ${metrics['avg_win']:.2f}")
    print(f"  Average Loss: ${metrics['avg_loss']:.2f}")
    print(f"  Profit Factor: {metrics['profit_factor']:.2f}")
    print(f"  Largest Win: ${metrics['largest_win']:.2f}")
    print(f"  Largest Loss: ${metrics['largest_loss']:.2f}")


def example_custom_date_range():
    """Example 4: Analyze specific date ranges."""
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Custom Date Range Analysis")
    print("=" * 80)
    
    ingestion = DataIngestion()
    
    # Load all data
    market_data = ingestion.load_market_data("data/example_market_data.csv")
    trades = ingestion.load_trades("data/example_trades.csv")
    
    # Filter to specific dates
    start = datetime(2024, 1, 2)
    end = datetime(2024, 1, 4)
    
    filtered_market = ingestion.filter_by_date_range(market_data, start, end)
    filtered_trades = ingestion.filter_by_date_range(trades, start, end)
    
    print(f"\nDate Range: {start.date()} to {end.date()}")
    print(f"  Market Data Candles: {len(filtered_market)}")
    print(f"  Trades: {len(filtered_trades)}")


def example_component_usage():
    """Example 5: Using individual components."""
    print("\n" + "=" * 80)
    print("EXAMPLE 5: Using Individual Components")
    print("=" * 80)
    
    from trade_review_ai.market_analysis import MarketAnalyzer
    from trade_review_ai.trade_evaluation import TradeEvaluator
    
    ingestion = DataIngestion()
    analyzer = MarketAnalyzer()
    evaluator = TradeEvaluator()
    
    # Load data
    market_data = ingestion.load_market_data("data/example_market_data.csv")
    trades = ingestion.load_trades("data/example_trades.csv")
    
    # Analyze market independently
    trend, strength = analyzer.calculate_trend(market_data)
    volatility = analyzer.calculate_volatility(market_data)
    
    print(f"\nMarket Analysis:")
    print(f"  Trend: {trend} (strength: {strength:.1%})")
    print(f"  Volatility: ${volatility:.2f}")
    
    # Analyze market context
    context = analyzer.analyze_market_context(
        symbol="AAPL",
        ohlcv_data=market_data,
        start_date=market_data[0].timestamp,
        end_date=market_data[-1].timestamp
    )
    
    # Evaluate individual trade
    trade = trades[0]
    evaluation = evaluator.evaluate_trade(trade, context)
    
    print(f"\nTrade Evaluation (Trade {trade.trade_id}):")
    print(f"  Entry Quality: {evaluation.entry_quality}")
    print(f"  Execution Discipline: {evaluation.execution_discipline}")
    print(f"  Trend Aligned: {evaluation.aligned_with_trend}")


def main():
    """Run all examples."""
    print("=" * 80)
    print("Trade Review AI - Advanced Examples")
    print("=" * 80)
    
    # Run examples that don't require API key
    example_data_validation()
    example_additional_metrics()
    example_custom_date_range()
    example_component_usage()
    
    # Run API-dependent example
    example_basic_analysis()
    
    print("\n" + "=" * 80)
    print("Examples complete!")
    print("=" * 80)
    print("\nFor more information, see README.md")


if __name__ == "__main__":
    main()
