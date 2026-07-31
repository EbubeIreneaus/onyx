from redis.asyncio import Redis
from setting import settings

redis = Redis.from_url(settings.DB_URL)