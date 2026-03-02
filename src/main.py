#!/usr/bin/env python3
"""CLI 入口"""

import asyncio
import logging
import sys
from datetime import date
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table

from .config import Config, load_config
from .storage import FundRepository, StockRepository, close_database, get_database

# 延迟导入采集器
AKShareFundCollector = None
TushareStockCollector = None


def _get_akshare_collector():
    global AKShareFundCollector
    if AKShareFundCollector is None:
        from .collectors import AKShareFundCollector as _AKShareFundCollector
        AKShareFundCollector = _AKShareFundCollector
    return AKShareFundCollector


def _get_tushare_collector():
    global TushareStockCollector
    if TushareStockCollector is None:
        from .collectors import TushareStockCollector as _TushareStockCollector
        TushareStockCollector = _TushareStockCollector
    return TushareStockCollector

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

console = Console()


def async_command(f):
    """将异步函数转换为 Click 命令"""
    import functools

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))

    return wrapper


@click.group()
@click.option("--config", "-c", type=click.Path(), help="配置文件路径")
@click.option("--verbose", "-v", is_flag=True, help="显示详细日志")
@click.pass_context
def cli(ctx: click.Context, config: Optional[str], verbose: bool):
    """每日自动化基金信息 + 股票信息采集系统"""
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    ctx.ensure_object(dict)
    ctx.obj["config_path"] = config


@cli.command()
@click.pass_context
@async_command
async def init(ctx: click.Context):
    """初始化数据库"""
    config_path = ctx.obj.get("config_path")
    cfg = load_config(config_path)

    console.print("[bold blue]初始化数据库...[/bold blue]")

    db = await get_database(cfg.database.sqlite_path)
    console.print(f"[green]✓[/green] 数据库已创建: {cfg.database.sqlite_path}")

    await close_database()
    console.print("[green]✓[/green] 初始化完成!")


@cli.command()
@click.option("--type", "-t", "data_type", type=click.Choice(["fund", "stock", "all"]),
              default="all", help="采集数据类型")
@click.option("--days", "-d", default=30, help="采集最近 N 天数据")
@click.pass_context
@async_command
async def collect(ctx: click.Context, data_type: str, days: int):
    """采集数据"""
    config_path = ctx.obj.get("config_path")
    cfg = load_config(config_path)

    console.print(f"[bold blue]开始采集数据 (类型: {data_type}, 天数: {days})[/bold blue]")

    try:
        # 初始化数据库
        await get_database(cfg.database.sqlite_path)

        if data_type in ("fund", "all"):
            await _collect_funds(cfg, days)

        if data_type in ("stock", "all"):
            await _collect_stocks(cfg, days)

        console.print("[green]✓[/green] 数据采集完成!")

    finally:
        await close_database()


async def _collect_funds(cfg: Config, days: int):
    """采集基金数据"""
    if not cfg.funds:
        console.print("[yellow]未配置基金监控列表[/yellow]")
        return

    AKShareFundCollector = _get_akshare_collector()
    collector = AKShareFundCollector()
    repo = FundRepository()

    fund_codes = [f.code for f in cfg.funds]
    console.print(f"[blue]采集 {len(fund_codes)} 只基金数据...[/blue]")

    result = await collector.collect_batch(fund_codes, days)

    if result.success:
        await repo.save_fund_navs(result.data)
        console.print(f"[green]✓[/green] 采集 {result.count} 条基金净值数据")
    else:
        console.print(f"[red]✗[/red] 基金数据采集失败: {result.error}")

async def _collect_stocks(cfg: Config, days: int):
    """采集股票数据"""
    if not cfg.stocks:
        console.print("[yellow]未配置股票监控列表[/yellow]")
        return

    if not cfg.tushare.token:
        console.print("[red]✗[/red] 未配置 Tushare Token，跳过股票数据采集")
        return

    TushareStockCollector = _get_tushare_collector()
    collector = TushareStockCollector(cfg.tushare.token)
    repo = StockRepository()

    stock_codes = [s.code for s in cfg.stocks]
    console.print(f"[blue]采集 {len(stock_codes)} 只股票数据...[/blue]")

    result = await collector.collect_batch(stock_codes)

    if result.success:
        await repo.save_stock_dailys(result.data)
        console.print(f"[green]✓[/green] 采集 {result.count} 条股票日线数据")
    else:
        console.print(f"[red]✗[/red] 股票数据采集失败: {result.error}")

@cli.command()
@click.pass_context
@async_command
async def status(ctx: click.Context):
    """查看系统状态"""
    config_path = ctx.obj.get("config_path")
    cfg = load_config(config_path)

    # 检查数据库
    db_path = Path(cfg.database.sqlite_path)
    db_exists = db_path.exists()

    table = Table(title="系统状态")
    table.add_column("项目", style="cyan")
    table.add_column("状态", style="green")

    table.add_row("数据库", "✓ 已初始化" if db_exists else "✗ 未初始化")
    table.add_row("基金监控", f"{len(cfg.funds)} 只")
    table.add_row("股票监控", f"{len(cfg.stocks)} 只")
    table.add_row("Tushare Token", "✓ 已配置" if cfg.tushare.token else "✗ 未配置")
    table.add_row("微信推送", "✓ 已启用" if cfg.notify.wechat.enabled else "○ 未启用")
    table.add_row("邮件推送", "✓ 已启用" if cfg.notify.email.enabled else "○ 未启用")

    console.print(table)

    if not db_exists:
        console.print("\n[yellow]提示: 请先运行 `daily-finance init` 初始化数据库[/yellow]")


@cli.command()
@click.pass_context
@async_command
async def funds(ctx: click.Context):
    """查看基金列表和最新净值"""
    config_path = ctx.obj.get("config_path")
    cfg = load_config(config_path)

    await get_database(cfg.database.sqlite_path)
    repo = FundRepository()

    table = Table(title="基金监控列表")
    table.add_column("代码", style="cyan")
    table.add_column("名称", style="green")
    table.add_column("最新净值", justify="right")
    table.add_column("日期", style="dim")
    table.add_column("涨跌", justify="right")

    for fund_cfg in cfg.funds:
        latest = await repo.get_latest_nav(fund_cfg.code)

        row = [fund_cfg.code, fund_cfg.name]
        if latest:
            row.append(f"{latest.unit_nav:.4f}")
            row.append(str(latest.nav_date))
            if latest.daily_growth is not None:
                color = "green" if latest.daily_growth >= 0 else "red"
                sign = "+" if latest.daily_growth >= 0 else ""
                row.append(f"[{color}]{sign}{latest.daily_growth:.2f}%[/{color}]")
            else:
                row.append("-")
        else:
            row.extend(["-", "无数据", "-"])

        table.add_row(*row)

    console.print(table)
    await close_database()


@cli.command()
@click.pass_context
@async_command
async def stocks(ctx: click.Context):
    """查看股票列表和最新行情"""
    config_path = ctx.obj.get("config_path")
    cfg = load_config(config_path)

    await get_database(cfg.database.sqlite_path)
    repo = StockRepository()

    table = Table(title="股票监控列表")
    table.add_column("代码", style="cyan")
    table.add_column("名称", style="green")
    table.add_column("最新价", justify="right")
    table.add_column("日期", style="dim")
    table.add_column("涨跌", justify="right")

    for stock_cfg in cfg.stocks:
        latest = await repo.get_latest_daily(stock_cfg.code.split(".")[0])

        row = [stock_cfg.code, stock_cfg.name]
        if latest:
            row.append(f"{latest.close:.2f}")
            row.append(str(latest.trade_date))
            if latest.pct_change is not None:
                color = "green" if latest.pct_change >= 0 else "red"
                sign = "+" if latest.pct_change >= 0 else ""
                row.append(f"[{color}]{sign}{latest.pct_change:.2f}%[/{color}]")
            else:
                row.append("-")
        else:
            row.extend(["-", "无数据", "-"])

        table.add_row(*row)

    console.print(table)
    await close_database()


@cli.command()
@click.pass_context
def config(ctx: click.Context):
    """显示当前配置"""
    config_path = ctx.obj.get("config_path")
    cfg = load_config(config_path)

    console.print("[bold]当前配置:[/bold]")
    console.print(f"  数据库: {cfg.database.type} ({cfg.database.sqlite_path})")
    console.print(f"  定投频率: {cfg.investment.frequency}")
    console.print(f"  采集时间: {cfg.schedule.collect_time}")
    console.print(f"  定投时间: {cfg.schedule.invest_time}")


@cli.command()
@click.option("--notify/--no-notify", default=False, help="是否推送通知")
@click.pass_context
@async_command
async def invest(ctx: click.Context, notify: bool):
    """检查定投信号"""
    config_path = ctx.obj.get("config_path")
    cfg = load_config(config_path)

    console.print("[bold blue]检查定投信号...[/bold blue]")

    try:
        await get_database(cfg.database.sqlite_path)
        repo = FundRepository()

        from .strategies import MADeviationStrategy

        strategy = MADeviationStrategy()
        signals = []

        for fund_cfg in cfg.funds:
            navs = await repo.get_nav_history(fund_cfg.code, days=60)

            if len(navs) < 20:
                console.print(f"[yellow]{fund_cfg.name}: 数据不足[/yellow]")
                continue

            result = await strategy.analyze(navs, fund_cfg.amount)
            signals.append(result.signal)

            # 打印信号
            console.print(
                f"{result.signal.emoji} {fund_cfg.name} ({fund_cfg.code}): "
                f"{result.signal.signal_type.value} "
                f"[{result.signal.strength}] "
                f"{result.signal.suggested_amount:.0f}元 "
                f"({result.signal.multiplier}x)"
            )
            console.print(f"   原因: {result.signal.reason}")

        # 发送通知
        if notify and signals:
            await _send_invest_notification(cfg, signals)

    finally:
        await close_database()


async def _send_invest_notification(cfg: Config, signals: list):
    """发送定投信号通知"""
    from .notify import WechatNotifier, EmailNotifier
    from ..models.signal import SignalType

    # 生成报告内容
    lines = ["📊 定投信号报告", ""]
    for signal in signals:
        lines.append(f"{signal.emoji} {signal.target_name}")
        lines.append(f"   类型: {signal.signal_type.value}")
        lines.append(f"   强度: {signal.strength}")
        lines.append(f"   金额: {signal.suggested_amount:.0f}元 ({signal.multiplier}x)")
        lines.append(f"   原因: {signal.reason}")
        lines.append("")

    content = "\n".join(lines)

    # 微信推送
    if cfg.notify.wechat.enabled and cfg.notify.wechat.send_key:
        notifier = WechatNotifier(cfg.notify.wechat.send_key)
        result = await notifier.send("📊 定投信号报告", content)
        if result.success:
            console.print("[green]✓[/green] 微信推送成功")
        else:
            console.print(f"[red]✗[/red] 微信推送失败: {result.error}")

    # 邮件推送
    if cfg.notify.email.enabled:
        notifier = EmailNotifier(
            smtp_server=cfg.notify.email.smtp_server,
            smtp_port=cfg.notify.email.smtp_port,
            sender=cfg.notify.email.sender,
            password=cfg.notify.email.password,
            receiver=cfg.notify.email.receiver,
        )
        result = await notifier.send("📊 定投信号报告", content)
        if result.success:
            console.print("[green]✓[/green] 邮件推送成功")
        else:
            console.print(f"[red]✗[/red] 邮件推送失败: {result.error}")
@cli.command()
@click.argument("code")
@click.pass_context
@async_command
async def analyze(ctx: click.Context, code: str):
    """分析股票技术指标"""
    config_path = ctx.obj.get("config_path")
    cfg = load_config(config_path)

    console.print(f"[bold blue]分析股票 {code}...[/bold blue]")

    try:
        await get_database(cfg.database.sqlite_path)
        repo = StockRepository()

        # 获取历史数据
        dailys = await repo.get_daily_history(code, days=60)

        if len(dailys) < 20:
            console.print("[red]数据不足，需要至少 20 条日线数据[/red]")
            return

        from .analyzers import StockAnalyzer

        analyzer = StockAnalyzer(dailys)
        result = analyzer.analyze()

        # 显示分析结果
        latest = dailys[0]
        console.print(f"\n[bold]{code}[/bold] - {latest.trade_date}")
        console.print(f"最新价: {latest.close:.2f}")

        # 均线分析
        ma = result["ma"]
        console.print(f"\n[cyan]均线分析[/cyan]")
        console.print(f"  MA5: {ma['ma5']:.2f}  MA20: {ma['ma20']:.2f}  MA60: {ma.get('ma60', 'N/A')}")
        console.print(f"  信号: {ma['signal']}")

        # MACD 分析
        macd = result["macd"]
        console.print(f"\n[cyan]MACD[/cyan]")
        console.print(f"  DIF: {macd['dif']}  DEA: {macd['dea']}  MACD: {macd['macd']}")
        console.print(f"  信号: {macd['signal']}")

        # RSI 分析
        rsi = result["rsi"]
        console.print(f"\n[cyan]RSI[/cyan]")
        console.print(f"  RSI(14): {rsi['rsi']}")
        console.print(f"  信号: {rsi['signal']}")

        # 布林带
        bb = result["bollinger"]
        console.print(f"\n[cyan]布林带[/cyan]")
        console.print(f"  上轨: {bb['upper']}  中轨: {bb['middle']}  下轨: {bb['lower']}")
        console.print(f"  信号: {bb['signal']}")

        # 趋势
        trend = result["trend"]
        console.print(f"\n[cyan]趋势分析[/cyan]")
        console.print(f"  5日涨跌: {trend.get('change_5d', 0):.2f}%")
        console.print(f"  20日涨跌: {trend.get('change_20d', 0):.2f}%")
        console.print(f"  波动率: {trend.get('volatility', 0):.2f}%")
        console.print(f"  趋势: {trend.get('trend', 'unknown')}")

    finally:
        await close_database()
def main():
    """主入口"""
    cli(obj={})


if __name__ == "__main__":
    main()
