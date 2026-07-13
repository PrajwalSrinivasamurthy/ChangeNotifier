#!/usr/bin/env python3
"""
Checks that the ChangeNotifier app is reachable and texts on state changes
(down, and recovery) via Twilio. Meant to be run from cron every 30 minutes.

Required env vars (read from the process environment / a sourced .env):
  TWILIO_ACCOUNT_SID (or TWILIO_SID)
  TWILIO_AUTH_TOKEN  (or TWILIO_TOKEN)
  TWILIO_FROM_NUMBER (or TWILIO_FROM)
  TWILIO_TO_NUMBERS  comma-separated, e.g. "+18062244674,+18064746037"
                      (or individual TWILIO_TO_1, TWILIO_TO_2, ...)

Optional env vars:
  HEALTHCHECK_URL   default: https://tosmonline0002.ttu.edu/changenotifier/
  HEALTHCHECK_TIMEOUT_SECONDS  default: 10
  UPTIME_STATE_FILE default: alongside this script, uptime_sms_alert.state.json
"""
import json
import os
import sys
from datetime import datetime, timezone

import requests

HEALTHCHECK_URL = os.environ.get("HEALTHCHECK_URL", "https://tosmonline0002.ttu.edu/changenotifier/")
TIMEOUT_SECONDS = float(os.environ.get("HEALTHCHECK_TIMEOUT_SECONDS", "10"))
STATE_FILE = os.environ.get(
    "UPTIME_STATE_FILE",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "uptime_sms_alert.state.json"),
)


def _get_to_numbers():
    combined = os.environ.get("TWILIO_TO_NUMBERS")
    if combined:
        return [n.strip() for n in combined.split(",") if n.strip()]

    numbers = []
    i = 1
    while True:
        n = os.environ.get(f"TWILIO_TO_{i}")
        if not n:
            break
        numbers.append(n)
        i += 1
    return numbers


def check_up():
    try:
        resp = requests.get(HEALTHCHECK_URL, timeout=TIMEOUT_SECONDS)
        return resp.ok, f"HTTP {resp.status_code}"
    except requests.RequestException as e:
        return False, str(e)


def send_sms(sid, token, from_number, to_numbers, body):
    url = f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json"
    for to_number in to_numbers:
        resp = requests.post(
            url,
            auth=(sid, token),
            data={"From": from_number, "To": to_number, "Body": body},
            timeout=TIMEOUT_SECONDS,
        )
        if resp.status_code >= 300:
            print(f"[uptime_sms_alert] Failed to text {to_number}: {resp.status_code} {resp.text}", file=sys.stderr)


def load_last_state():
    try:
        with open(STATE_FILE) as f:
            return json.load(f).get("status", "up")
    except (FileNotFoundError, json.JSONDecodeError):
        return "up"


def save_state(status):
    with open(STATE_FILE, "w") as f:
        json.dump({"status": status, "checked_at": datetime.now(timezone.utc).isoformat()}, f)


def main():
    sid = os.environ.get("TWILIO_ACCOUNT_SID") or os.environ.get("TWILIO_SID")
    token = os.environ.get("TWILIO_AUTH_TOKEN") or os.environ.get("TWILIO_TOKEN")
    from_number = os.environ.get("TWILIO_FROM_NUMBER") or os.environ.get("TWILIO_FROM")
    to_numbers = _get_to_numbers()

    missing = [name for name, val in [
        ("TWILIO_ACCOUNT_SID", sid), ("TWILIO_AUTH_TOKEN", token), ("TWILIO_FROM_NUMBER", from_number),
    ] if not val] + (["TWILIO_TO_NUMBERS"] if not to_numbers else [])
    if missing:
        print(f"[uptime_sms_alert] Missing required env vars: {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)

    is_up, detail = check_up()
    last_status = load_last_state()
    now_status = "up" if is_up else "down"

    print(f"[uptime_sms_alert] {HEALTHCHECK_URL} -> {detail} (status={now_status}, last={last_status})")

    if now_status != last_status:
        if now_status == "down":
            body = f"ChangeNotifier is DOWN: {HEALTHCHECK_URL} ({detail})"
        else:
            body = f"ChangeNotifier is back UP: {HEALTHCHECK_URL}"
        send_sms(sid, token, from_number, to_numbers, body)

    save_state(now_status)


if __name__ == "__main__":
    main()
