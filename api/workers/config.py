from arq.connections import RedisSettings
from arq.worker import create_pool
from setting import settings
from .auth import update_session, send_welcome_email

REDIS_SETTING = RedisSettings.from_dsn(settings.REDIS_URL)

async def get_arq_pool():
    pool = await create_pool(REDIS_SETTING)
    return pool

class WorkerSettings:
    functions = [update_session, send_welcome_email]
    redis_settings = REDIS_SETTING
    queue_name = "onyx"