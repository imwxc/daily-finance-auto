"""技术指标分析"""

import logging
from typing import Optional

import numpy as np

from ..models.stock import StockDaily

logger = logging.getLogger(__name__)


class TechnicalIndicators:
    """技术指标计算器"""

    @staticmethod
    def ma(prices: list[float], period: int) -> list[Optional[float]]:
        """简单移动平均线"""
        result = []
        for i in range(len(prices)):
            if i < period - 1:
                result.append(None)
            else:
                avg = sum(prices[i - period + 1 : i + 1]) / period
                result.append(round(avg, 2))
        return result

    @staticmethod
    def ema(prices: list[float], period: int) -> list[Optional[float]]:
        """指数移动平均线"""
        result = []
        multiplier = 2 / (period + 1)

        for i in range(len(prices)):
            if i < period - 1:
                result.append(None)
            elif i == period - 1:
                # 第一个 EMA = SMA
                result.append(round(sum(prices[:period]) / period, 2))
            else:
                ema = (prices[i] * multiplier) + (result[-1] * (1 - multiplier))
                result.append(round(ema, 2))
        return result

    @staticmethod
    def macd(
        prices: list[float], fast: int = 12, slow: int = 26, signal: int = 9
    ) -> dict:
        """MACD 指标"""
        ema_fast = TechnicalIndicators.ema(prices, fast)
        ema_slow = TechnicalIndicators.ema(prices, slow)

        # DIF = EMA(12) - EMA(26)
        dif = [
            round(f - s, 4) if f and s else None
            for f, s in zip(ema_fast, ema_slow)
        ]

        # DEA = EMA(DIF, 9)
        dif_values = [d for d in dif if d is not None]
        dea_values = TechnicalIndicators.ema(dif_values, signal)

        # MACD = (DIF - DEA) * 2
        macd_values = []
        dea_idx = 0
        for d in dif:
            if d is None or dea_idx >= len(dea_values) or dea_values[dea_idx] is None:
                macd_values.append(None)
            else:
                macd_values.append(round((d - dea_values[dea_idx]) * 2, 4))
                dea_idx += 1

        return {
            "dif": dif,
            "dea": dea_values,
            "macd": macd_values,
        }

    @staticmethod
    def rsi(prices: list[float], period: int = 14) -> list[Optional[float]]:
        """相对强弱指数 RSI"""
        result = []

        for i in range(len(prices)):
            if i < period:
                result.append(None)
                continue

            # 计算涨跌幅
            gains = []
            losses = []
            for j in range(i - period + 1, i + 1):
                change = prices[j] - prices[j - 1]
                if change > 0:
                    gains.append(change)
                    losses.append(0)
                else:
                    gains.append(0)
                    losses.append(abs(change))

            avg_gain = sum(gains) / period
            avg_loss = sum(losses) / period

            if avg_loss == 0:
                rsi = 100
            else:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))

            result.append(round(rsi, 2))

        return result

    @staticmethod
    def bollinger_bands(
        prices: list[float], period: int = 20, std_dev: float = 2
    ) -> dict:
        """布林带"""
        middle = TechnicalIndicators.ma(prices, period)
        upper = []
        lower = []

        for i in range(len(prices)):
            if middle[i] is None:
                upper.append(None)
                lower.append(None)
                continue

            window = prices[i - period + 1 : i + 1]
            std = np.std(window)
            upper.append(round(middle[i] + std_dev * std, 2))
            lower.append(round(middle[i] - std_dev * std, 2))

        return {
            "upper": upper,
            "middle": middle,
            "lower": lower,
        }

    @staticmethod
    def kdj(
        highs: list[float],
        lows: list[float],
        closes: list[float],
        n: int = 9,
        m1: int = 3,
        m2: int = 3,
    ) -> dict:
        """KDJ 指标"""
        k_values = []
        d_values = []
        j_values = []

        prev_k = 50
        prev_d = 50

        for i in range(len(closes)):
            if i < n - 1:
                k_values.append(None)
                d_values.append(None)
                j_values.append(None)
                continue

            # 计算 RSV
            high_n = max(highs[i - n + 1 : i + 1])
            low_n = min(lows[i - n + 1 : i + 1])

            if high_n == low_n:
                rsv = 50
            else:
                rsv = (closes[i] - low_n) / (high_n - low_n) * 100

            # K = SMA(RSV, M1)
            k = (2 / 3) * prev_k + (1 / 3) * rsv
            # D = SMA(K, M2)
            d = (2 / 3) * prev_d + (1 / 3) * k
            # J = 3K - 2D
            j = 3 * k - 2 * d

            k_values.append(round(k, 2))
            d_values.append(round(d, 2))
            j_values.append(round(j, 2))

            prev_k = k
            prev_d = d

        return {
            "k": k_values,
            "d": d_values,
            "j": j_values,
        }


class StockAnalyzer:
    """股票分析器"""

    def __init__(self, dailys: list[StockDaily]):
        self.dailys = sorted(dailys, key=lambda x: x.trade_date, reverse=True)
        self.closes = [d.close for d in reversed(self.dailys)]
        self.highs = [d.high for d in reversed(self.dailys)]
        self.lows = [d.low for d in reversed(self.dailys)]

    def analyze(self) -> dict:
        """综合分析"""
        return {
            "ma": self._analyze_ma(),
            "macd": self._analyze_macd(),
            "rsi": self._analyze_rsi(),
            "bollinger": self._analyze_bollinger(),
            "trend": self._analyze_trend(),
        }

    def _analyze_ma(self) -> dict:
        """均线分析"""
        ma5 = TechnicalIndicators.ma(self.closes, 5)
        ma20 = TechnicalIndicators.ma(self.closes, 20)
        ma60 = TechnicalIndicators.ma(self.closes, 60)

        current_price = self.closes[-1]
        ma5_val = ma5[-1]
        ma20_val = ma20[-1]
        ma60_val = ma60[-1]

        # 判断趋势
        trend = "unknown"
        if ma5_val and ma20_val:
            if ma5_val > ma20_val:
                trend = "up"
            else:
                trend = "down"

        return {
            "ma5": ma5_val,
            "ma20": ma20_val,
            "ma60": ma60_val,
            "current": current_price,
            "trend": trend,
            "signal": self._ma_signal(current_price, ma5_val, ma20_val, ma60_val),
        }

    def _ma_signal(self, price, ma5, ma20, ma60) -> str:
        """均线信号"""
        if not all([ma5, ma20, ma60]):
            return "数据不足"

        if price > ma5 > ma20 > ma60:
            return "多头排列 📈"
        elif price < ma5 < ma20 < ma60:
            return "空头排列 📉"
        elif ma5 > ma20:
            return "短期上涨趋势"
        else:
            return "短期下跌趋势"

    def _analyze_macd(self) -> dict:
        """MACD 分析"""
        macd_data = TechnicalIndicators.macd(self.closes)

        dif = macd_data["dif"][-1] if macd_data["dif"] else None
        dea = macd_data["dea"][-1] if macd_data["dea"] else None
        macd = macd_data["macd"][-1] if macd_data["macd"] else None

        signal = "unknown"
        if dif and dea:
            if dif > dea and dif > 0:
                signal = "多头"
            elif dif < dea and dif < 0:
                signal = "空头"
            elif dif > dea:
                signal = "金叉"
            else:
                signal = "死叉"

        return {
            "dif": dif,
            "dea": dea,
            "macd": macd,
            "signal": signal,
        }

    def _analyze_rsi(self) -> dict:
        """RSI 分析"""
        rsi_values = TechnicalIndicators.rsi(self.closes)
        current_rsi = rsi_values[-1]

        signal = "中性"
        if current_rsi:
            if current_rsi > 80:
                signal = "超买"
            elif current_rsi > 70:
                signal = "偏强"
            elif current_rsi < 20:
                signal = "超卖"
            elif current_rsi < 30:
                signal = "偏弱"

        return {
            "rsi": current_rsi,
            "signal": signal,
        }

    def _analyze_bollinger(self) -> dict:
        """布林带分析"""
        bb = TechnicalIndicators.bollinger_bands(self.closes)
        current_price = self.closes[-1]
        upper = bb["upper"][-1]
        middle = bb["middle"][-1]
        lower = bb["lower"][-1]

        signal = "unknown"
        if upper and lower:
            if current_price > upper:
                signal = "突破上轨"
            elif current_price < lower:
                signal = "跌破下轨"
            elif current_price > middle:
                signal = "上轨区间"
            else:
                signal = "下轨区间"

        return {
            "upper": upper,
            "middle": middle,
            "lower": lower,
            "current": current_price,
            "signal": signal,
        }

    def _analyze_trend(self) -> dict:
        """趋势分析"""
        if len(self.closes) < 20:
            return {"trend": "数据不足"}

        # 计算 5 日和 20 日涨跌幅
        change_5d = (self.closes[-1] - self.closes[-5]) / self.closes[-5] * 100
        change_20d = (self.closes[-1] - self.closes[-20]) / self.closes[-20] * 100

        # 计算波动率 (20日标准差)
        volatility = np.std(self.closes[-20:]) / np.mean(self.closes[-20:]) * 100

        return {
            "change_5d": round(change_5d, 2),
            "change_20d": round(change_20d, 2),
            "volatility": round(volatility, 2),
            "trend": "上涨" if change_20d > 0 else "下跌",
        }
