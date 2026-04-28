from __future__ import annotations

import logging

from app.config import load_settings
from app.runner import run_once

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)


if __name__ == "__main__":
    settings = load_settings()
    run_once(settings)
