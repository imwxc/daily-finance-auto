"""策略基类"""

from abc import ABC, abstractmethod
from datetime import date
from typing import Generic, TypeVar

from pydantic import BaseModel

from ..models.signal import InvestSignal, SignalType

T = TypeVar("T")


class StrategyResult(BaseModel):
    """策略计算结果"""

    signal: InvestSignal
    indicators: dict = {}
    debug_info: dict = {}


class BaseStrategy(ABC, Generic[T]):
    """策略基类"""

    name: str = "base"
    description: str = "基础策略"

    @abstractmethod
    async def analyze(self, data: list[T], base_amount: float) -> StrategyResult:
        """
        分析数据并生成信号

        Args:
            data: 输入数据（如基金净值列表）
            base_amount: 基础定投金额

        Returns:
            StrategyResult: 策略结果
        """
        pass

    def calculate_multiplier(self, strength: int) -> float:
        """根据信号强度计算投资倍数"""
        if strength >= 80:
            return 2.0  # 非常强信号，加倍
        elif strength >= 60:
            return 1.5  # 强信号，增加 50%
        elif strength >= 40:
            return 1.0  # 中等信号，正常
        elif strength >= 20:
            return 0.5  # 弱信号，减半
        else:
            return 0.0  # 跳过
