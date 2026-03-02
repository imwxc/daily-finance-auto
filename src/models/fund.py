"""基金相关数据模型"""

from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class FundType(str, Enum):
    """基金类型"""

    STOCK = "stock"  # 股票型
    BOND = "bond"  # 债券型
    MIXED = "mixed"  # 混合型
    INDEX = "index"  # 指数型
    MONEY = "money"  # 货币型
    QDII = "qdii"  # QDII
    ETF = "etf"  # ETF
    LOF = "lof"  # LOF
    OTHER = "other"  # 其他


class Fund(BaseModel):
    """基金基础信息"""

    code: str = Field(..., description="基金代码，如 000001")
    name: str = Field(..., description="基金名称")
    full_code: str = Field(..., description="完整代码，如 000001.OF")
    fund_type: FundType = Field(default=FundType.OTHER, description="基金类型")
    manager: Optional[str] = Field(None, description="基金经理")
    company: Optional[str] = Field(None, description="基金公司")
    establish_date: Optional[date] = Field(None, description="成立日期")
    benchmark: Optional[str] = Field(None, description="业绩比较基准")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")


class FundNav(BaseModel):
    """基金净值数据"""

    fund_code: str = Field(..., description="基金代码")
    nav_date: date = Field(..., description="净值日期")
    unit_nav: float = Field(..., description="单位净值")
    acc_nav: Optional[float] = Field(None, description="累计净值")
    daily_growth: Optional[float] = Field(None, description="日增长率(%)")
    purchase_status: Optional[str] = Field(None, description="申购状态")
    redeem_status: Optional[str] = Field(None, description="赎回状态")
    dividend: Optional[float] = Field(None, description="分红")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")

    class Config:
        # 允许 nav_date 作为主键的一部分
        json_encoders = {
            date: lambda v: v.isoformat(),
            datetime: lambda v: v.isoformat(),
        }


class FundWatchItem(BaseModel):
    """基金监控项"""

    code: str = Field(..., description="基金代码")
    name: str = Field(..., description="基金名称")
    amount: float = Field(default=1000, description="定投金额(元)")
    enabled: bool = Field(default=True, description="是否启用")
    strategy: str = Field(default="ma_deviation", description="定投策略")
    notes: Optional[str] = Field(None, description="备注")
