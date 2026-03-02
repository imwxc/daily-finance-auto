"""基金数据仓库"""

import logging
from datetime import date
from typing import Optional

import aiosqlite

from ..models.fund import Fund, FundNav
from .database import Database, get_database

logger = logging.getLogger(__name__)


class FundRepository:
    """基金数据仓库"""

    def __init__(self, db: Optional[Database] = None):
        self._db = db

    async def _get_db(self) -> Database:
        if self._db is None:
            self._db = await get_database()
        return self._db

    async def save_fund(self, fund: Fund) -> None:
        """保存基金基础信息"""
        db = await self._get_db()
        await db.execute(
            """
            INSERT INTO funds (code, name, full_code, fund_type, manager, company, 
                               establish_date, benchmark, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(code) DO UPDATE SET
                name = excluded.name,
                fund_type = excluded.fund_type,
                manager = excluded.manager,
                company = excluded.company,
                establish_date = excluded.establish_date,
                benchmark = excluded.benchmark,
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                fund.code,
                fund.name,
                fund.full_code,
                fund.fund_type.value,
                fund.manager,
                fund.company,
                fund.establish_date.isoformat() if fund.establish_date else None,
                fund.benchmark,
            ),
        )
        logger.debug(f"保存基金信息: {fund.code} - {fund.name}")

    async def save_fund_navs(self, navs: list[FundNav]) -> int:
        """批量保存基金净值"""
        if not navs:
            return 0

        db = await self._get_db()
        params_list = [
            (
                nav.fund_code,
                nav.nav_date.isoformat(),
                nav.unit_nav,
                nav.acc_nav,
                nav.daily_growth,
                nav.purchase_status,
                nav.redeem_status,
                nav.dividend,
            )
            for nav in navs
        ]

        await db.executemany(
            """
            INSERT INTO fund_navs (fund_code, nav_date, unit_nav, acc_nav, daily_growth,
                                   purchase_status, redeem_status, dividend, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(fund_code, nav_date) DO UPDATE SET
                unit_nav = excluded.unit_nav,
                acc_nav = excluded.acc_nav,
                daily_growth = excluded.daily_growth,
                purchase_status = excluded.purchase_status,
                redeem_status = excluded.redeem_status,
                dividend = excluded.dividend,
                updated_at = CURRENT_TIMESTAMP
            """,
            params_list,
        )
        logger.info(f"保存 {len(navs)} 条基金净值数据")
        return len(navs)

    async def get_fund(self, code: str) -> Optional[Fund]:
        """获取基金基础信息"""
        db = await self._get_db()
        rows = await db.execute(
            "SELECT * FROM funds WHERE code = ?", (code,), fetch=True
        )
        if rows:
            row = rows[0]
            return Fund(
                code=row["code"],
                name=row["name"],
                full_code=row["full_code"],
                manager=row["manager"],
                company=row["company"],
            )
        return None

    async def get_latest_nav(self, fund_code: str) -> Optional[FundNav]:
        """获取最新净值"""
        db = await self._get_db()
        rows = await db.execute(
            """
            SELECT * FROM fund_navs 
            WHERE fund_code = ? 
            ORDER BY nav_date DESC LIMIT 1
            """,
            (fund_code,),
            fetch=True,
        )
        if rows:
            row = rows[0]
            return FundNav(
                fund_code=row["fund_code"],
                nav_date=date.fromisoformat(row["nav_date"]),
                unit_nav=row["unit_nav"],
                acc_nav=row["acc_nav"],
                daily_growth=row["daily_growth"],
            )
        return None

    async def get_nav_history(
        self, fund_code: str, days: int = 30
    ) -> list[FundNav]:
        """获取历史净值"""
        db = await self._get_db()
        rows = await db.execute(
            """
            SELECT * FROM fund_navs 
            WHERE fund_code = ? 
            ORDER BY nav_date DESC LIMIT ?
            """,
            (fund_code, days),
            fetch=True,
        )
        return [
            FundNav(
                fund_code=row["fund_code"],
                nav_date=date.fromisoformat(row["nav_date"]),
                unit_nav=row["unit_nav"],
                acc_nav=row["acc_nav"],
                daily_growth=row["daily_growth"],
            )
            for row in rows
        ]

    async def list_funds(self) -> list[Fund]:
        """列出所有基金"""
        db = await self._get_db()
        rows = await db.execute("SELECT * FROM funds ORDER BY code", fetch=True)
        return [
            Fund(
                code=row["code"],
                name=row["name"],
                full_code=row["full_code"],
                manager=row["manager"],
                company=row["company"],
            )
            for row in rows
        ]
