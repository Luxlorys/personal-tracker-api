from redis.asyncio import Redis, from_url


def create_redis(url: str) -> Redis:
    """Create a Redis client. The caller owns its lifecycle."""
    return from_url(url, encoding="utf-8", decode_responses=True)
