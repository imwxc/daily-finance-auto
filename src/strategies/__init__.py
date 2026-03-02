"""策略模块"""

from .base import BaseStrategy, StrategyResult
from .ma_deviation import MADeviationStrategy

__all__ = [
    "BaseStrategy",
    "StrategyResult",
    "MADeviationStrategy",
]
