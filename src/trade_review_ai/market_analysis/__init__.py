"""Market analysis module for deriving market context."""

from datetime import datetime
from typing import List, Tuple
import numpy as np

from ..models import OHLCV, MarketContext


class MarketAnalyzer:
    """
    Analyzes market data to derive context such as trend, structure, and volatility.
    
    Uses deterministic technical analysis methods to ensure consistent, 
    reproducible results.
    """
    
    @staticmethod
    def calculate_trend(ohlcv_data: List[OHLCV]) -> Tuple[str, float]:
        """
        Calculate trend direction and strength using linear regression.
        
        Args:
            ohlcv_data: List of OHLCV candlestick data
            
        Returns:
            Tuple of (trend_direction, trend_strength)
            - trend_direction: "bullish", "bearish", or "neutral"
            - trend_strength: 0.0 to 1.0
        """
        if len(ohlcv_data) < 2:
            return "neutral", 0.0
        
        closes = np.array([candle.close for candle in ohlcv_data])
        x = np.arange(len(closes))
        
        # Linear regression
        slope, _ = np.polyfit(x, closes, 1)
        
        # Calculate R-squared for strength
        y_pred = slope * x + np.mean(closes)
        ss_res = np.sum((closes - y_pred) ** 2)
        ss_tot = np.sum((closes - np.mean(closes)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        
        # Normalize slope relative to price
        avg_price = np.mean(closes)
        normalized_slope = slope / avg_price if avg_price > 0 else 0
        
        # Determine trend direction
        threshold = 0.001  # 0.1% per period
        if normalized_slope > threshold:
            trend = "bullish"
        elif normalized_slope < -threshold:
            trend = "bearish"
        else:
            trend = "neutral"
        
        # Trend strength is R-squared
        strength = max(0.0, min(1.0, r_squared))
        
        return trend, strength
    
    @staticmethod
    def calculate_volatility(ohlcv_data: List[OHLCV]) -> float:
        """
        Calculate Average True Range (ATR) as volatility measure.
        
        Args:
            ohlcv_data: List of OHLCV candlestick data
            
        Returns:
            ATR value (average volatility)
        """
        if len(ohlcv_data) < 2:
            return 0.0
        
        true_ranges = []
        for i in range(1, len(ohlcv_data)):
            high = ohlcv_data[i].high
            low = ohlcv_data[i].low
            prev_close = ohlcv_data[i - 1].close
            
            tr = max(
                high - low,
                abs(high - prev_close),
                abs(low - prev_close)
            )
            true_ranges.append(tr)
        
        return np.mean(true_ranges) if true_ranges else 0.0
    
    @staticmethod
    def find_support_resistance(
        ohlcv_data: List[OHLCV],
        num_levels: int = 3
    ) -> Tuple[List[float], List[float]]:
        """
        Identify key support and resistance levels using swing highs/lows.
        
        Args:
            ohlcv_data: List of OHLCV candlestick data
            num_levels: Number of levels to identify
            
        Returns:
            Tuple of (support_levels, resistance_levels)
        """
        if len(ohlcv_data) < 3:
            return [], []
        
        # Find swing lows (support) and swing highs (resistance)
        swing_lows = []
        swing_highs = []
        
        for i in range(1, len(ohlcv_data) - 1):
            # Swing low: lower than neighbors
            if (ohlcv_data[i].low < ohlcv_data[i - 1].low and
                ohlcv_data[i].low < ohlcv_data[i + 1].low):
                swing_lows.append(ohlcv_data[i].low)
            
            # Swing high: higher than neighbors
            if (ohlcv_data[i].high > ohlcv_data[i - 1].high and
                ohlcv_data[i].high > ohlcv_data[i + 1].high):
                swing_highs.append(ohlcv_data[i].high)
        
        # Cluster similar levels and take top N
        support_levels = MarketAnalyzer._cluster_levels(swing_lows, num_levels)
        resistance_levels = MarketAnalyzer._cluster_levels(swing_highs, num_levels)
        
        return support_levels, resistance_levels
    
    @staticmethod
    def _cluster_levels(levels: List[float], num_clusters: int) -> List[float]:
        """
        Cluster price levels that are close together.
        
        Args:
            levels: List of price levels
            num_clusters: Number of clusters to return
            
        Returns:
            List of clustered price levels
        """
        if not levels:
            return []
        
        levels = sorted(levels)
        
        if len(levels) <= num_clusters:
            return levels
        
        # Simple clustering: group levels within 1% of each other
        clusters = []
        current_cluster = [levels[0]]
        
        for level in levels[1:]:
            if abs(level - current_cluster[-1]) / current_cluster[-1] < 0.01:
                current_cluster.append(level)
            else:
                clusters.append(np.mean(current_cluster))
                current_cluster = [level]
        
        if current_cluster:
            clusters.append(np.mean(current_cluster))
        
        # Return top N most significant levels (most touches)
        return sorted(clusters)[:num_clusters]
    
    @staticmethod
    def analyze_market_context(
        symbol: str,
        ohlcv_data: List[OHLCV],
        start_date: datetime,
        end_date: datetime
    ) -> MarketContext:
        """
        Perform comprehensive market analysis.
        
        Args:
            symbol: Trading symbol
            ohlcv_data: List of OHLCV candlestick data
            start_date: Analysis start date
            end_date: Analysis end date
            
        Returns:
            MarketContext object with analysis results
        """
        trend, trend_strength = MarketAnalyzer.calculate_trend(ohlcv_data)
        volatility = MarketAnalyzer.calculate_volatility(ohlcv_data)
        support_levels, resistance_levels = MarketAnalyzer.find_support_resistance(ohlcv_data)
        
        volumes = [candle.volume for candle in ohlcv_data]
        average_volume = np.mean(volumes) if volumes else 0.0
        
        return MarketContext(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            trend=trend,
            trend_strength=trend_strength,
            volatility=volatility,
            support_levels=support_levels,
            resistance_levels=resistance_levels,
            average_volume=average_volume
        )
