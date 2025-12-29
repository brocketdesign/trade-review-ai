# Trade Review AI

An educational trade-analysis system that connects TradingView-compatible market data with the OpenAI API to perform structured, pedagogical reviews of trading activity. Designed for correctness, determinism, and trader learning.

## Features

- **Modular Architecture**: Clean separation of concerns across data ingestion, market analysis, trade evaluation, and AI commentary
- **Market Context Analysis**: Deterministic analysis of trend, structure, volatility, support/resistance levels
- **Trade Evaluation**: Objective assessment of entry/exit quality, risk-reward ratios, and execution discipline
- **AI-Powered Insights**: Pedagogical commentary focused on learning and improvement (not speculation)
- **Flexible Data Sources**: Works with CSV files compatible with TradingView export format

## System Architecture

```
trade-review-ai/
├── src/trade_review_ai/
│   ├── data_ingestion/      # Load market data and trade logs
│   ├── market_analysis/     # Analyze trend, volatility, structure
│   ├── trade_evaluation/    # Evaluate trade quality and discipline
│   ├── ai_integration/      # Generate OpenAI-powered commentary
│   ├── models.py            # Data models (OHLCV, Trade, MarketContext, etc.)
│   ├── config.py            # Configuration management
│   └── analyzer.py          # Main orchestration layer
├── data/                    # Market and trade data files
├── main.py                  # CLI interface
└── requirements.txt         # Python dependencies
```

## Installation

1. **Clone the repository**:
```bash
git clone https://github.com/brocketdesign/trade-review-ai.git
cd trade-review-ai
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Configure API keys**:
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

## Usage

### Quick Start

Run the example analysis:

```bash
python main.py
```

This will analyze the example trades in `data/example_trades.csv` against the market data in `data/example_market_data.csv`.

### Custom Analysis

1. **Prepare your data files**:

   **Market Data CSV** (`market_data.csv`):
   ```csv
   timestamp,open,high,low,close,volume
   2024-01-01 09:00:00,100.50,102.00,100.00,101.50,1000000
   2024-01-01 10:00:00,101.50,103.00,101.00,102.50,1100000
   ...
   ```

   **Trade Log CSV** (`trades.csv`):
   ```csv
   trade_id,timestamp,symbol,side,entry_price,quantity,exit_price,exit_timestamp,stop_loss,take_profit,pnl,notes
   T001,2024-01-01 10:30:00,AAPL,buy,102.00,100,105.50,2024-01-01 14:30:00,100.50,106.00,350.00,Entry near support
   ...
   ```

2. **Use the Python API**:

```python
from datetime import datetime
from trade_review_ai.analyzer import TradeReviewSystem

# Initialize system
system = TradeReviewSystem()

# Run analysis
review = system.analyze_period(
    symbol="AAPL",
    market_data_path="data/market_data.csv",
    trades_path="data/trades.csv",
    start_date=datetime(2024, 1, 1),
    end_date=datetime(2024, 1, 31)
)

# Access results
print(f"Trend: {review.market_context.trend}")
print(f"Win Rate: {review.overall_performance['win_rate']}%")
print(f"AI Commentary:\n{review.ai_commentary}")
```

## Data Format

### Market Data (OHLCV)

Required columns:
- `timestamp`: Date and time (ISO format)
- `open`: Opening price
- `high`: Highest price
- `low`: Lowest price
- `close`: Closing price
- `volume`: Trading volume

### Trade Logs

Required columns:
- `trade_id`: Unique identifier
- `timestamp`: Trade entry time
- `symbol`: Trading symbol
- `side`: "buy" or "sell"
- `entry_price`: Entry price
- `quantity`: Position size

Optional columns:
- `exit_price`: Exit price (if closed)
- `exit_timestamp`: Exit time (if closed)
- `stop_loss`: Stop loss price
- `take_profit`: Take profit price
- `pnl`: Realized profit/loss
- `notes`: Trade notes/strategy

## Analysis Components

### Market Context Analysis

Deterministic technical analysis providing:
- **Trend Direction & Strength**: Linear regression-based trend detection
- **Volatility**: Average True Range (ATR) calculation
- **Support/Resistance**: Swing high/low identification
- **Volume Analysis**: Average trading volume

### Trade Evaluation

Objective assessment including:
- **Entry Quality**: Alignment with trend and market structure
- **Exit Quality**: Profit-taking and loss-cutting discipline
- **Risk/Reward Ratio**: Trade setup quality
- **Execution Discipline**: Use of stops, targets, and position sizing

### AI Commentary

OpenAI-generated pedagogical insights covering:
- Market context summary
- Execution analysis
- Key strengths
- Areas for improvement
- Actionable learning points

## Configuration

Environment variables (`.env`):

```bash
# Required
OPENAI_API_KEY=your_api_key_here

# Optional
OPENAI_MODEL=gpt-4                 # Default: gpt-4
DEFAULT_LOOKBACK_DAYS=30           # Default: 30
MAX_TRADES_PER_ANALYSIS=100        # Default: 100
```

## Design Principles

1. **Modularity**: Each component has a single responsibility
2. **Determinism**: Market analysis uses consistent, reproducible methods
3. **Pedagogy**: Focus on learning, not speculation
4. **Correctness**: Input validation and error handling throughout
5. **Extensibility**: Easy to add new data sources or analysis methods

## Example Output

```
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
Average P&L per Trade: $132.50

AI-GENERATED PEDAGOGICAL COMMENTARY
================================================================================
The trader demonstrated strong alignment with the prevailing bullish trend...
[Detailed educational feedback]
```

## Contributing

Contributions are welcome! Please focus on:
- Maintaining modularity and clean architecture
- Adding deterministic analysis methods
- Improving pedagogical aspects
- Expanding data source compatibility

## License

MIT License - see LICENSE file for details

## Acknowledgments

- Designed for educational purposes
- Uses OpenAI API for commentary generation
- Compatible with TradingView data exports
