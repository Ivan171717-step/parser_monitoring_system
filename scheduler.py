from __future__ import annotations

import logging

from apscheduler.schedulers.blocking import BlockingScheduler

from app.config import load_settings
from app.runner import run_once

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
settings = load_settings([])


def job() -> None:
    run_once(settings)


if __name__ == "__main__":
    scheduler = BlockingScheduler(timezone=settings.timezone)
    scheduler.add_job(job, "interval", hours=settings.run_every_hours, id="parser_monitoring", max_instances=1)
    logging.info("Scheduler started: every %s hours", settings.run_every_hours)
    scheduler.start()
