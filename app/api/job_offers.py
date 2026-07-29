import datetime
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.enums import ExperienceLevel, ContractType, WorkMode, OfferStatus
from app.repositories import job_offer_repository
from app.schemas.job_offer import JobOfferResponse

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