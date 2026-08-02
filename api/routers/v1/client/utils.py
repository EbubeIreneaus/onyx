from typing import Tuple, Set, Dict, Any
from schemas.user import UserManage
from permission import AppPermission
from setting import settings
from libs.logger import logger

import math

class UnlimitedLimit:
    def __ge__(self, other): return False
    def __gt__(self, other): return False
    def __le__(self, other): return False
    def __lt__(self, other): return False
    def __rge__(self, other): return False
    def __rgt__(self, other): return False
    def __rle__(self, other): return False
    def __rlt__(self, other): return False
    def __eq__(self, other):
        if isinstance(other, str):
            return other.lower() in ('unlimited', 'forever', 'infinite')
        return False
    def __str__(self): return 'unlimited'
    def __repr__(self): return 'unlimited'
    def __format__(self, format_spec): return 'unlimited'
    def __int__(self): return 999_999_999

UNLIMITED = UnlimitedLimit()

def parse_int_limit(value: Any, default: Any = 0) -> Any:
    if value is None:
        return default
    if isinstance(value, str):
        val_str = value.strip().lower()
        if val_str in ('unlimited', 'forever', 'infinite', '-1', 'inf', 'infinity'):
            return UNLIMITED
    if isinstance(value, (int, float)):
        if value < 0 or math.isinf(value):
            return UNLIMITED
        return int(value)
    try:
        val_int = int(value)
        if val_int < 0:
            return UNLIMITED
        return val_int
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
