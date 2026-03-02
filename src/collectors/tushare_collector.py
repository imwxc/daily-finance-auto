"""Tushare 股票数据采集器"""

import logging
import os
from datetime import date, datetime, timedelta

from ..models.stock import Stock, StockDaily
from .base import BaseCollector, CollectorResult

logger = logging.getLogger(__name__)


class TushareStockCollector(BaseCollector[StockDaily]):
    """Tushare 股票数据采集器"""

    def __init__(self, token: str | None = None):
        super().__init__("TushareStock")
        self._token = token or os.getenv("TUSHARE_TOKEN")
        self._pro = None

    def _get_pro(self):
        """获取 Tushare Pro API 实例"""
        if self._pro is None:
            if not self._token:
                raise ValueError("未配置 Tushare Token，请设置 TUSHARE_TOKEN 环境变量")
            import tushare as ts

            ts.set_token(self._token)
            self._pro = ts.pro_api()
        return self._pro

    async def collect(
        self,
        stock_code: str,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> CollectorResult[StockDaily]:
        """
        采集股票日线数据

        Args:
            stock_code: 股票代码 (如 600519.SH)
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
        """
        try:
            pro = self._get_pro()

            # 默认获取最近 30 天数据
            if end_date is None:
                end_date = date.today().strftime("%Y%m%d")
            if start_date is None:
                start_date = (date.today() - timedelta(days=60)).strftime("%Y%m%d")

            df = pro.daily(
                ts_code=stock_code,
                start_date=start_date,
                end_date=end_date,
            )

            if df is None or df.empty:
                return CollectorResult(
                    success=False,
                    error=f"未获取到股票 {stock_code} 的数据",
                    source=self.name,
                )

            # 转换数据
            daily_list = []
            for _, row in df.iterrows():
                try:
                    daily = StockDaily(
                        stock_code=row["ts_code"].split(".")[0],
                        trade_date=self._parse_date(row["trade_date"]),
                        open=float(row["open"]),
                        high=float(row["high"]),
                        low=float(row["low"]),
                        close=float(row["close"]),
                        pre_close=self._parse_float(row.get("pre_close")),
                        change=self._parse_float(row.get("change")),
                        pct_change=self._parse_float(row.get("pct_chg")),
                        volume=self._parse_float(row.get("vol")),
                        amount=self._parse_float(row.get("amount")),
                    )
                    daily_list.append(daily)
                except (ValueError, TypeError) as e:
                    logger.warning(f"解析数据行失败: {row}, 错误: {e}")
                    continue

            return CollectorResult(
                success=True,
                data=daily_list,
                source=self.name,
                count=len(daily_list),
            )

        except Exception as e:
            logger.error(f"采集股票 {stock_code} 数据失败: {e}")
            return CollectorResult(
                success=False,
                error=str(e),
                source=self.name,
            )

    async def collect_stock_info(self, stock_code: str) -> CollectorResult[Stock]:
        """采集股票基础信息"""
        try:
            pro = self._get_pro()

            # 解析代码和市场
            code, market = stock_code.split(".")

            df = pro.stock_basic(ts_code=stock_code, fields=",".join([
                "ts_code", "name", "market", "industry",
                "list_date", "total_share", "float_share"
            ]))

            if df is None or df.empty:
                return CollectorResult(
                    success=False,
                    error=f"未获取到股票 {stock_code} 的基础信息",
                    source=self.name,
                )

            row = df.iloc[0]
            from ..models.stock import MarketType

            stock = Stock(
                code=code,
                name=row["name"],
                full_code=stock_code,
                market=MarketType(market.lower()),
                industry=row.get("industry"),
                list_date=self._parse_date(row.get("list_date")),
                total_shares=self._parse_float(row.get("total_share")),
                float_shares=self._parse_float(row.get("float_share")),
            )

            return CollectorResult(
                success=True,
                data=[stock],
                source=self.name,
                count=1,
            )

        except Exception as e:
            logger.error(f"采集股票 {stock_code} 基础信息失败: {e}")
            return CollectorResult(
                success=False,
                error=str(e),
                source=self.name,
            )

    async def collect_batch(
        self,
        stock_codes: list[str],
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> CollectorResult[StockDaily]:
        """批量采集多个股票的日线数据"""
        all_dailys = []
        errors = []

        for code in stock_codes:
            result = await self.collect(code, start_date, end_date)
            if result.success:
                all_dailys.extend(result.data)
            else:
                errors.append(f"{code}: {result.error}")

        if errors:
            logger.warning(f"部分股票采集失败: {errors}")

        return CollectorResult(
            success=len(all_dailys) > 0,
            data=all_dailys,
            error="; ".join(errors) if errors else None,
            source=self.name,
            count=len(all_dailys),
        )

    @staticmethod
    def _parse_date(value) -> date | None:
        """解析日期"""
        if value is None:
            return None
        if isinstance(value, date):
            return value
        if isinstance(value, str):
            try:
                return datetime.strptime(value, "%Y%m%d").date()
            except ValueError:
                pass
            for fmt in ["%Y-%m-%d", "%Y/%m/%d"]:
                try:
                    return datetime.strptime(value, fmt).date()
                except ValueError:
                    continue
        return None

    @staticmethod
    def _parse_float(value) -> float | None:
        """解析浮点数"""
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            try:
                return float(value.strip())
            except ValueError:
                return None
        return None
