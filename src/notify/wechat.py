"""Server酱微信推送"""

import aiohttp
import logging

from .base import BaseNotifier, NotifyResult

logger = logging.getLogger(__name__)


class WechatNotifier(BaseNotifier):
    """Server酱微信推送"""

    name = "wechat"
    API_URL = "https://sctapi.ftqq.com/{send_key}.send"

    def __init__(self, send_key: str):
        self.send_key = send_key

    async def send(self, title: str, content: str) -> NotifyResult:
        if not self.send_key:
            return NotifyResult(success=False, error="未配置 send_key")

        url = self.API_URL.format(send_key=self.send_key)

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    data={
                        "title": title,
                        "desp": self.format_html(content),
                    },
                ) as resp:
                    result = await resp.json()

                    if resp.status == 200 and result.get("code") == 0:
                        logger.info(f"微信推送成功: {title}")
                        return NotifyResult(
                            success=True,
                            message_id=str(result.get("data", {}).get("msgid", "")),
                        )
                    else:
                        error = result.get("message", "未知错误")
                        logger.error(f"微信推送失败: {error}")
                        return NotifyResult(success=False, error=error)

        except Exception as e:
            logger.error(f"微信推送异常: {e}")
            return NotifyResult(success=False, error=str(e))
