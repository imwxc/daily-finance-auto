"""均线偏离策略"""

import logging
from datetime import date

import numpy as np

from ..models.fund import FundNav
from ..models.signal import InvestSignal, SignalType
from .base import BaseStrategy, StrategyResult

logger = logging.getLogger(__name__)


class MADeviationStrategy(BaseStrategy[FundNav]):
    """
    均线偏离策略

    根据当前净值相对于均线的偏离程度调整定投金额：
    - 净值 < 均线 20%: 加倍定投 (强买入信号)
    - 净值 < 均线 10%: 增加 50% 定投
    - 净值在均线附近: 正常定投
    - 净值 > 均线 10%: 减少 50% 定投
    - 净值 > 均线 20%: 跳过定投
    """

    name = "ma_deviation"
    description = "均线偏离策略"

    def __init__(self, ma_period: int = 60):
        """
        Args:
            ma_period: 均线周期（默认 60 日）
        """
        self.ma_period = ma_period

    async def analyze(self, data: list[FundNav], base_amount: float) -> StrategyResult:
        if len(data) < self.ma_period:
            logger.warning(f"数据不足，需要至少 {self.ma_period} 条数据")
            return self._create_signal(
                data[0] if data else None,
                base_amount,
                SignalType.NORMAL,
                50,
                f"数据不足，使用正常定投",
                {},
            )

        # 计算均线
        nav_values = np.array([nav.unit_nav for nav in data[: self.ma_period]])
        ma = np.mean(nav_values)

        # 当前净值
        current_nav = data[0].unit_nav
        current_date = data[0].nav_date

        # 计算偏离度
        deviation = (current_nav - ma) / ma * 100

        # 根据偏离度确定信号
        signal_type, strength, reason = self._determine_signal(deviation)

        indicators = {
            "current_nav": round(current_nav, 4),
            "ma": round(ma, 4),
            "deviation": round(deviation, 2),
            "ma_period": self.ma_period,
        }

        return self._create_signal(
            data[0],
            base_amount,
            signal_type,
            strength,
            reason,
            indicators,
        )

    def _determine_signal(
        self, deviation: float
    ) -> tuple[SignalType, int, str]:
        """根据偏离度确定信号类型和强度"""
        if deviation <= -20:
            return SignalType.INCREASE, 90, f"大幅低于均线 {abs(deviation):.1f}%，强烈买入信号"
        elif deviation <= -10:
            return SignalType.INCREASE, 70, f"低于均线 {abs(deviation):.1f}%，买入信号"
        elif deviation <= 10:
            return SignalType.NORMAL, 50, f"接近均线，正常定投"
        elif deviation <= 20:
            return SignalType.REDUCE, 30, f"高于均线 {deviation:.1f}%，减少定投"
        else:
            return SignalType.SKIP, 10, f"大幅高于均线 {deviation:.1f}%，建议跳过"

    def _create_signal(
        self,
        latest_nav: FundNav | None,
        base_amount: float,
        signal_type: SignalType,
        strength: int,
        reason: str,
        indicators: dict,
    ) -> StrategyResult:
        multiplier = self.calculate_multiplier(strength)
        suggested_amount = base_amount * multiplier

        signal = InvestSignal(
            target_code=latest_nav.fund_code if latest_nav else "UNKNOWN",
            target_name="",
            signal_type=signal_type,
            strength=strength,
            base_amount=base_amount,
            suggested_amount=suggested_amount,
            reason=reason,
            indicators=indicators,
            signal_date=latest_nav.nav_date if latest_nav else date.today(),
        )

        return StrategyResult(
            signal=signal,
            indicators=indicators,
        )
