"""测试策略模块"""

import pytest
from datetime import date

from src.models import FundNav
from src.strategies import MADeviationStrategy


@pytest.fixture
def sample_navs():
    """创建测试用净值数据"""
    navs = []
    base_nav = 1.0
    for i in range(60):
        # 创建一个上涨趋势
        nav_value = base_nav + i * 0.01 + (i % 5 - 2) * 0.005
        navs.append(FundNav(
            fund_code="000001",
            nav_date=date(2026, 1, 1) + __import__('datetime').timedelta(days=i),
            unit_nav=round(nav_value, 4),
        ))
    return list(reversed(navs))  # 最新的在前


@pytest.mark.asyncio
async def test_ma_deviation_strategy(sample_navs):
    """测试均线偏离策略"""
    strategy = MADeviationStrategy(ma_period=20)
    result = await strategy.analyze(sample_navs, base_amount=1000)

    assert result.signal is not None
    assert result.signal.base_amount == 1000
    assert result.signal.strength >= 0
    assert result.signal.strength <= 100
    assert "ma" in result.indicators


@pytest.mark.asyncio
async def test_strategy_with_insufficient_data():
    """测试数据不足的情况"""
    navs = [
        FundNav(
            fund_code="000001",
            nav_date=date(2026, 2, 28),
            unit_nav=1.0,
        )
        for _ in range(10)
    ]

    strategy = MADeviationStrategy(ma_period=60)
    result = await strategy.analyze(navs, base_amount=1000)

    # 数据不足时应该返回正常信号
    assert result.signal.signal_type.value == "normal"
