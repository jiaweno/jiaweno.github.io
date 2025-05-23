# backend/run_worker.py
import sys
import redis
from rq import Connection, Worker # Queue is not directly used here, but good to know
from app.core.config import settings # Ensure this path is correct for your setup

# Ensure the app directory is in the Python path
# This might be needed if run_worker.py is in the backend root and imports from app.core
# If your project structure or PYTHONPATH handles this, you might not need it.
# Example: sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
# Or better, ensure your execution environment (e.g., Docker container) has PYTHONPATH set up.

listen_queues = ['lms_default_queue'] # Listen to the queue defined in worker_setup.py

redis_url = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0"
conn = redis.from_url(redis_url)

if __name__ == '__main__':
    # It's good practice to set up logging for the worker as well.
    # This could be similar to how it's done in tasks.py or a more centralized setup.
    import logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    logger.info(f"Worker starting, listening on queues: {listen_queues}")
    
    with Connection(conn):
        # Create a worker that listens to the specified queues
        worker = Worker(listen_queues, connection=conn) 
        
        # Start the worker. 
        # worker.work() is blocking. 
        # with_scheduler=True is for RQ-Scheduler, not needed for basic task processing.
        worker.work(with_scheduler=False)
