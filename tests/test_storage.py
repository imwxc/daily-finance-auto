"""测试存储层"""

import pytest
from datetime import date

from src.storage import Database, FundRepository, StockRepository
from src.models import Fund, FundNav, Stock, StockDaily


@pytest.fixture
async def db(tmp_path):
    """创建测试数据库"""
    db_path = str(tmp_path / "test.db")
    database = Database(db_path)
    await database.connect()
    await database.init_tables()
    yield database
    await database.close()


@pytest.mark.asyncio
async def test_fund_crud(db):
    """测试基金 CRUD 操作"""
    repo = FundRepository(db)

    # Create
    fund = Fund(code="000001", name="测试基金", full_code="000001.OF")
    await repo.save_fund(fund)

    # Read
    saved = await repo.get_fund("000001")
    assert saved is not None
    assert saved.name == "测试基金"

    # List
    funds = await repo.list_funds()
    assert len(funds) == 1


@pytest.mark.asyncio
async def test_fund_nav_batch(db):
    """测试批量保存净值"""
    repo = FundRepository(db)

    # 先保存基金
    fund = Fund(code="000001", name="测试基金", full_code="000001.OF")
    await repo.save_fund(fund)

    # 批量保存净值
    navs = [
        FundNav(
            fund_code="000001",
            nav_date=date(2026, 2, 28) - __import__('datetime').timedelta(days=i),
            unit_nav=1.0 + i * 0.01,
        )
        for i in range(30)
    ]
    count = await repo.save_fund_navs(navs)
    assert count == 30

    # 读取最新净值
    latest = await repo.get_latest_nav("000001")
    assert latest is not None
    assert latest.unit_nav == 1.29  # 最后一个


@pytest.mark.asyncio
async def test_stock_crud(db):
    """测试股票 CRUD 操作"""
    from src.models.stock import MarketType

    repo = StockRepository(db)

    # Create
    stock = Stock(
        code="600519",
        name="贵州茅台",
        full_code="600519.SH",
        market=MarketType.SH,
    )
    await repo.save_stock(stock)

    # Read
    saved = await repo.get_stock("600519")
    assert saved is not None
    assert saved.name == "贵州茅台"
