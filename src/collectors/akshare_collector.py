"""AKShare 基金数据采集器"""

import logging
from datetime import date, datetime

import akshare as ak

from ..models.fund import Fund, FundNav
from .base import BaseCollector, CollectorResult

logger = logging.getLogger(__name__)


class AKShareFundCollector(BaseCollector[FundNav]):
    """AKShare 基金净值采集器"""

    def __init__(self):
        super().__init__("AKShareFund")

    async def collect(self, fund_code: str, days: int = 30) -> CollectorResult[FundNav]:
        """
        采集基金净值数据

        Args:
            fund_code: 基金代码 (6位数字)
            days: 获取最近 N 天的数据
        """
        try:
            # AKShare 获取基金净值 (API 参数已更新: fund -> symbol)
            # 去掉 .OF 后缀
            code = fund_code.replace(".OF", "").replace(".of", "")
            df = ak.fund_open_fund_info_em(symbol=code, indicator="单位净值走势")

            if df is None or df.empty:
                return CollectorResult(
                    success=False,
                    error=f"未获取到基金 {fund_code} 的数据",
                    source=self.name,
                )

            # 转换数据 - 使用 tail(days) 获取最新数据
            nav_list = []
            # 数据从旧到新排序，tail(days) 获取最新的数据
            for _, row in df.tail(days).iterrows():
                try:
                    nav = FundNav(
                        fund_code=fund_code,
                        nav_date=self._parse_date(row.get("净值日期")),
                        unit_nav=float(row.get("单位净值", 0)),
                        acc_nav=self._parse_float(row.get("累计净值")),
                        daily_growth=self._parse_float(row.get("日增长率")),
                    )
                    nav_list.append(nav)
                except (ValueError, TypeError) as e:
                    logger.warning(f"解析数据行失败: {row}, 错误: {e}")
                    continue

            return CollectorResult(
                success=True,
                data=nav_list,
                source=self.name,
                count=len(nav_list),
            )

        except Exception as e:
            logger.error(f"采集基金 {fund_code} 数据失败: {e}")
            return CollectorResult(
                success=False,
                error=str(e),
                source=self.name,
            )

    async def collect_fund_info(self, fund_code: str) -> CollectorResult[Fund]:
        """采集基金基础信息"""
        try:
            df = ak.fund_individual_basic_info_xq(fund=fund_code)

            if df is None or df.empty:
                return CollectorResult(
                    success=False,
                    error=f"未获取到基金 {fund_code} 的基础信息",
                    source=self.name,
                )

            # 解析基础信息
            info_dict = dict(zip(df["item"], df["value"]))

            fund = Fund(
                code=fund_code,
                name=info_dict.get("基金简称", ""),
                full_code=f"{fund_code}.OF",
                manager=info_dict.get("基金经理"),
                company=info_dict.get("基金管理人"),
            )

            return CollectorResult(
                success=True,
                data=[fund],
                source=self.name,
                count=1,
            )

        except Exception as e:
            logger.error(f"采集基金 {fund_code} 基础信息失败: {e}")
            return CollectorResult(
                success=False,
                error=str(e),
                source=self.name,
            )

    async def collect_batch(
        self, fund_codes: list[str], days: int = 30
    ) -> CollectorResult[FundNav]:
        """批量采集多个基金的净值数据"""
        all_navs = []
        errors = []

        for code in fund_codes:
            result = await self.collect(code, days)
            if result.success:
                all_navs.extend(result.data)
            else:
                errors.append(f"{code}: {result.error}")

        if errors:
            logger.warning(f"部分基金采集失败: {errors}")

        return CollectorResult(
            success=len(all_navs) > 0,
            data=all_navs,
            error="; ".join(errors) if errors else None,
            source=self.name,
            count=len(all_navs),
        )

    @staticmethod
    def _parse_date(value) -> date | None:
        """解析日期"""
        if value is None:
            return None
        if isinstance(value, date):
            return value
        if isinstance(value, str):
            # 尝试多种格式
            for fmt in ["%Y-%m-%d", "%Y/%m/%d", "%Y%m%d"]:
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
            # 移除百分号
            value = value.replace("%", "").strip()
            try:
                return float(value)
            except ValueError:
                return None
        return None
