import os
import logging

from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

logger = logging.getLogger(__name__)


def is_twilio_configured() -> bool:
    return bool(
        os.getenv("TWILIO_ACCOUNT_SID")
        and os.getenv("TWILIO_AUTH_TOKEN")
        and os.getenv("TWILIO_FROM_NUMBER")
    )


def send_sms(to_number: str, body: str) -> tuple[bool, str]:
    """Send an SMS via Twilio. Returns (success, status_message).

    If Twilio credentials are missing, this logs and returns a "skipped"
    result instead of raising, so the rest of the app keeps working before
    Twilio is set up.
    """
    if not is_twilio_configured():
        msg = "Twilio not configured (missing env vars) - SMS skipped"
        logger.warning(msg)
        return False, msg

    if not to_number:
        msg = "No recipient phone number configured - SMS skipped"
        logger.warning(msg)
        return False, msg

    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    from_number = os.getenv("TWILIO_FROM_NUMBER")

    try:
        client = Client(account_sid, auth_token)
        message = client.messages.create(body=body, from_=from_number, to=to_number)
        return True, f"sent (sid={message.sid})"
    except TwilioRestException as e:
        logger.error("Twilio send failed: %s", e)
        return False, f"Twilio error: {e}"
