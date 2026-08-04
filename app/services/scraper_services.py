from app.scrapers.nofluffjobs_scraper import run_scraper
from sqlalchemy.orm import Session
from app.services.job_offer_service import process_scraped_offer

def scrape_and_save_offers(db:Session) -> None:
    offers = run_scraper()
    for offer in offers:
        try:
           process_scraped_offer(db,offer)
        except Exception as e:
            print(f"Unexpected error: {e}")

