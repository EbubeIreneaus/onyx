from typing import Tuple, Set, Dict, Any
from schemas.user import UserManage
from permission import AppPermission
from setting import settings
from libs.logger import logger

def parse_int_limit(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

from datetime import datetime, timezone

def get_user_permissions_and_limits(user: UserManage) -> Tuple[Set[Any], Dict[str, int]]:
    permissions: Set[Any] = set()
    sub = user.current_subscription
    now = datetime.now(timezone.utc)

    sub_valid = False
    if sub and sub.tier:
        exp_dt = sub.expired_at
        if exp_dt:
            if isinstance(exp_dt, str):
                try:
                    exp_dt = datetime.fromisoformat(exp_dt)
                except Exception:
                    exp_dt = None
            if exp_dt:
                if exp_dt.tzinfo is None:
                    exp_dt = exp_dt.replace(tzinfo=timezone.utc)
                if exp_dt > now:
                    sub_valid = True

    if sub_valid and sub and sub.tier:
        tier = sub.tier
        raw_perms = tier.permissions or []
        for p in raw_perms:
            val = p.value if hasattr(p, "value") else str(p)
            permissions.add(val)
            permissions.add(p)
            try:
                permissions.add(AppPermission(val))
            except Exception as err:
                logger.debug(f"Could not convert permission value '{val}' to AppPermission: {err}")
        
        limits = {
            "max_short_link": parse_int_limit(getattr(tier, "max_short_link", None), settings.MIN_ALLOWED_SHORT_LINKS),
            "max_custom_domains": parse_int_limit(getattr(tier, "max_custom_domains", None), 0),
            "max_onyx_subdomains": parse_int_limit(getattr(tier, "max_onyx_subdomains", None), 0),
            "max_custom_paths": parse_int_limit(getattr(tier, "max_custom_paths", None), 0),
            "max_visits_per_shortlink": parse_int_limit(getattr(tier, "max_visits_per_shortlink", None), 500),
            "link_durability": parse_int_limit(getattr(tier, "link_durability", None), 14),
        }
    else:
        limits = {
            "max_short_link": settings.MIN_ALLOWED_SHORT_LINKS,
            "max_custom_domains": 0,
            "max_onyx_subdomains": 0,
            "max_custom_paths": 0,
            "max_visits_per_shortlink": 500,
            "link_durability": 14,
        }
    return permissions, limits

# Maintain backwards-compatible helper for get_user_permissions_and_limit
def get_user_permissions_and_limit(user: UserManage):
    perms, limits = get_user_permissions_and_limits(user)
    return perms, limits["max_short_link"]
