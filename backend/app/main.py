import os
import logging
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from apscheduler.schedulers.background import BackgroundScheduler

from .database import Base, engine, get_db
from .models import Website, Settings, NotificationLog
from .schemas import WebsiteCreate, WebsiteOut, SettingsUpdate, SettingsOut, NotificationLogOut
from .checker import check_all_websites, check_website

load_dotenv()
logging.basicConfig(level=logging.INFO)

SEED_WEBSITES = [
    {"name": "TTU K-12", "url": "https://www.depts.ttu.edu/k12/"},
    {"name": "TTU Online", "url": "https://www.depts.ttu.edu/online/"},
    {"name": "TTU K-12 Testing", "url": "https://www.depts.ttu.edu/k12/testing/"},
]

scheduler = BackgroundScheduler()


def seed_db():
    from .database import SessionLocal

    db = SessionLocal()
    try:
        if db.query(Settings).first() is None:
            db.add(Settings(recipient_phone_number=None))
        for site in SEED_WEBSITES:
            if not db.query(Website).filter(Website.url == site["url"]).first():
                db.add(Website(name=site["name"], url=site["url"]))
        db.commit()
    finally:
        db.close()


def scheduled_job():
    from .database import SessionLocal

    db = SessionLocal()
    try:
        check_all_websites(db)
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    seed_db()
    interval_minutes = int(os.getenv("CHECK_INTERVAL_MINUTES", "15"))
    scheduler.add_job(scheduled_job, "interval", minutes=interval_minutes, id="check_all")
    scheduler.start()
    yield
    scheduler.shutdown()


app = FastAPI(title="Webpage Change Notifier", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/api/websites", response_model=list[WebsiteOut])
def list_websites(db: Session = Depends(get_db)):
    return db.query(Website).order_by(Website.created_at).all()


@app.post("/api/websites", response_model=WebsiteOut)
def create_website(payload: WebsiteCreate, db: Session = Depends(get_db)):
    if db.query(Website).filter(Website.url == payload.url).first():
        raise HTTPException(status_code=400, detail="This URL is already being monitored")
    name = payload.name or payload.url
    website = Website(name=name, url=payload.url)
    db.add(website)
    db.commit()
    db.refresh(website)
    try:
        check_website(db, website)
    except Exception:
        logging.exception("Initial check failed for %s", website.url)
    return website


@app.delete("/api/websites/{website_id}")
def delete_website(website_id: int, db: Session = Depends(get_db)):
    website = db.query(Website).get(website_id)
    if not website:
        raise HTTPException(status_code=404, detail="Website not found")
    db.delete(website)
    db.commit()
    return {"ok": True}


@app.post("/api/websites/{website_id}/check", response_model=WebsiteOut)
def trigger_check(website_id: int, db: Session = Depends(get_db)):
    website = db.query(Website).get(website_id)
    if not website:
        raise HTTPException(status_code=404, detail="Website not found")
    check_website(db, website)
    db.refresh(website)
    return website


@app.get("/api/settings", response_model=SettingsOut)
def get_settings(db: Session = Depends(get_db)):
    settings = db.query(Settings).first()
    if not settings:
        settings = Settings(recipient_phone_number=None)
        db.add(settings)
        db.commit()
    return settings


@app.post("/api/settings", response_model=SettingsOut)
def update_settings(payload: SettingsUpdate, db: Session = Depends(get_db)):
    settings = db.query(Settings).first()
    if not settings:
        settings = Settings()
        db.add(settings)
    settings.recipient_phone_number = payload.recipient_phone_number
    db.commit()
    db.refresh(settings)
    return settings


@app.get("/api/logs", response_model=list[NotificationLogOut])
def list_logs(db: Session = Depends(get_db)):
    return db.query(NotificationLog).order_by(NotificationLog.created_at.desc()).limit(50).all()
