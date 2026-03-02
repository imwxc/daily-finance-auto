"""数据采集器基类"""

import asyncio
import logging
from abc import ABC, abstractmethod
from datetime import date, datetime
from enum import Enum
from typing import Any, Generic, TypeVar

from pydantic import BaseModel

logger = logging.getLogger(__name__)

T = TypeVar("T")


class CollectorStatus(str, Enum):
    """采集器状态"""

    IDLE = "idle"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


class CollectorResult(BaseModel, Generic[T]):
    """采集结果"""

    success: bool
    data: list[T] = []
    error: str | None = None
    source: str = ""
    collected_at: datetime = datetime.now()
    count: int = 0

    class Config:
        arbitrary_types_allowed = True


class BaseCollector(ABC, Generic[T]):
    """数据采集器基类"""

    def __init__(self, name: str):
        self.name = name
        self.status = CollectorStatus.IDLE
        self._last_error: str | None = None

    @property
    def last_error(self) -> str | None:
        return self._last_error

    @abstractmethod
    async def collect(self, *args, **kwargs) -> CollectorResult[T]:
        """执行数据采集"""
        pass

    async def collect_with_retry(
        self,
        max_retries: int = 3,
        retry_delay: float = 5.0,
        *args,
        **kwargs,
    ) -> CollectorResult[T]:
        """
        带重试的采集

        Args:
            max_retries: 最大重试次数
            retry_delay: 重试间隔(秒)
        """
        self.status = CollectorStatus.RUNNING
        last_error = None

        for attempt in range(max_retries):
            try:
                logger.info(f"[{self.name}] 开始采集 (尝试 {attempt + 1}/{max_retries})")
                result = await self.collect(*args, **kwargs)

                if result.success:
                    self.status = CollectorStatus.SUCCESS
                    logger.info(f"[{self.name}] 采集成功，获取 {result.count} 条数据")
                    return result

                last_error = result.error
                logger.warning(f"[{self.name}] 采集失败: {result.error}")

            except Exception as e:
                last_error = str(e)
                logger.error(f"[{self.name}] 采集异常: {e}")

            if attempt < max_retries - 1:
                logger.info(f"[{self.name}] 等待 {retry_delay} 秒后重试...")
                await asyncio.sleep(retry_delay)

        # 所有重试都失败
        self.status = CollectorStatus.FAILED
        self._last_error = last_error
        return CollectorResult(
            success=False,
            error=last_error,
            source=self.name,
        )

    def sync_collect(self, *args, **kwargs) -> CollectorResult[T]:
        """同步采集（用于 CLI）"""
        return asyncio.run(self.collect_with_retry(*args, **kwargs))
