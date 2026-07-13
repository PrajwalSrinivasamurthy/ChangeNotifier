"""Standalone process that polls the backend's /health endpoint and texts
when it stops responding. Runs as its own container/process so it can still
alert after the backend itself has crashed.

Downtime alerts always go to TWILIO_TO_NUMBER (comma-separated for multiple
recipients), independent of the dashboard-configured recipient used for
content-change alerts.
"""
import os
import time
import logging

import requests
from dotenv import load_dotenv

from .sms import send_sms

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

HEALTH_URL = os.getenv("WATCHDOG_URL", "http://localhost:8000/health")
CHECK_INTERVAL_SECONDS = int(os.getenv("WATCHDOG_INTERVAL_SECONDS", "30"))
REQUEST_TIMEOUT_SECONDS = int(os.getenv("WATCHDOG_TIMEOUT_SECONDS", "10"))
FAILURE_THRESHOLD = int(os.getenv("WATCHDOG_FAILURE_THRESHOLD", "3"))
ALERT_NUMBERS = [n.strip() for n in os.getenv("TWILIO_TO_NUMBER", "").split(",") if n.strip()]


def is_backend_up() -> bool:
    try:
        resp = requests.get(HEALTH_URL, timeout=REQUEST_TIMEOUT_SECONDS)
        return resp.ok
    except requests.RequestException:
        return False


def alert_all(body: str) -> None:
    for number in ALERT_NUMBERS:
        send_sms(number, body)


def run() -> None:
    consecutive_failures = 0
    is_down = False
    logger.info("Watchdog started, polling %s every %ss", HEALTH_URL, CHECK_INTERVAL_SECONDS)

    while True:
        if is_backend_up():
            if is_down:
                logger.info("Backend recovered")
                alert_all("Webpage Change Notifier backend is back UP.")
                is_down = False
            consecutive_failures = 0
        else:
            consecutive_failures += 1
            logger.warning("Health check failed (%d/%d)", consecutive_failures, FAILURE_THRESHOLD)
            if consecutive_failures >= FAILURE_THRESHOLD and not is_down:
                logger.error("Backend appears DOWN, sending alert")
                alert_all(f"Webpage Change Notifier backend is DOWN (unreachable at {HEALTH_URL}).")
                is_down = True

        time.sleep(CHECK_INTERVAL_SECONDS)


if __name__ == "__main__":
    run()
