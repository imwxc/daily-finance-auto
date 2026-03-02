"""数据库连接和初始化"""

import aiosqlite
import asyncio
import logging
import sqlite3
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class Database:
    """异步 SQLite 数据库"""

    def __init__(self, db_path: str = "./data/finance.db"):
        self.db_path = db_path
        self._conn: Optional[aiosqlite.Connection] = None
        self._lock = asyncio.Lock()

    async def connect(self) -> None:
        """连接数据库"""
        if self._conn is not None:
            return

        # 确保目录存在
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        self._conn = await aiosqlite.connect(self.db_path)
        self._conn.row_factory = aiosqlite.Row
        logger.info(f"数据库已连接: {self.db_path}")

    async def close(self) -> None:
        """关闭数据库连接"""
        if self._conn is not None:
            await self._conn.close()
            self._conn = None
            logger.info("数据库连接已关闭")

    async def init_tables(self) -> None:
        """初始化数据库表"""
        if self._conn is None:
            await self.connect()

        await self._conn.executescript("""
            -- 基金基础信息表
            CREATE TABLE IF NOT EXISTS funds (
                code TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                full_code TEXT UNIQUE NOT NULL,
                fund_type TEXT DEFAULT 'other',
                manager TEXT,
                company TEXT,
                establish_date TEXT,
                benchmark TEXT,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            -- 基金净值表
            CREATE TABLE IF NOT EXISTS fund_navs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fund_code TEXT NOT NULL,
                nav_date TEXT NOT NULL,
                unit_nav REAL NOT NULL,
                acc_nav REAL,
                daily_growth REAL,
                purchase_status TEXT,
                redeem_status TEXT,
                dividend REAL,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(fund_code, nav_date),
                FOREIGN KEY (fund_code) REFERENCES funds(code)
            );

            -- 股票基础信息表
            CREATE TABLE IF NOT EXISTS stocks (
                code TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                full_code TEXT UNIQUE NOT NULL,
                market TEXT NOT NULL,
                industry TEXT,
                list_date TEXT,
                total_shares REAL,
                float_shares REAL,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            -- 股票日线数据表
            CREATE TABLE IF NOT EXISTS stock_dailys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stock_code TEXT NOT NULL,
                trade_date TEXT NOT NULL,
                open REAL NOT NULL,
                high REAL NOT NULL,
                low REAL NOT NULL,
                close REAL NOT NULL,
                pre_close REAL,
                change REAL,
                pct_change REAL,
                volume REAL,
                amount REAL,
                turnover_rate REAL,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(stock_code, trade_date),
                FOREIGN KEY (stock_code) REFERENCES stocks(code)
            );

            -- 投资信号记录表
            CREATE TABLE IF NOT EXISTS invest_signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target_code TEXT NOT NULL,
                target_name TEXT NOT NULL,
                signal_type TEXT NOT NULL,
                strength INTEGER NOT NULL,
                base_amount REAL NOT NULL,
                suggested_amount REAL NOT NULL,
                reason TEXT NOT NULL,
                indicators TEXT,
                signal_date TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            -- 创建索引
            CREATE INDEX IF NOT EXISTS idx_fund_navs_date ON fund_navs(nav_date);
            CREATE INDEX IF NOT EXISTS idx_fund_navs_code ON fund_navs(fund_code);
            CREATE INDEX IF NOT EXISTS idx_stock_dailys_date ON stock_dailys(trade_date);
            CREATE INDEX IF NOT EXISTS idx_stock_dailys_code ON stock_dailys(stock_code);
            CREATE INDEX IF NOT EXISTS idx_signals_date ON invest_signals(signal_date);
        """)
        await self._conn.commit()
        logger.info("数据库表初始化完成")

    @property
    def conn(self) -> aiosqlite.Connection:
        if self._conn is None:
            raise RuntimeError("数据库未连接，请先调用 connect()")
        return self._conn

    async def execute(
        self, sql: str, params: tuple = (), *, fetch: bool = False
    ) -> list[aiosqlite.Row] | None:
        """执行 SQL"""
        async with self._lock:
            cursor = await self.conn.execute(sql, params)
            if fetch:
                return await cursor.fetchall()
            await self.conn.commit()
            return None

    async def executemany(
        self, sql: str, params_list: list[tuple]
    ) -> None:
        """批量执行 SQL"""
        async with self._lock:
            await self.conn.executemany(sql, params_list)
            await self.conn.commit()


# 全局数据库实例
_db: Optional[Database] = None


async def get_database(db_path: str | None = None) -> Database:
    """获取数据库实例"""
    global _db
    if _db is None:
        if db_path is None:
            from ..config import get_config
            config = get_config()
            db_path = config.database.sqlite_path
        _db = Database(db_path)
        await _db.connect()
        await _db.init_tables()
    return _db


async def close_database() -> None:
    """关闭数据库连接"""
    global _db
    if _db is not None:
        await _db.close()
        _db = None
