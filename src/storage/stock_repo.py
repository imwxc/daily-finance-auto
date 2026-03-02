"""股票数据仓库"""

import logging
from datetime import date
from typing import Optional

from ..models.stock import Stock, StockDaily
from .database import Database, get_database

logger = logging.getLogger(__name__)


class StockRepository:
    """股票数据仓库"""

    def __init__(self, db: Optional[Database] = None):
        self._db = db

    async def _get_db(self) -> Database:
        if self._db is None:
            self._db = await get_database()
        return self._db

    async def save_stock(self, stock: Stock) -> None:
        """保存股票基础信息"""
        db = await self._get_db()
        await db.execute(
            """
            INSERT INTO stocks (code, name, full_code, market, industry, 
                                list_date, total_shares, float_shares, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(code) DO UPDATE SET
                name = excluded.name,
                industry = excluded.industry,
                total_shares = excluded.total_shares,
                float_shares = excluded.float_shares,
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                stock.code,
                stock.name,
                stock.full_code,
                stock.market.value,
                stock.industry,
                stock.list_date.isoformat() if stock.list_date else None,
                stock.total_shares,
                stock.float_shares,
            ),
        )
        logger.debug(f"保存股票信息: {stock.code} - {stock.name}")

    async def save_stock_dailys(self, dailys: list[StockDaily]) -> int:
        """批量保存股票日线数据"""
        if not dailys:
            return 0

        db = await self._get_db()
        params_list = [
            (
                daily.stock_code,
                daily.trade_date.isoformat(),
                daily.open,
                daily.high,
                daily.low,
                daily.close,
                daily.pre_close,
                daily.change,
                daily.pct_change,
                daily.volume,
                daily.amount,
                daily.turnover_rate,
            )
            for daily in dailys
        ]

        await db.executemany(
            """
            INSERT INTO stock_dailys (stock_code, trade_date, open, high, low, close,
                                      pre_close, change, pct_change, volume, amount, 
                                      turnover_rate, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(stock_code, trade_date) DO UPDATE SET
                open = excluded.open,
                high = excluded.high,
                low = excluded.low,
                close = excluded.close,
                pre_close = excluded.pre_close,
                change = excluded.change,
                pct_change = excluded.pct_change,
                volume = excluded.volume,
                amount = excluded.amount,
                turnover_rate = excluded.turnover_rate,
                updated_at = CURRENT_TIMESTAMP
            """,
            params_list,
        )
        logger.info(f"保存 {len(dailys)} 条股票日线数据")
        return len(dailys)

    async def get_stock(self, code: str) -> Optional[Stock]:
        """获取股票基础信息"""
        db = await self._get_db()
        rows = await db.execute(
            "SELECT * FROM stocks WHERE code = ?", (code,), fetch=True
        )
        if rows:
            row = rows[0]
            from ..models.stock import MarketType
            return Stock(
                code=row["code"],
                name=row["name"],
                full_code=row["full_code"],
                market=MarketType(row["market"]),
                industry=row["industry"],
            )
        return None

    async def get_latest_daily(self, stock_code: str) -> Optional[StockDaily]:
        """获取最新日线数据"""
        db = await self._get_db()
        rows = await db.execute(
            """
            SELECT * FROM stock_dailys 
            WHERE stock_code = ? 
            ORDER BY trade_date DESC LIMIT 1
            """,
            (stock_code,),
            fetch=True,
        )
        if rows:
            row = rows[0]
            return StockDaily(
                stock_code=row["stock_code"],
                trade_date=date.fromisoformat(row["trade_date"]),
                open=row["open"],
                high=row["high"],
                low=row["low"],
                close=row["close"],
                pre_close=row["pre_close"],
                change=row["change"],
                pct_change=row["pct_change"],
                volume=row["volume"],
                amount=row["amount"],
            )
        return None

    async def get_daily_history(
        self, stock_code: str, days: int = 60
    ) -> list[StockDaily]:
        """获取历史日线数据"""
        db = await self._get_db()
        rows = await db.execute(
            """
            SELECT * FROM stock_dailys 
            WHERE stock_code = ? 
            ORDER BY trade_date DESC LIMIT ?
            """,
            (stock_code, days),
            fetch=True,
        )
        return [
            StockDaily(
                stock_code=row["stock_code"],
                trade_date=date.fromisoformat(row["trade_date"]),
                open=row["open"],
                high=row["high"],
                low=row["low"],
                close=row["close"],
                pre_close=row["pre_close"],
                change=row["change"],
                pct_change=row["pct_change"],
                volume=row["volume"],
                amount=row["amount"],
            )
            for row in rows
        ]

    async def list_stocks(self) -> list[Stock]:
        """列出所有股票"""
        db = await self._get_db()
        rows = await db.execute("SELECT * FROM stocks ORDER BY code", fetch=True)
        from ..models.stock import MarketType
        return [
            Stock(
                code=row["code"],
                name=row["name"],
                full_code=row["full_code"],
                market=MarketType(row["market"]),
                industry=row["industry"],
            )
            for row in rows
        ]
