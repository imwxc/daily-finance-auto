"""投资信号相关数据模型"""

from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class SignalType(str, Enum):
    """信号类型"""

    NORMAL = "normal"  # 正常定投
    INCREASE = "increase"  # 加仓信号
    REDUCE = "reduce"  # 减仓信号
    SKIP = "skip"  # 跳过定投
    SELL = "sell"  # 卖出信号


class SignalStrength(int, Enum):
    """信号强度 (0-100)"""

    WEAK = 30  # 弱信号
    MEDIUM = 50  # 中等信号
    STRONG = 70  # 强信号
    VERY_STRONG = 90  # 非常强信号


class InvestSignal(BaseModel):
    """投资信号"""

    target_code: str = Field(..., description="目标代码(基金/股票)")
    target_name: str = Field(..., description="目标名称")
    signal_type: SignalType = Field(..., description="信号类型")
    strength: int = Field(..., ge=0, le=100, description="信号强度(0-100)")
    base_amount: float = Field(..., description="基础定投金额")
    suggested_amount: float = Field(..., description="建议投资金额")
    reason: str = Field(..., description="信号原因")
    indicators: dict = Field(default_factory=dict, description="相关指标")
    signal_date: date = Field(default_factory=date.today, description="信号日期")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")

    @property
    def multiplier(self) -> float:
        """投资倍数"""
        if self.base_amount == 0:
            return 0
        return round(self.suggested_amount / self.base_amount, 2)

    @property
    def emoji(self) -> str:
        """信号对应的 emoji"""
        emoji_map = {
            SignalType.NORMAL: "✅",
            SignalType.INCREASE: "📉",
            SignalType.REDUCE: "📈",
            SignalType.SKIP: "⏸️",
            SignalType.SELL: "🔴",
        }
        return emoji_map.get(self.signal_type, "❓")

    class Config:
        json_encoders = {
            date: lambda v: v.isoformat(),
            datetime: lambda v: v.isoformat(),
        }
