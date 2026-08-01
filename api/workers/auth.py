import httpx
from user_agents import parse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_mail import MessageSchema, MessageType, FastMail

from models.db import SessionLocal
from models.user import Session as AuthSession
from libs.mail import conf
from setting import settings
from libs.logger import logger

async def update_session(ctx, session_id, user_agent_string):
    async with SessionLocal() as db:
        try:
            stmt = select(AuthSession).where(AuthSession.session_id == session_id)
            session = await db.scalar(stmt)
            if not session:
                return False

            if user_agent_string:
                user_agent = parse(user_agent_string)
                device_info = str(user_agent).replace("/", "")
                session.user_agent = device_info

            ip = session.ip_address
            if ip and ip not in ("127.0.0.1", "localhost", "::1"):
                async with httpx.AsyncClient() as client:
                    try:
                        res = await client.get(f"http://ip-api.com/json/{ip}?fields=status,country,city,zip", timeout=5.0)
                        r = res.json()
                        if r.get("status") == "success":
                            location = f"{r.get('city', '')}, {r.get('country', '')}. {r.get('zip', '')}"
                            session.location = location
                    except Exception as err:
                        logger.warning(f"Failed to fetch IP geolocation for {ip}: {err}")

            await db.commit()
            return True
        except Exception as e:
            await db.rollback()
            logger.exception(f"Error updating session {session_id}: {e}")
            raise e

async def send_welcome_email(ctx, email, fullname):
    try:
        message = MessageSchema(
            subject="Welcome to Onyx - URL Shortener & Analytics",
            recipients=[email],
            template_body={"fullname": fullname, "url": f"https://{settings.DOMAIN_NAME}"},
            subtype=MessageType.html
        )
        fm = FastMail(conf)
        await fm.send_message(message, template_name="welcome.html")
        logger.info(f"Welcome email sent successfully to {email}")
        return True
    except Exception as e:
        logger.exception(f"Error sending welcome email to {email}: {e}")
        raise e
