import uuid
import json
import urllib.request
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from models.db import SessionLocal
from models.redirect import Redirect as RedirectModel, RedirectVisitors as RedirectVisitorModel
from models.user import User, Subscription
from libs.logger import logger
from libs.redis import redis

def parse_user_agent(ua_str: str) -> str:
    if not ua_str or ua_str == "Unknown":
        return "Unknown Device"
    ua_lower = ua_str.lower()
    
    device_type = "Desktop"
    if any(m in ua_lower for m in ["mobile", "android", "iphone", "ipad", "ipod"]):
        device_type = "Mobile"
    elif "tablet" in ua_lower:
        device_type = "Tablet"
        
    browser = "Browser"
    if "edg/" in ua_lower or "edge/" in ua_lower:
        browser = "Edge"
    elif "chrome/" in ua_lower:
        browser = "Chrome"
    elif "firefox/" in ua_lower:
        browser = "Firefox"
    elif "safari/" in ua_lower and "chrome/" not in ua_lower:
        browser = "Safari"
    elif "opera/" in ua_lower or "opr/" in ua_lower:
        browser = "Opera"
        
    os_name = ""
    if "windows" in ua_lower:
        os_name = "Windows"
    elif "mac os" in ua_lower or "macintosh" in ua_lower:
        os_name = "macOS"
    elif "android" in ua_lower:
        os_name = "Android"
    elif "iphone" in ua_lower or "ipad" in ua_lower:
        os_name = "iOS"
    elif "linux" in ua_lower:
        os_name = "Linux"
        
    if os_name:
        return f"{browser} on {os_name} ({device_type})"
    return f"{browser} ({device_type})"

def fetch_ip_location(ip: str) -> str:
    if not ip or ip in ("127.0.0.1", "localhost", "::1") or ip.startswith("192.168.") or ip.startswith("10."):
        return "Local Network (Development)"
    try:
        url = f"http://ip-api.com/json/{ip}?fields=status,country,city"
        req = urllib.request.Request(url, headers={"User-Agent": "OnyxSaaS/1.0"})
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data.get("status") == "success":
                city = data.get("city", "")
                country = data.get("country", "")
                if city and country:
                    return f"{city}, {country}"
                return country or city or "Unknown Location"
    except Exception as err:
        logger.debug(f"Failed to fetch IP geolocation for {ip}: {err}")
    return "Unknown Location"

async def log_redirect_visitor_task(ctx: dict, redirect_id_str: str, client_ip: str, user_agent_str: str):
    async with SessionLocal() as db:
        try:
            redirect_uuid = uuid.UUID(redirect_id_str)
            location_str = fetch_ip_location(client_ip)
            device_str = parse_user_agent(user_agent_str)

            visitor = RedirectVisitorModel(
                redirect_id=redirect_uuid,
                ip=client_ip,
                location=location_str,
                device=device_str,
            )
            db.add(visitor)
            await db.commit()
            logger.info(f"Worker logged visitor ({device_str}, {location_str}) for redirect '{redirect_id_str}'")

            # Check visit limit enforcement
            stmt = (
                select(RedirectModel)
                .options(selectinload(RedirectModel.user).selectinload(User.current_subscription).selectinload(Subscription.tier))
                .where(RedirectModel.redirect_id == redirect_uuid)
            )
            redirect_obj = await db.scalar(stmt)
            if redirect_obj and redirect_obj.user:
                from routers.v1.client.utils import get_user_permissions_and_limits
                _, limits = get_user_permissions_and_limits(redirect_obj.user)
                max_visits = limits.get("max_visits_per_shortlink")

                total_visits = await db.scalar(
                    select(func.count(RedirectVisitorModel.id)).where(RedirectVisitorModel.redirect_id == redirect_uuid)
                ) or 0

                if max_visits and total_visits >= max_visits:
                    redirect_obj.expired = True
                    await db.commit()
                    redis_key = f"onyx:redirect:{redirect_obj.domain}:{redirect_obj.slug}"
                    await redis.delete(redis_key)
                    logger.info(f"Redirect {redirect_id_str} reached visit limit ({total_visits}/{max_visits}) and was expired.")

        except Exception as e:
            await db.rollback()
            logger.exception(f"Error logging visitor in background worker for redirect '{redirect_id_str}': {e}")
