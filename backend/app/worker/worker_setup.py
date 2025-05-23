# backend/app/worker/worker_setup.py
import redis
from rq import Queue
from app.core.config import settings # Adjust import path as needed

# Ensure your Redis settings are correctly loaded by `settings`
redis_url = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0" # Using DB 0 for RQ by default
conn = redis.from_url(redis_url)

# Define different queues if needed, e.g., 'default', 'high_priority'
# For now, one default queue
default_queue = Queue("lms_default_queue", connection=conn)

# You can add more queues here
# ocr_queue = Queue("ocr_tasks", connection=conn)
