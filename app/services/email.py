import httpx
from app.core.config import settings


RESEND_API_URL = "https://api.resend.com/emails"


async def send_email(to_email: str, subject: str, body: str):
    if not settings.RESEND_API_KEY:
        raise ValueError("RESEND_API_KEY is not configured")

    if not settings.EMAIL_FROM:
        raise ValueError("EMAIL_FROM is not configured")

    payload = {
        "from": settings.EMAIL_FROM,
        "to": [to_email],
        "subject": subject,
        "text": body,
    }

    headers = {
        "Authorization": f"Bearer {settings.RESEND_API_KEY}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.post(
            RESEND_API_URL,
            json=payload,
            headers=headers,
        )
        response.raise_for_status()

    return response.json()


async def send_verification_email(
    to_email: str,
    verification_token: str
):
    verification_link = (
        f"{settings.BACKEND_URL.rstrip('/')}"
        f"/api/v1/auth/verify-email?token={verification_token}"
    )

    body = f"""
Hello,

Thank you for registering on AI Technical Hiring Platform.

Please verify your email by clicking the link below:

{verification_link}

This verification link expires in 30 minutes.

If you did not create this account, please ignore this email.

Regards,
AI Technical Hiring Platform
"""

    await send_email(
        to_email=to_email,
        subject="Verify Your Email Address",
        body=body,
    )


async def send_password_reset_email(
    to_email: str,
    reset_token: str
):
    reset_link = (
        f"{settings.BACKEND_URL.rstrip('/')}"
        f"/api/v1/auth/reset-password?token={reset_token}"
    )

    body = f"""
Hello,

We received a request to reset your password.

Use the link below to reset your password:

{reset_link}

This password reset link expires in 30 minutes.

If you did not request a password reset, please ignore this email.

Regards,
AI Technical Hiring Platform
"""

    await send_email(
        to_email=to_email,
        subject="Reset Your Password",
        body=body,
    )
