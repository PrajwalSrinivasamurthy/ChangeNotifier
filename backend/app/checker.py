import logging
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from .models import Website, Settings, NotificationLog
from .scraper import fetch_last_modified_text
from .sms import send_sms

logger = logging.getLogger(__name__)


def check_website(db: Session, website: Website) -> None:
    now = datetime.now(timezone.utc)
    try:
        current_text = fetch_last_modified_text(website.url)
    except Exception as e:
        logger.error("Failed to check %s: %s", website.url, e)
        website.last_checked_at = now
        db.commit()
        return

    previous_text = website.last_modified_text
    website.last_checked_at = now

    if previous_text is not None and current_text != previous_text:
        website.last_changed_at = now
        settings = db.query(Settings).first()
        to_number = settings.recipient_phone_number if settings else None
        body = f"{website.name} changed!\n{website.url}\nNew last-modified: {current_text}"
        success, status_message = send_sms(to_number, body)
        db.add(
            NotificationLog(
                website_id=website.id,
                message=body,
                status="sent" if success else "skipped" if "skipped" in status_message else "failed",
            )
        )

    website.last_modified_text = current_text
    db.commit()


def check_all_websites(db: Session) -> None:
    for website in db.query(Website).all():
        check_website(db, website)
