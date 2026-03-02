"""股票相关数据模型"""

from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class MarketType(str, Enum):
    """市场类型"""

    SH = "sh"  # 上海
    SZ = "sz"  # 深圳
    BJ = "bj"  # 北京


class Stock(BaseModel):
    """股票基础信息"""

    code: str = Field(..., description="股票代码，如 600519")
    name: str = Field(..., description="股票名称")
    full_code: str = Field(..., description="完整代码，如 600519.SH")
    market: MarketType = Field(..., description="市场类型")
    industry: Optional[str] = Field(None, description="所属行业")
    list_date: Optional[date] = Field(None, description="上市日期")
    total_shares: Optional[float] = Field(None, description="总股本(万股)")
    float_shares: Optional[float] = Field(None, description="流通股本(万股)")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")


class StockDaily(BaseModel):
    """股票日线数据"""

    stock_code: str = Field(..., description="股票代码")
    trade_date: date = Field(..., description="交易日期")
    open: float = Field(..., description="开盘价")
    high: float = Field(..., description="最高价")
    low: float = Field(..., description="最低价")
    close: float = Field(..., description="收盘价")
    pre_close: Optional[float] = Field(None, description="昨收价")
    change: Optional[float] = Field(None, description="涨跌额")
    pct_change: Optional[float] = Field(None, description="涨跌幅(%)")
    volume: Optional[float] = Field(None, description="成交量(手)")
    amount: Optional[float] = Field(None, description="成交额(千元)")
    turnover_rate: Optional[float] = Field(None, description="换手率(%)")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")

    class Config:
        json_encoders = {
            date: lambda v: v.isoformat(),
            datetime: lambda v: v.isoformat(),
        }


class StockWatchItem(BaseModel):
    """股票监控项"""

    code: str = Field(..., description="股票代码")
    name: str = Field(..., description="股票名称")
    shares: float = Field(default=0, description="持仓股数")
    cost_price: Optional[float] = Field(None, description="成本价")
    enabled: bool = Field(default=True, description="是否启用")
    notes: Optional[str] = Field(None, description="备注")
