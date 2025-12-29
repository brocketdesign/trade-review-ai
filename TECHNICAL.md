# Trade Review AI - Technical Documentation

## Architecture Overview

The system follows a clean, modular architecture with clear separation of concerns:

```
┌─────────────────┐
│   Main Entry    │
│   (main.py)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  TradeReview    │
│    System       │  ◄── Orchestrates all components
└────────┬────────┘
         │
    ┌────┴────┬────────┬────────┬─────────┐
    ▼         ▼        ▼        ▼         ▼
┌────────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌────────┐
│ Data   │ │Market│ │Trade │ │  AI  │ │ Utils  │
│Ingest  │ │Analy │ │Eval  │ │Integ │ │        │
└────────┘ └──────┘ └──────┘ └──────┘ └────────┘
```

## Component Details

### 1. Data Ingestion (`data_ingestion/`)

**Purpose**: Load and validate market data and trade logs

**Key Classes**:
- `DataIngestion`: Main class for loading CSV files

**Methods**:
- `load_market_data()`: Loads OHLCV data from CSV
- `load_trades()`: Loads trade logs from CSV
- `filter_by_date_range()`: Filters data to specific period

**Data Validation**:
- Checks for required columns
- Validates data types
- Handles missing values gracefully

### 2. Market Analysis (`market_analysis/`)

**Purpose**: Derive market context using deterministic technical analysis

**Key Classes**:
- `MarketAnalyzer`: Performs technical analysis

**Methods**:
- `calculate_trend()`: Linear regression-based trend detection
- `calculate_volatility()`: ATR (Average True Range) calculation
- `find_support_resistance()`: Swing high/low detection
- `analyze_market_context()`: Complete market analysis

**Algorithms**:
- **Trend Detection**: Uses linear regression on close prices
  - R² value determines trend strength
  - Slope normalized by price determines direction
  
- **Volatility**: Average True Range (ATR)
  ```
  TR = max(high - low, |high - prev_close|, |low - prev_close|)
  ATR = average(TR)
  ```

- **Support/Resistance**: Swing point detection
  - Swing low: price lower than both neighbors
  - Swing high: price higher than both neighbors
  - Clustering: Groups levels within 1% of each other

### 3. Trade Evaluation (`trade_evaluation/`)

**Purpose**: Evaluate trade quality based on objective criteria

**Key Classes**:
- `TradeEvaluator`: Evaluates individual trades

**Methods**:
- `evaluate_entry_quality()`: Scores entry timing and positioning
- `evaluate_exit_quality()`: Scores exit execution
- `calculate_risk_reward()`: Computes R:R ratio
- `check_trend_alignment()`: Validates trend following
- `evaluate_execution_discipline()`: Assesses risk management

**Scoring System**:

Entry Quality:
- +2 points: Aligned with trend
- +2 points: Near support (buy) or resistance (sell)
- -1 point: Counter-trend
- Result: "good" (≥3), "acceptable" (≥1), "poor" (<1)

Execution Discipline:
- +2 points: Has stop loss
- +2 points: Has take profit
- +1 point: Has trade notes
- +2 points: R:R ratio ≥ 2.0
- +1 point: R:R ratio ≥ 1.0
- Result: "high" (≥5), "medium" (≥3), "low" (<3)

### 4. AI Integration (`ai_integration/`)

**Purpose**: Generate pedagogical commentary via OpenAI API

**Key Classes**:
- `AICommentaryGenerator`: Interfaces with OpenAI

**Methods**:
- `generate_commentary()`: Creates educational analysis

**Prompt Engineering**:
- Low temperature (0.3) for consistency
- Structured sections: context, execution, strengths, improvements, learning
- Evidence-based (references specific trades)
- Non-speculative (no future predictions)

### 5. Models (`models.py`)

**Purpose**: Define data structures using Pydantic

**Key Models**:
- `OHLCV`: Candlestick data
- `Trade`: Individual trade record
- `MarketContext`: Market analysis results
- `TradeEvaluation`: Trade assessment
- `TradeReview`: Complete review package

**Benefits**:
- Type validation
- Serialization/deserialization
- Clear documentation
- IDE autocomplete support

### 6. Configuration (`config.py`)

**Purpose**: Manage application settings

**Configuration Sources**:
1. Environment variables
2. .env file
3. Defaults

**Settings**:
- `openai_api_key`: API authentication
- `openai_model`: Model selection (default: gpt-4)
- `default_lookback_days`: Analysis period
- `max_trades_per_analysis`: Batch size limit

### 7. Utilities (`utils/`)

**Purpose**: Helper functions and utilities

**Functions**:
- `format_trade_review_report()`: Text formatting
- `export_to_json()`: JSON export
- `calculate_additional_metrics()`: Advanced metrics
- `validate_trade_data()`: Data quality checks

## Data Flow

```
1. Load Configuration
   ├── Environment variables
   └── .env file

2. Load Data
   ├── Market data (OHLCV) from CSV
   └── Trade logs from CSV

3. Filter Data
   └── Date range filtering

4. Analyze Market
   ├── Calculate trend
   ├── Calculate volatility
   └── Find support/resistance

5. Evaluate Trades
   ├── Assess entry quality
   ├── Assess exit quality
   ├── Calculate risk/reward
   └── Check execution discipline

6. Generate Commentary
   ├── Build context prompt
   ├── Call OpenAI API
   └── Format response

7. Package Results
   └── Create TradeReview object

8. Output
   ├── Console display
   ├── JSON export
   └── Text report
```

## Error Handling

The system implements comprehensive error handling:

1. **Data Loading**:
   - FileNotFoundError for missing files
   - ValueError for invalid formats

2. **Configuration**:
   - ValueError for missing API keys
   - Validation for configuration values

3. **API Calls**:
   - Exception handling for OpenAI errors
   - Graceful degradation with error messages

4. **Data Validation**:
   - Type checking via Pydantic
   - Range validation
   - Required field validation

## Performance Considerations

1. **Data Processing**:
   - Uses pandas for efficient CSV loading
   - NumPy for numerical computations
   - Linear time complexity O(n) for most operations

2. **Memory Usage**:
   - Filters data early to reduce memory footprint
   - Processes trades sequentially
   - No unnecessary data duplication

3. **API Efficiency**:
   - Single API call per analysis
   - Batches all trades in one prompt
   - Low temperature reduces token usage

## Extensibility

The modular design allows easy extension:

1. **New Data Sources**:
   - Implement new loaders in `data_ingestion/`
   - Maintain OHLCV and Trade model interfaces

2. **Additional Analysis**:
   - Add methods to `MarketAnalyzer`
   - Update `MarketContext` model

3. **Custom Evaluations**:
   - Extend `TradeEvaluator`
   - Add fields to `TradeEvaluation`

4. **Alternative AI Providers**:
   - Create new generator in `ai_integration/`
   - Implement same interface

## Testing Strategy

1. **Unit Tests**: Test individual components
2. **Integration Tests**: Test component interactions
3. **End-to-End Tests**: Test complete workflows
4. **Data Validation**: Test edge cases and invalid inputs

See `test_system.py` for examples.

## Security Considerations

1. **API Key Management**:
   - Never commit .env files
   - Use environment variables
   - Rotate keys regularly

2. **Data Privacy**:
   - No data sent to external services except OpenAI
   - User data stays local

3. **Input Validation**:
   - Pydantic validates all inputs
   - File path validation
   - Type checking

## Future Enhancements

Potential improvements:

1. **Data Sources**:
   - Direct TradingView API integration
   - Real-time data streaming
   - Multiple broker support

2. **Analysis**:
   - Machine learning for pattern recognition
   - Backtesting capabilities
   - Portfolio-level analysis

3. **Visualization**:
   - Chart generation
   - Interactive dashboards
   - Trade replay

4. **Reporting**:
   - PDF export
   - Email reports
   - Custom templates
