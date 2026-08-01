import sys
import asyncio
import logging
from pathlib import Path
from arq.worker import run_worker

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from workers.config import WorkerSettings

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    run_worker(WorkerSettings)