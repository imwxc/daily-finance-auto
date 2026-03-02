"""测试采集器模块"""

import pytest

from src.models import Fund, FundNav, Stock, StockDaily


def test_fund_model():
    """测试基金模型"""
    fund = Fund(
        code="000001",
        name="华夏成长",
        full_code="000001.OF",
    )
    assert fund.code == "000001"
    assert fund.name == "华夏成长"


def test_fund_nav_model():
    """测试基金净值模型"""
    from datetime import date

    nav = FundNav(
        fund_code="000001",
        nav_date=date(2026, 2, 28),
        unit_nav=1.2345,
        daily_growth=1.5,
    )
    assert nav.fund_code == "000001"
    assert nav.unit_nav == 1.2345
    assert nav.daily_growth == 1.5


def test_stock_model():
    """测试股票模型"""
    from src.models.stock import MarketType

    stock = Stock(
        code="600519",
        name="贵州茅台",
        full_code="600519.SH",
        market=MarketType.SH,
    )
    assert stock.code == "600519"
    assert stock.market == MarketType.SH


def test_signal_model():
    """测试信号模型"""
    from src.models.signal import InvestSignal, SignalType

    signal = InvestSignal(
        target_code="000001",
        target_name="测试基金",
        signal_type=SignalType.INCREASE,
        strength=80,
        base_amount=1000,
        suggested_amount=2000,
        reason="均线偏离-15%",
    )
    assert signal.signal_type == SignalType.INCREASE
    assert signal.multiplier == 2.0
    assert signal.emoji == "📉"


@pytest.mark.asyncio
async def test_database_init(tmp_path):
    """测试数据库初始化"""
    from src.storage import Database

    db_path = str(tmp_path / "test.db")
    db = Database(db_path)
    await db.connect()
    await db.init_tables()
    await db.close()

    import os
    assert os.path.exists(db_path)


@pytest.mark.asyncio
async def test_fund_repository(tmp_path):
    """测试基金仓库"""
    from datetime import date
    from src.storage import Database, FundRepository

    db_path = str(tmp_path / "test.db")
    db = Database(db_path)
    await db.connect()
    await db.init_tables()

    repo = FundRepository(db)

    # 保存基金
    fund = Fund(code="000001", name="测试基金", full_code="000001.OF")
    await repo.save_fund(fund)

    # 保存净值
    nav = FundNav(
        fund_code="000001",
        nav_date=date(2026, 2, 28),
        unit_nav=1.2345,
    )
    count = await repo.save_fund_navs([nav])
    assert count == 1

    # 读取净值
    latest = await repo.get_latest_nav("000001")
    assert latest is not None
    assert latest.unit_nav == 1.2345

    await db.close()
