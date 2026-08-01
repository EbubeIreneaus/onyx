import uuid
import logging

from models.db import SessionLocal
from models.redirect import RedirectVisitors as RedirectVisitorModel
from libs.logger import logger

async def log_redirect_visitor_task(ctx: dict, redirect_id_str: str, client_ip: str, user_agent_str: str):
    async with SessionLocal() as db:
        try:
            redirect_uuid = uuid.UUID(redirect_id_str)
            visitor = RedirectVisitorModel(
                redirect_id=redirect_uuid,
                ip=client_ip,
                device=user_agent_str,
            )
            db.add(visitor)
            await db.commit()
            logger.info(f"Worker logged visitor from IP '{client_ip}' for redirect '{redirect_id_str}'")
        except Exception as e:
            await db.rollback()
            logger.exception(f"Error logging visitor in background worker for redirect '{redirect_id_str}': {e}")
