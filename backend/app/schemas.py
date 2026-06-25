from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, field_validator, field_serializer


def _as_utc_iso(v: Optional[datetime]) -> Optional[str]:
    """SQLite drops tzinfo on read, so naive datetimes here are always UTC
    (everything is written with datetime.now(timezone.utc)). Re-attach the
    offset on the way out so clients parse them as UTC instead of assuming
    local time."""
    if v is None:
        return None
    if v.tzinfo is None:
        v = v.replace(tzinfo=timezone.utc)
    return v.isoformat()


class WebsiteCreate(BaseModel):
    url: str
    name: Optional[str] = None

    @field_validator("url")
    @classmethod
    def normalize_url(cls, v: str) -> str:
        v = v.strip()
        if not v.startswith("http://") and not v.startswith("https://"):
            v = "https://" + v
        return v


class WebsiteOut(BaseModel):
    id: int
    name: str
    url: str
    last_modified_text: Optional[str]
    last_checked_at: Optional[datetime]
    last_changed_at: Optional[datetime]

    @field_serializer("last_checked_at", "last_changed_at")
    def serialize_dt(self, v: Optional[datetime]) -> Optional[str]:
        return _as_utc_iso(v)

    class Config:
        from_attributes = True


class SettingsUpdate(BaseModel):
    recipient_phone_number: str


class SettingsOut(BaseModel):
    recipient_phone_number: Optional[str]

    class Config:
        from_attributes = True


class NotificationLogOut(BaseModel):
    id: int
    website_id: int
    message: str
    status: str
    created_at: datetime

    @field_serializer("created_at")
    def serialize_dt(self, v: datetime) -> Optional[str]:
        return _as_utc_iso(v)

    class Config:
        from_attributes = True
