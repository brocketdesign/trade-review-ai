#!/usr/bin/env python3
"""
Trade Review AI - Web Application

A professional Flask web application for visualizing trade analyses
and performance metrics with live market data support.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from trade_review_ai.analyzer import TradeReviewSystem
from trade_review_ai.config import load_config
from trade_review_ai.live_data import LiveDataService, ManualTradeManager
from trade_review_ai.models import OHLCV

app = Flask(__name__)
CORS(app)

# Global cache for analysis results
_analysis_cache = {}

# Global manual trade manager
_trade_manager = ManualTradeManager()


def get_trade_review_system():
    """Initialize and return the trade review system."""
    config = load_config()
    return TradeReviewSystem(config)


def run_analysis_with_live_data(symbol: str, start_date: datetime, end_date: datetime, interval: str = '1d'):
    """Run analysis using live market data and manual trades."""
    cache_key = f"live_{symbol}_{start_date}_{end_date}_{interval}"
    
    if cache_key not in _analysis_cache:
        # Fetch live market data
        market_data = LiveDataService.fetch_market_data(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            interval=interval
        )
        
        if not market_data:
            raise ValueError(f"No market data found for {symbol}")
        
        # Get manual trades for this symbol and period
        trades = _trade_manager.get_trades(symbol=symbol, start_date=start_date, end_date=end_date)
        
        # Use the system to analyze
        system = get_trade_review_system()
        
        # Analyze market context
        market_context = system.market_analyzer.analyze_market_context(
            symbol=symbol,
            ohlcv_data=market_data,
            start_date=start_date,
            end_date=end_date
        )
        
        # If we have trades, evaluate them
        evaluations = []
        if trades:
            evaluations = system.trade_evaluator.evaluate_trades(trades, market_context)
        
        # Calculate performance metrics
        performance_metrics = system._calculate_performance_metrics(trades, evaluations) if trades else {
            "total_trades": 0,
            "closed_trades": 0,
            "open_trades": 0,
            "winning_trades": 0,
            "losing_trades": 0,
            "win_rate": 0.0,
            "total_pnl": 0.0,
            "avg_pnl": 0.0,
            "trades_with_trend": 0,
            "trades_against_trend": 0,
            "high_discipline_trades": 0,
            "good_entry_trades": 0
        }
        
        # Generate AI commentary if we have trades
        ai_commentary = "No trades to analyze. Add trades manually to get AI-generated insights."
        if trades:
            ai_commentary = system.ai_generator.generate_commentary(
                market_context=market_context,
                trades=trades,
                evaluations=evaluations,
                performance_metrics=performance_metrics
            )
        
        from trade_review_ai.models import TradeReview
        review = TradeReview(
            period_start=start_date,
            period_end=end_date,
            symbol=symbol,
            market_context=market_context,
            trades=trades,
            evaluations=evaluations,
            ai_commentary=ai_commentary,
            overall_performance=performance_metrics
        )
        
        # Store in cache along with market data
        _analysis_cache[cache_key] = {
            'review': review,
            'market_data': market_data
        }
    
    return _analysis_cache[cache_key]


def run_analysis(symbol: str, start_date: datetime, end_date: datetime):
    """Run analysis and cache results."""
    cache_key = f"{symbol}_{start_date}_{end_date}"
    
    if cache_key not in _analysis_cache:
        system = get_trade_review_system()
        
        market_data_path = str(Path(__file__).parent.parent / "data" / "example_market_data.csv")
        trades_path = str(Path(__file__).parent.parent / "data" / "example_trades.csv")
        
        review = system.analyze_period(
            symbol=symbol,
            market_data_path=market_data_path,
            trades_path=trades_path,
            start_date=start_date,
            end_date=end_date
        )
        _analysis_cache[cache_key] = review
    
    return _analysis_cache[cache_key]


@app.route('/')
def index():
    """Render the main dashboard."""
    return render_template('index.html')


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Run analysis with provided parameters."""
    try:
        data = request.get_json() or {}
        symbol = data.get('symbol', 'AAPL')
        start_date = datetime.fromisoformat(data.get('start_date', '2024-01-01'))
        end_date = datetime.fromisoformat(data.get('end_date', '2024-01-05'))
        
        review = run_analysis(symbol, start_date, end_date)
        
        return jsonify({
            'success': True,
            'data': review.model_dump(mode='json')
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/market-context')
def get_market_context():
    """Get market context data."""
    try:
        symbol = request.args.get('symbol', 'AAPL')
        start_date = datetime.fromisoformat(request.args.get('start_date', '2024-01-01'))
        end_date = datetime.fromisoformat(request.args.get('end_date', '2024-01-05'))
        
        review = run_analysis(symbol, start_date, end_date)
        
        return jsonify({
            'success': True,
            'data': review.market_context.model_dump(mode='json')
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/trades')
def get_trades():
    """Get trades data."""
    try:
        symbol = request.args.get('symbol', 'AAPL')
        start_date = datetime.fromisoformat(request.args.get('start_date', '2024-01-01'))
        end_date = datetime.fromisoformat(request.args.get('end_date', '2024-01-05'))
        
        review = run_analysis(symbol, start_date, end_date)
        
        trades_data = [trade.model_dump(mode='json') for trade in review.trades]
        
        return jsonify({
            'success': True,
            'data': trades_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/evaluations')
def get_evaluations():
    """Get trade evaluations data."""
    try:
        symbol = request.args.get('symbol', 'AAPL')
        start_date = datetime.fromisoformat(request.args.get('start_date', '2024-01-01'))
        end_date = datetime.fromisoformat(request.args.get('end_date', '2024-01-05'))
        
        review = run_analysis(symbol, start_date, end_date)
        
        evaluations_data = [eval.model_dump(mode='json') for eval in review.evaluations]
        
        return jsonify({
            'success': True,
            'data': evaluations_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/performance')
def get_performance():
    """Get overall performance metrics."""
    try:
        symbol = request.args.get('symbol', 'AAPL')
        start_date = datetime.fromisoformat(request.args.get('start_date', '2024-01-01'))
        end_date = datetime.fromisoformat(request.args.get('end_date', '2024-01-05'))
        
        review = run_analysis(symbol, start_date, end_date)
        
        return jsonify({
            'success': True,
            'data': review.overall_performance
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/ai-commentary')
def get_ai_commentary():
    """Get AI-generated commentary."""
    try:
        symbol = request.args.get('symbol', 'AAPL')
        start_date = datetime.fromisoformat(request.args.get('start_date', '2024-01-01'))
        end_date = datetime.fromisoformat(request.args.get('end_date', '2024-01-05'))
        
        review = run_analysis(symbol, start_date, end_date)
        
        return jsonify({
            'success': True,
            'data': {
                'commentary': review.ai_commentary
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/market-data')
def get_market_data():
    """Get raw market data for charting."""
    try:
        import pandas as pd
        
        market_data_path = Path(__file__).parent.parent / "data" / "example_market_data.csv"
        df = pd.read_csv(market_data_path)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        start_date = request.args.get('start_date', '2024-01-01')
        end_date = request.args.get('end_date', '2024-01-05')
        
        mask = (df['timestamp'] >= start_date) & (df['timestamp'] <= end_date + ' 23:59:59')
        filtered_df = df.loc[mask]
        
        return jsonify({
            'success': True,
            'data': filtered_df.to_dict(orient='records')
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/dashboard-summary')
def get_dashboard_summary():
    """Get complete dashboard summary with all data."""
    try:
        symbol = request.args.get('symbol', 'AAPL')
        start_date = datetime.fromisoformat(request.args.get('start_date', '2024-01-01'))
        end_date = datetime.fromisoformat(request.args.get('end_date', '2024-01-05'))
        
        review = run_analysis(symbol, start_date, end_date)
        
        # Get market data for chart
        import pandas as pd
        market_data_path = Path(__file__).parent.parent / "data" / "example_market_data.csv"
        df = pd.read_csv(market_data_path)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        mask = (df['timestamp'] >= str(start_date.date())) & (df['timestamp'] <= str(end_date.date()) + ' 23:59:59')
        filtered_df = df.loc[mask]
        
        return jsonify({
            'success': True,
            'data': {
                'review': review.model_dump(mode='json'),
                'market_data': filtered_df.to_dict(orient='records')
            }
        })
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 400


# ==================== LIVE DATA ENDPOINTS ====================

@app.route('/api/live/market-data')
def get_live_market_data():
    """Fetch live market data for a symbol."""
    try:
        symbol = request.args.get('symbol', 'AAPL')
        period = request.args.get('period')  # e.g., '1mo', '3mo', '1y'
        interval = request.args.get('interval', '1d')  # e.g., '1m', '5m', '1h', '1d'
        
        # Parse dates if provided
        start_date = None
        end_date = None
        if request.args.get('start_date'):
            start_date = datetime.fromisoformat(request.args.get('start_date'))
        if request.args.get('end_date'):
            end_date = datetime.fromisoformat(request.args.get('end_date'))
        
        market_data = LiveDataService.fetch_market_data(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            period=period,
            interval=interval
        )
        
        # Convert to dict format
        data_list = [ohlcv.model_dump(mode='json') for ohlcv in market_data]
        
        return jsonify({
            'success': True,
            'symbol': symbol.upper(),
            'data': data_list
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/live/symbol-info')
def get_symbol_info():
    """Get information about a symbol."""
    try:
        symbol = request.args.get('symbol', 'AAPL')
        info = LiveDataService.get_symbol_info(symbol)
        
        return jsonify({
            'success': True,
            'data': info
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/live/search')
def search_symbols():
    """Search for symbols."""
    try:
        query = request.args.get('q', '')
        limit = int(request.args.get('limit', 10))
        
        results = LiveDataService.search_symbols(query, limit)
        
        return jsonify({
            'success': True,
            'data': results
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/live/validate')
def validate_symbol():
    """Validate if a symbol exists."""
    try:
        symbol = request.args.get('symbol', '')
        is_valid = LiveDataService.validate_symbol(symbol)
        
        return jsonify({
            'success': True,
            'symbol': symbol.upper(),
            'valid': is_valid
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/live/analyze')
def analyze_live():
    """Run analysis with live market data."""
    try:
        symbol = request.args.get('symbol', 'AAPL')
        period = request.args.get('period', '1mo')
        interval = request.args.get('interval', '1d')
        
        # Parse dates if provided, otherwise use period
        start_date = None
        end_date = datetime.now()
        
        if request.args.get('start_date'):
            start_date = datetime.fromisoformat(request.args.get('start_date'))
        if request.args.get('end_date'):
            end_date = datetime.fromisoformat(request.args.get('end_date'))
        
        # If no start date, calculate from period
        if not start_date:
            period_days = {
                '1d': 1, '5d': 5, '1w': 7, '1mo': 30, '3mo': 90,
                '6mo': 180, '1y': 365, '2y': 730, '5y': 1825
            }
            days = period_days.get(period, 30)
            start_date = end_date - timedelta(days=days)
        
        result = run_analysis_with_live_data(symbol, start_date, end_date, interval)
        
        # Convert market data to dict format
        market_data_list = [ohlcv.model_dump(mode='json') for ohlcv in result['market_data']]
        
        return jsonify({
            'success': True,
            'data': {
                'review': result['review'].model_dump(mode='json'),
                'market_data': market_data_list
            }
        })
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 400


# ==================== MANUAL TRADE ENDPOINTS ====================

@app.route('/api/trades/manual', methods=['GET'])
def get_manual_trades():
    """Get all manual trades."""
    try:
        symbol = request.args.get('symbol')
        start_date = None
        end_date = None
        
        if request.args.get('start_date'):
            start_date = datetime.fromisoformat(request.args.get('start_date'))
        if request.args.get('end_date'):
            end_date = datetime.fromisoformat(request.args.get('end_date'))
        
        trades = _trade_manager.get_trades(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date
        )
        
        return jsonify({
            'success': True,
            'data': [trade.model_dump(mode='json') for trade in trades]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/trades/manual', methods=['POST'])
def add_manual_trade():
    """Add a new manual trade."""
    try:
        data = request.get_json()
        
        # Parse timestamp if provided
        timestamp = None
        if data.get('timestamp'):
            timestamp = datetime.fromisoformat(data['timestamp'])
        
        exit_timestamp = None
        if data.get('exit_timestamp'):
            exit_timestamp = datetime.fromisoformat(data['exit_timestamp'])
        
        trade = _trade_manager.add_trade(
            symbol=data['symbol'],
            side=data['side'],
            entry_price=float(data['entry_price']),
            quantity=float(data['quantity']),
            timestamp=timestamp,
            exit_price=float(data['exit_price']) if data.get('exit_price') else None,
            exit_timestamp=exit_timestamp,
            stop_loss=float(data['stop_loss']) if data.get('stop_loss') else None,
            take_profit=float(data['take_profit']) if data.get('take_profit') else None,
            notes=data.get('notes')
        )
        
        # Clear analysis cache for this symbol to force re-analysis
        keys_to_remove = [k for k in _analysis_cache.keys() if trade.symbol in k]
        for k in keys_to_remove:
            del _analysis_cache[k]
        
        return jsonify({
            'success': True,
            'data': trade.model_dump(mode='json')
        })
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 400


@app.route('/api/trades/manual/<trade_id>', methods=['PUT'])
def update_manual_trade(trade_id):
    """Update an existing manual trade."""
    try:
        data = request.get_json()
        
        exit_timestamp = None
        if data.get('exit_timestamp'):
            exit_timestamp = datetime.fromisoformat(data['exit_timestamp'])
        
        trade = _trade_manager.update_trade(
            trade_id=trade_id,
            exit_price=float(data['exit_price']) if data.get('exit_price') else None,
            exit_timestamp=exit_timestamp,
            stop_loss=float(data['stop_loss']) if data.get('stop_loss') else None,
            take_profit=float(data['take_profit']) if data.get('take_profit') else None,
            notes=data.get('notes')
        )
        
        if trade:
            # Clear cache
            keys_to_remove = [k for k in _analysis_cache.keys() if trade.symbol in k]
            for k in keys_to_remove:
                del _analysis_cache[k]
            
            return jsonify({
                'success': True,
                'data': trade.model_dump(mode='json')
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Trade {trade_id} not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/trades/manual/<trade_id>', methods=['DELETE'])
def delete_manual_trade(trade_id):
    """Delete a manual trade."""
    try:
        success = _trade_manager.delete_trade(trade_id)
        
        if success:
            # Clear all cache since we don't know the symbol
            _analysis_cache.clear()
            
            return jsonify({
                'success': True,
                'message': f'Trade {trade_id} deleted'
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Trade {trade_id} not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/trades/manual/clear', methods=['POST'])
def clear_manual_trades():
    """Clear all manual trades or trades for a specific symbol."""
    try:
        data = request.get_json() or {}
        symbol = data.get('symbol')
        
        _trade_manager.clear_trades(symbol)
        _analysis_cache.clear()
        
        return jsonify({
            'success': True,
            'message': f'Trades cleared' + (f' for {symbol}' if symbol else '')
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


if __name__ == '__main__':
    print("=" * 60)
    print("Trade Review AI - Web Dashboard")
    print("=" * 60)
    print("\nStarting server at http://localhost:5000")
    print("Press Ctrl+C to stop\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
