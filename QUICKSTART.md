# Trade Review AI - Quick Start Guide

This guide helps you get started with Trade Review AI quickly.

## Prerequisites

- Python 3.8 or higher
- pip package manager
- OpenAI API key

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/brocketdesign/trade-review-ai.git
cd trade-review-ai
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

Alternatively, install as a package:

```bash
pip install -e .
```

### 3. Configure API Key

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:

```
OPENAI_API_KEY=sk-your-actual-api-key-here
OPENAI_MODEL=gpt-4
```

**Getting an OpenAI API Key:**
1. Go to https://platform.openai.com/
2. Sign up or log in
3. Navigate to API Keys
4. Create a new secret key
5. Copy and paste it into your `.env` file

## Running the System

### Quick Test (No API Key Required)

Test the system components without making API calls:

```bash
python test_system.py
```

Expected output:
```
================================================================================
Trade Review AI - Component Testing
================================================================================

Testing Data Ingestion...
  ✓ Loaded 30 market data candles
  ✓ Loaded 5 trades
  ...
ALL TESTS PASSED ✓
```

### Full Analysis (API Key Required)

Run a complete analysis with AI commentary:

```bash
python main.py
```

This will:
1. Load example market data
2. Load example trades
3. Analyze market context (trend, volatility, support/resistance)
4. Evaluate each trade
5. Generate AI-powered pedagogical commentary
6. Display comprehensive results

### Run Examples

Explore various features:

```bash
python examples.py
```

## Using Your Own Data

### Prepare Your Data Files

1. **Market Data CSV** (e.g., `my_market_data.csv`):

```csv
timestamp,open,high,low,close,volume
2024-01-01 09:00:00,100.50,102.00,100.00,101.50,1000000
2024-01-01 10:00:00,101.50,103.00,101.00,102.50,1100000
...
```

2. **Trade Log CSV** (e.g., `my_trades.csv`):

```csv
trade_id,timestamp,symbol,side,entry_price,quantity,exit_price,exit_timestamp,stop_loss,take_profit,pnl,notes
T001,2024-01-01 10:30:00,AAPL,buy,102.00,100,105.50,2024-01-01 14:30:00,100.50,106.00,350.00,Good entry
...
```

### Run Custom Analysis

Create a Python script:

```python
from datetime import datetime
from trade_review_ai.analyzer import TradeReviewSystem

# Initialize
system = TradeReviewSystem()

# Analyze your data
review = system.analyze_period(
    symbol="YOUR_SYMBOL",
    market_data_path="path/to/your/market_data.csv",
    trades_path="path/to/your/trades.csv",
    start_date=datetime(2024, 1, 1),
    end_date=datetime(2024, 1, 31)
)

# View results
print(f"Trend: {review.market_context.trend}")
print(f"Win Rate: {review.overall_performance['win_rate']:.1f}%")
print(f"\nAI Commentary:\n{review.ai_commentary}")
```

## Data Format Reference

### Market Data Columns

| Column | Type | Description | Required |
|--------|------|-------------|----------|
| timestamp | datetime | Candlestick time | Yes |
| open | float | Opening price | Yes |
| high | float | Highest price | Yes |
| low | float | Lowest price | Yes |
| close | float | Closing price | Yes |
| volume | float | Trading volume | Yes |

### Trade Log Columns

| Column | Type | Description | Required |
|--------|------|-------------|----------|
| trade_id | string | Unique identifier | Yes |
| timestamp | datetime | Entry time | Yes |
| symbol | string | Trading symbol | Yes |
| side | string | "buy" or "sell" | Yes |
| entry_price | float | Entry price | Yes |
| quantity | float | Position size | Yes |
| exit_price | float | Exit price | No |
| exit_timestamp | datetime | Exit time | No |
| stop_loss | float | Stop loss price | No |
| take_profit | float | Take profit price | No |
| pnl | float | Profit/loss | No |
| notes | string | Trade notes | No |

## Troubleshooting

### "OPENAI_API_KEY not found"

**Solution:** Make sure you've created a `.env` file with your API key.

### "No module named 'trade_review_ai'"

**Solution:** Install dependencies with `pip install -r requirements.txt`

### "No market data found for period"

**Solution:** Check that your CSV file has data within the specified date range.

### Import errors

**Solution:** Make sure you're running scripts from the project root directory.

## Next Steps

1. **Read the Documentation**
   - `README.md` - Overview and usage
   - `TECHNICAL.md` - Architecture details
   - `CONTRIBUTING.md` - Contribution guidelines

2. **Explore the Code**
   - `src/trade_review_ai/` - Main package
   - `examples.py` - Usage examples
   - `test_system.py` - Test suite

3. **Customize for Your Needs**
   - Modify analysis parameters in `.env`
   - Add custom evaluation criteria
   - Extend with additional data sources

## Getting Help

- **Issues:** https://github.com/brocketdesign/trade-review-ai/issues
- **Documentation:** See README.md and TECHNICAL.md
- **Examples:** Run `python examples.py`

## Important Notes

- **API Costs:** Using OpenAI API incurs costs. Monitor your usage at https://platform.openai.com/usage
- **Data Privacy:** Your data stays local except for the AI commentary generation
- **Educational Use:** This tool is for educational purposes. Always verify analysis results

## Example Output

```
================================================================================
Trade Review AI - Educational Trading Analysis
================================================================================

MARKET CONTEXT
================================================================================
Symbol: AAPL
Trend: BULLISH (strength: 95.23%)
Volatility (ATR): $1.23
Support Levels: $100.50, $102.00, $105.00
Resistance Levels: $110.00, $112.50, $115.00

PERFORMANCE SUMMARY
================================================================================
Total Trades: 5
Win Rate: 75.0% (3 wins, 1 losses)
Total P&L: $530.00

AI-GENERATED PEDAGOGICAL COMMENTARY
================================================================================
The trader demonstrated strong alignment with the prevailing bullish trend,
with 4 out of 5 trades positioned in the direction of market momentum...
[Detailed educational feedback on execution, discipline, and areas for improvement]
```

Happy Trading Analysis! 🚀
