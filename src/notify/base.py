"""消息推送基类"""

import logging
from abc import ABC, abstractmethod

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class NotifyResult(BaseModel):
    """推送结果"""

    success: bool
    error: str | None = None
    message_id: str | None = None


class BaseNotifier(ABC):
    """消息推送基类"""

    name: str = "base"

    @abstractmethod
    async def send(self, title: str, content: str) -> NotifyResult:
        """发送消息"""
        pass

    def format_html(self, content: str) -> str:
        """格式化为 HTML"""
        return content.replace("\n", "<br>")
