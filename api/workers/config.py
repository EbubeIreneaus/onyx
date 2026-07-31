from arq.connections import RedisSettings
from setting import settings
from arq.worker import create_pool

REDIS_SETTING = RedisSettings.from_dsn(settings.REDIS_URL)

async def get_arq_pool():
    pool = await create_pool(REDIS_SETTING)
    return pool

class WorkerSettings:
    functions = []
    redis_settings = REDIS_SETTING
    queue_name = "onyx"