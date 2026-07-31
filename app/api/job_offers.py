import datetime
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.enums import ExperienceLevel, ContractType, WorkMode, OfferStatus
from app.repositories import job_offer_repository
from app.schemas.job_offer import JobOfferResponse, ScrapeUrlRequest
from app.scrapers.nofluffjobs_scraper import fetch_page, parse_state_transfer, find_offer_slug, find_posting_data, \
    create_JobOffer_from_scraped_data
from app.services import job_offer_service
from app.services.job_offer_service import process_scraped_offer

router = APIRouter(prefix="/offers", tags=["offers"])

@router.get("/",response_model= list[JobOfferResponse])
def get_offers(
        db: Session = Depends(get_db),
        technology: str | None= None,
        location:str | None= None,
        experience: ExperienceLevel |None= None,
        salary_min: float |None= None,
        salary_max: float | None= None,
        type_of_contract: ContractType | None= None,
        mode_of_work: WorkMode| None= None,
        status: OfferStatus| None= None,
        publish_date: datetime.date | None= None,
        expiration_date: datetime.date | None= None,
        last_seen_at: datetime.date | None= None,
        company_name: str | None= None):
    result = (
    job_offer_repository.search(
        db=db,
        technology=technology,
        location=location,
        experience=experience,
        salary_min=salary_min,
        salary_max=salary_max,
        type_of_contract=type_of_contract,
        mode_of_work=mode_of_work,
        status=status,
        publish_date=publish_date,
        expiration_date=expiration_date,
        last_seen_at=last_seen_at,
        company_name=company_name)
    )
    return result

@router.get("/{offer_id}",response_model= JobOfferResponse)
def get_offer(offer_id:int, db: Session = Depends(get_db)):
    result = job_offer_repository.get_by_id(db=db, offer_id=offer_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Offer not found")
    else:
        return result

@router.post("/",response_model= JobOfferResponse, status_code=201)
def create_offer(request: ScrapeUrlRequest, db: Session = Depends(get_db)):
    html_content = fetch_page(url=request.url_address)
    state = parse_state_transfer(html_content)
    slug = find_offer_slug(url=request.url_address)
    posting_data = find_posting_data(state=state,offer_slug=slug)
    raw_offer = create_JobOffer_from_scraped_data(parse_data=posting_data, url=request.url_address)
    if raw_offer is None:
        raise HTTPException(status_code=422, detail="Unprocessable Entity")
    else:
        offer = process_scraped_offer(db=db, data=raw_offer)
        return offer

@router.delete("/{offer_id}", status_code=204)
def delete_offer(offer_id: int, db: Session = Depends(get_db)):
    is_exists = job_offer_repository.get_by_id(db=db, offer_id=offer_id)
    if is_exists:
        job_offer_service.delete_record_by_id(db=db, offer_id=offer_id)
    else:
        raise HTTPException(status_code=404, detail="Offer not found")