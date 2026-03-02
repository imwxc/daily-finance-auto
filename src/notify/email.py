"""邮件推送"""

import asyncio
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from .base import BaseNotifier, NotifyResult

logger = logging.getLogger(__name__)


class EmailNotifier(BaseNotifier):
    """邮件推送"""

    name = "email"

    def __init__(
        self,
        smtp_server: str,
        smtp_port: int,
        sender: str,
        password: str,
        receiver: str,
    ):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender = sender
        self.password = password
        self.receiver = receiver

    async def send(self, title: str, content: str) -> NotifyResult:
        if not all([self.sender, self.password, self.receiver]):
            return NotifyResult(success=False, error="邮件配置不完整")

        try:
            # 在线程池中执行同步的 SMTP 操作
            result = await asyncio.get_event_loop().run_in_executor(
                None, self._send_email, title, content
            )
            return result
        except Exception as e:
            logger.error(f"邮件推送异常: {e}")
            return NotifyResult(success=False, error=str(e))

    def _send_email(self, title: str, content: str) -> NotifyResult:
        """同步发送邮件"""
        msg = MIMEMultipart("alternative")
        msg["Subject"] = title
        msg["From"] = self.sender
        msg["To"] = self.receiver

        # 纯文本版本
        text_part = MIMEText(content, "plain", "utf-8")
        msg.attach(text_part)

        # HTML 版本
        html_part = MIMEText(self.format_html(content), "html", "utf-8")
        msg.attach(html_part)

        try:
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                server.login(self.sender, self.password)
                server.sendmail(self.sender, [self.receiver], msg.as_string())

            logger.info(f"邮件推送成功: {title}")
            return NotifyResult(success=True)
        except Exception as e:
            logger.error(f"邮件发送失败: {e}")
            return NotifyResult(success=False, error=str(e))
