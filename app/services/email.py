from email.message import EmailMessage

import aiosmtplib

from app.core.config import settings


async def send_verification_email(
    to_email: str,
    verification_token: str
):
    verification_link = (
        f"http://127.0.0.1:8000/api/v1/auth/verify-email"
        f"?token={verification_token}"
    )

    message = EmailMessage()

    message["From"] = settings.EMAIL_FROM
    message["To"] = to_email
    message["Subject"] = "Verify Your Email Address"

    message.set_content(
        f"""
Hello,

Thank you for registering on AI Technical Hiring Platform.

Please verify your email by clicking the link below:

{verification_link}

This verification link expires in 30 minutes.

If you did not create this account, please ignore this email.

Regards,
AI Technical Hiring Platform
"""
    )

    await aiosmtplib.send(
        message,
        hostname=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        start_tls=True,
        username=settings.SMTP_USER,
        password=settings.SMTP_PASSWORD
    )

async def send_password_reset_email(
    to_email: str,
    reset_token: str
):
    reset_link = (
        f"http://127.0.0.1:8000/api/v1/auth/reset-password"
        f"?token={reset_token}"
    )

    message = EmailMessage()

    message["From"] = settings.EMAIL_FROM
    message["To"] = to_email
    message["Subject"] = "Reset Your Password"

    message.set_content(
        f"""
Hello,

We received a request to reset your password.

Click the link below to reset your password:

{reset_link}

This password reset link expires in 30 minutes.

If you did not request a password reset, please ignore this email.

Regards,
AI Technical Hiring Platform
"""
    )

    await aiosmtplib.send(
        message,
        hostname=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        start_tls=True,
        username=settings.SMTP_USER,
        password=settings.SMTP_PASSWORD
    )