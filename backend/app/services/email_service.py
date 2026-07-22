import logging
import smtplib
import ssl
from email.mime.text import MIMEText

from app.core.config import get_settings

logger = logging.getLogger(__name__)

# Windows 中文计算机名会导致 EHLO 报 UnicodeEncodeError，固定用 ASCII 主机名
SMTP_LOCAL_HOSTNAME = "localhost"


def _send_email(to_email: str, subject: str, body: str) -> None:
    settings = get_settings()
    if not settings.smtp_user or not settings.smtp_password:
        raise RuntimeError("SMTP 未配置，请在 backend/.env 设置 SMTP_USER / SMTP_PASSWORD（QQ 邮箱授权码）")

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = settings.smtp_from or settings.smtp_user
    msg["To"] = to_email

    if settings.smtp_use_ssl:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(
            settings.smtp_host,
            settings.smtp_port,
            context=context,
            timeout=15,
            local_hostname=SMTP_LOCAL_HOSTNAME,
        ) as server:
            server.login(settings.smtp_user, settings.smtp_password)
            server.send_message(msg)
    else:
        context = ssl.create_default_context()
        with smtplib.SMTP(
            settings.smtp_host,
            settings.smtp_port,
            timeout=15,
            local_hostname=SMTP_LOCAL_HOSTNAME,
        ) as server:
            server.starttls(context=context)
            server.login(settings.smtp_user, settings.smtp_password)
            server.send_message(msg)

    logger.info("email sent to %s", to_email)


def send_verification_email(to_email: str, code: str) -> None:
    subject = "CYINC 注册验证码"
    body = (
        f"你好，\n\n"
        f"你正在注册 CYINC 主站账号，验证码为：{code}\n\n"
        f"验证码 10 分钟内有效，请勿泄露给他人。\n\n"
        f"— CYINC 主站"
    )
    _send_email(to_email, subject, body)


def send_password_reset_email(to_email: str, code: str) -> None:
    subject = "CYINC 重置密码验证码"
    body = (
        f"你好，\n\n"
        f"你正在重置 CYINC 主站账号密码，验证码为：{code}\n\n"
        f"验证码 10 分钟内有效，请勿泄露给他人。若非本人操作请忽略此邮件。\n\n"
        f"— CYINC 主站"
    )
    _send_email(to_email, subject, body)
