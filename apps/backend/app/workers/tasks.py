import dramatiq
from dramatiq.brokers.redis import RedisBroker

from app.core.config import get_settings

redis_broker = RedisBroker(url=get_settings().redis_url)
dramatiq.set_broker(redis_broker)


@dramatiq.actor(max_retries=3)
def enqueue_question_generation(source_id: str) -> None:
    # Phase 2 will retrieve source chunks, generate structured questions, validate, deduplicate, and persist.
    return None
