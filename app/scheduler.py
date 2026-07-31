from apscheduler.schedulers.background import BackgroundScheduler
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.services.scraper_services import scrape_and_save_offers
from app.database import SessionLocal

def run_scheduled_scrape():
    db = SessionLocal()
    try:
        scrape_and_save_offers(db)
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = BackgroundScheduler()
    scheduler.add_job(run_scheduled_scrape, 'cron', hour=20, minute=0)
    scheduler.start()
    yield
    scheduler.shutdown()
