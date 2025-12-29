"""AI integration module for generating pedagogical commentary."""

from typing import List
from openai import OpenAI

from ..models import Trade, MarketContext, TradeEvaluation
from ..config import Config


class AICommentaryGenerator:
    """
    Generates structured, pedagogical commentary using OpenAI API.
    
    Focuses on educational insights rather than speculative predictions.
    """
    
    def __init__(self, config: Config):
        """
        Initialize the AI commentary generator.
        
        Args:
            config: Application configuration
        """
        self.config = config
        self.client = OpenAI(api_key=config.openai_api_key)
    
    def _build_prompt(
        self,
        market_context: MarketContext,
        trades: List[Trade],
        evaluations: List[TradeEvaluation],
        performance_metrics: dict
    ) -> str:
        """
        Build the prompt for AI commentary generation.
        
        Args:
            market_context: Market context analysis
            trades: List of trades
            evaluations: List of trade evaluations
            performance_metrics: Overall performance metrics
            
        Returns:
            Formatted prompt string
        """
        # Format market context
        context_str = f"""
Market Context ({market_context.symbol}):
- Period: {market_context.start_date.date()} to {market_context.end_date.date()}
- Trend: {market_context.trend} (strength: {market_context.trend_strength:.2f})
- Volatility (ATR): {market_context.volatility:.4f}
- Support Levels: {', '.join([f'{level:.2f}' for level in market_context.support_levels])}
- Resistance Levels: {', '.join([f'{level:.2f}' for level in market_context.resistance_levels])}
- Average Volume: {market_context.average_volume:.0f}
"""
        
        # Format trades and evaluations
        trades_str = "\nTrades Analysis:\n"
        for trade, evaluation in zip(trades, evaluations):
            status = "closed" if trade.exit_price else "open"
            pnl_str = f"P&L: ${trade.pnl:.2f}" if trade.pnl is not None else "P&L: N/A"
            
            # Build exit info
            if trade.exit_price:
                exit_str = f"- Exit: ${trade.exit_price:.2f} at {trade.exit_timestamp.strftime('%Y-%m-%d %H:%M')}"
            else:
                exit_str = "- Exit: Still open"
            
            # Build stop loss and take profit strings
            sl_str = f"${trade.stop_loss:.2f}" if trade.stop_loss else "None"
            tp_str = f"${trade.take_profit:.2f}" if trade.take_profit else "None"
            rr_str = f"{evaluation.risk_reward_ratio:.2f}" if evaluation.risk_reward_ratio else "N/A"
            
            trades_str += f"""
Trade {trade.trade_id} ({status}):
- Side: {trade.side.upper()}
- Entry: ${trade.entry_price:.2f} at {trade.timestamp.strftime('%Y-%m-%d %H:%M')}
{exit_str}
- {pnl_str}
- Stop Loss: {sl_str}
- Take Profit: {tp_str}
- Entry Quality: {evaluation.entry_quality}
- Exit Quality: {evaluation.exit_quality if evaluation.exit_quality else "N/A (open)"}
- Aligned with Trend: {evaluation.aligned_with_trend}
- Execution Discipline: {evaluation.execution_discipline}
- Risk/Reward: {rr_str}
- Key Observations: {'; '.join(evaluation.key_observations)}
"""
        
        # Format performance metrics
        metrics_str = f"""
Overall Performance:
- Total Trades: {performance_metrics['total_trades']}
- Winning Trades: {performance_metrics['winning_trades']}
- Losing Trades: {performance_metrics['losing_trades']}
- Win Rate: {performance_metrics['win_rate']:.1f}%
- Total P&L: ${performance_metrics['total_pnl']:.2f}
- Average P&L per Trade: ${performance_metrics['avg_pnl']:.2f}
- Trades with Trend: {performance_metrics['trades_with_trend']}
- Trades against Trend: {performance_metrics['trades_against_trend']}
"""
        
        # Build full prompt
        prompt = f"""You are an experienced trading educator reviewing a trader's performance. Analyze the following trading data and provide educational, pedagogical commentary focused on learning and improvement.

{context_str}
{trades_str}
{metrics_str}

Please provide a structured review that includes:

1. **Market Context Summary**: Brief overview of the market conditions during this period.

2. **Execution Analysis**: Evaluate the trader's execution quality, including:
   - Entry timing and quality
   - Exit discipline
   - Risk management practices
   - Alignment with market trend

3. **Key Strengths**: Identify what the trader did well (be specific with examples).

4. **Areas for Improvement**: Highlight specific areas where the trader can improve (be constructive and specific).

5. **Learning Points**: Provide 2-3 actionable learning points or principles the trader should focus on.

Keep the commentary:
- Educational and constructive (not speculative about future moves)
- Specific and evidence-based (reference actual trades)
- Focused on process and discipline (not just results)
- Encouraging but honest about areas needing improvement

Limit your response to approximately 500 words."""

        return prompt
    
    def generate_commentary(
        self,
        market_context: MarketContext,
        trades: List[Trade],
        evaluations: List[TradeEvaluation],
        performance_metrics: dict
    ) -> str:
        """
        Generate AI-powered pedagogical commentary.
        
        Args:
            market_context: Market context analysis
            trades: List of trades
            evaluations: List of trade evaluations
            performance_metrics: Overall performance metrics
            
        Returns:
            AI-generated commentary string
        """
        prompt = self._build_prompt(market_context, trades, evaluations, performance_metrics)
        
        try:
            response = self.client.chat.completions.create(
                model=self.config.openai_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an experienced trading educator focused on helping traders learn and improve through objective analysis of their trading performance."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,  # Lower temperature for more consistent, factual responses
                max_tokens=1000
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            return f"Error generating AI commentary: {str(e)}"
