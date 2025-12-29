#!/usr/bin/env python3
"""
Command-line interface for Trade Review AI.

This script demonstrates how to use the trade review system to analyze
trading performance over a specified period.
"""

import sys
from datetime import datetime
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from trade_review_ai.analyzer import TradeReviewSystem
from trade_review_ai.config import load_config


def main():
    """Run trade review analysis."""
    print("=" * 80)
    print("Trade Review AI - Educational Trading Analysis")
    print("=" * 80)
    print()
    
    try:
        # Load configuration
        print("Loading configuration...")
        config = load_config()
        print(f"✓ Using model: {config.openai_model}")
        print()
        
        # Initialize system
        print("Initializing Trade Review System...")
        system = TradeReviewSystem(config)
        print("✓ System initialized")
        print()
        
        # Define analysis parameters
        symbol = "AAPL"
        market_data_path = "data/example_market_data.csv"
        trades_path = "data/example_trades.csv"
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 5)
        
        print(f"Analysis Parameters:")
        print(f"  Symbol: {symbol}")
        print(f"  Period: {start_date.date()} to {end_date.date()}")
        print(f"  Market Data: {market_data_path}")
        print(f"  Trades Data: {trades_path}")
        print()
        
        # Run analysis
        print("Running analysis...")
        print("-" * 80)
        review = system.analyze_period(
            symbol=symbol,
            market_data_path=market_data_path,
            trades_path=trades_path,
            start_date=start_date,
            end_date=end_date
        )
        print("-" * 80)
        print()
        
        # Display results
        print("MARKET CONTEXT")
        print("=" * 80)
        print(f"Symbol: {review.market_context.symbol}")
        print(f"Trend: {review.market_context.trend.upper()} (strength: {review.market_context.trend_strength:.2%})")
        print(f"Volatility (ATR): ${review.market_context.volatility:.2f}")
        print(f"Support Levels: {', '.join([f'${level:.2f}' for level in review.market_context.support_levels])}")
        print(f"Resistance Levels: {', '.join([f'${level:.2f}' for level in review.market_context.resistance_levels])}")
        print(f"Average Volume: {review.market_context.average_volume:,.0f}")
        print()
        
        print("PERFORMANCE SUMMARY")
        print("=" * 80)
        perf = review.overall_performance
        print(f"Total Trades: {perf['total_trades']}")
        print(f"Closed Trades: {perf['closed_trades']} | Open Trades: {perf['open_trades']}")
        print(f"Win Rate: {perf['win_rate']:.1f}% ({perf['winning_trades']} wins, {perf['losing_trades']} losses)")
        print(f"Total P&L: ${perf['total_pnl']:.2f}")
        print(f"Average P&L per Trade: ${perf['avg_pnl']:.2f}")
        print(f"Trades with Trend: {perf['trades_with_trend']} | Against Trend: {perf['trades_against_trend']}")
        print(f"High Discipline Trades: {perf['high_discipline_trades']}")
        print(f"Good Entry Trades: {perf['good_entry_trades']}")
        print()
        
        print("INDIVIDUAL TRADE EVALUATIONS")
        print("=" * 80)
        for trade, evaluation in zip(review.trades, review.evaluations):
            status = "CLOSED" if trade.exit_price else "OPEN"
            pnl_str = f"${trade.pnl:.2f}" if trade.pnl is not None else "N/A"
            
            print(f"\nTrade {trade.trade_id} ({status}) - {trade.side.upper()}")
            print(f"  Entry: ${trade.entry_price:.2f} @ {trade.timestamp.strftime('%Y-%m-%d %H:%M')}")
            if trade.exit_price:
                print(f"  Exit: ${trade.exit_price:.2f} @ {trade.exit_timestamp.strftime('%Y-%m-%d %H:%M')}")
            print(f"  P&L: {pnl_str}")
            print(f"  Entry Quality: {evaluation.entry_quality}")
            if evaluation.exit_quality:
                print(f"  Exit Quality: {evaluation.exit_quality}")
            print(f"  Risk/Reward: {evaluation.risk_reward_ratio:.2f}" if evaluation.risk_reward_ratio else "  Risk/Reward: N/A")
            print(f"  Trend Alignment: {'Yes' if evaluation.aligned_with_trend else 'No'}")
            print(f"  Execution Discipline: {evaluation.execution_discipline}")
            if evaluation.key_observations:
                print(f"  Observations:")
                for obs in evaluation.key_observations:
                    print(f"    - {obs}")
        print()
        
        print("AI-GENERATED PEDAGOGICAL COMMENTARY")
        print("=" * 80)
        print(review.ai_commentary)
        print()
        
        print("=" * 80)
        print("Analysis complete!")
        print("=" * 80)
        
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        print("\nMake sure the data files exist:")
        print("  - data/example_market_data.csv")
        print("  - data/example_trades.csv")
        sys.exit(1)
    
    except ValueError as e:
        print(f"ERROR: {e}")
        print("\nMake sure your .env file is configured with OPENAI_API_KEY")
        print("See .env.example for reference")
        sys.exit(1)
    
    except Exception as e:
        print(f"ERROR: An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
