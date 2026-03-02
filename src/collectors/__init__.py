"""数据采集模块"""

from .base import BaseCollector, CollectorResult
from .akshare_collector import AKShareFundCollector
from .tushare_collector import TushareStockCollector

__all__ = [
    "BaseCollector",
    "CollectorResult",
    "AKShareFundCollector",
    "TushareStockCollector",
]
