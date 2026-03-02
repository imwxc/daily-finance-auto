"""配置加载模块"""

import os
from pathlib import Path
from typing import Any, Optional

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class TushareConfig(BaseModel):
    """Tushare API 配置"""

    token: str = Field(default="", description="Tushare API Token")


class DatabaseConfig(BaseModel):
    """数据库配置"""

    type: str = Field(default="sqlite", description="数据库类型: sqlite | postgresql")

    # SQLite 配置
    sqlite_path: str = Field(default="./data/finance.db", description="SQLite 数据库路径")

    # PostgreSQL 配置
    postgresql_host: str = Field(default="localhost")
    postgresql_port: int = Field(default=5432)
    postgresql_database: str = Field(default="finance")
    postgresql_user: str = Field(default="postgres")
    postgresql_password: str = Field(default="")

    @property
    def sqlite_url(self) -> str:
        """SQLite 连接 URL"""
        return f"sqlite:///{self.sqlite_path}"

    @property
    def postgresql_url(self) -> str:
        """PostgreSQL 连接 URL"""
        return (
            f"postgresql://{self.postgresql_user}:{self.postgresql_password}"
            f"@{self.postgresql_host}:{self.postgresql_port}/{self.postgresql_database}"
        )

    @property
    def database_url(self) -> str:
        """获取当前数据库连接 URL"""
        if self.type == "postgresql":
            return self.postgresql_url
        return self.sqlite_url


class FundWatchConfig(BaseModel):
    """基金监控配置"""

    code: str
    name: str
    amount: float = 1000
    strategy: str = "ma_deviation"


class StockWatchConfig(BaseModel):
    """股票监控配置"""

    code: str
    name: str
    shares: float = 0
    cost_price: Optional[float] = None


class InvestmentConfig(BaseModel):
    """定投策略配置"""

    frequency: str = Field(default="weekly", description="定投频率: daily | weekly | monthly")
    day_of_week: int = Field(default=3, description="每周几定投 (0=周一, 4=周五)")
    day_of_month: int = Field(default=1, description="每月几号定投")


class WechatNotifyConfig(BaseModel):
    """微信推送配置 (Server酱)"""

    enabled: bool = False
    send_key: str = ""


class EmailNotifyConfig(BaseModel):
    """邮件通知配置"""

    enabled: bool = False
    smtp_server: str = "smtp.qq.com"
    smtp_port: int = 465
    sender: str = ""
    password: str = ""
    receiver: str = ""


class NotifyConfig(BaseModel):
    """通知配置"""

    wechat: WechatNotifyConfig = Field(default_factory=WechatNotifyConfig)
    email: EmailNotifyConfig = Field(default_factory=EmailNotifyConfig)


class ScheduleConfig(BaseModel):
    """调度配置"""

    collect_time: str = Field(default="16:30", description="数据采集时间")
    invest_time: str = Field(default="09:30", description="定投执行时间")


class Config(BaseModel):
    """主配置"""

    tushare: TushareConfig = Field(default_factory=TushareConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    funds: list[FundWatchConfig] = Field(default_factory=list)
    stocks: list[StockWatchConfig] = Field(default_factory=list)
    investment: InvestmentConfig = Field(default_factory=InvestmentConfig)
    notify: NotifyConfig = Field(default_factory=NotifyConfig)
    schedule: ScheduleConfig = Field(default_factory=ScheduleConfig)


def load_config(config_path: Optional[str | Path] = None) -> Config:
    """
    加载配置文件

    Args:
        config_path: 配置文件路径，默认为 ./config.yaml

    Returns:
        Config: 配置对象
    """
    if config_path is None:
        config_path = Path("config.yaml")
    else:
        config_path = Path(config_path)

    if not config_path.exists():
        # 尝试查找配置文件
        possible_paths = [
            Path("config.yaml"),
            Path("config.yml"),
            Path.home() / ".daily-finance" / "config.yaml",
        ]
        for path in possible_paths:
            if path.exists():
                config_path = path
                break
        else:
            # 使用默认配置
            return Config()

    with open(config_path, encoding="utf-8") as f:
        config_data = yaml.safe_load(f) or {}

    # 处理嵌套的 watch_list 结构
    if "funds" in config_data and isinstance(config_data["funds"], dict):
        config_data["funds"] = config_data["funds"].get("watch_list", [])
    if "stocks" in config_data and isinstance(config_data["stocks"], dict):
        config_data["stocks"] = config_data["stocks"].get("watch_list", [])

    # 支持环境变量覆盖敏感配置

    # 支持环境变量覆盖敏感配置
    if tushare_token := os.getenv("TUSHARE_TOKEN"):
        config_data.setdefault("tushare", {})["token"] = tushare_token

    return Config(**config_data)


# 全局配置实例
_config: Optional[Config] = None


def get_config(reload: bool = False) -> Config:
    """
    获取全局配置实例

    Args:
        reload: 是否重新加载配置

    Returns:
        Config: 配置对象
    """
    global _config
    if _config is None or reload:
        _config = load_config()
    return _config
