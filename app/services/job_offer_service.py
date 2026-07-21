import datetime
from app.enums import OfferStatus
from app.repositories import job_offer_repository
from app.repositories import offer_history_repository
from app.models import JobOffer, OfferHistory
from sqlalchemy.orm import Session
from app.schemas.job_offer import JobOfferCreate
from app.services.company_service import get_or_create_company
from app.services.technology_service import get_or_create_tech

def create_job_offer_from_scraped_data(db: Session, data: JobOfferCreate) -> JobOffer:
    company = get_or_create_company(db, data.company_name)
    tech = [get_or_create_tech(db,tech_name) for tech_name in data.technologies]
    data_dict = data.model_dump(exclude={"company_name","technologies"})
    data_dict["status"] = OfferStatus.ACTIVE
    data_dict["last_seen_at"] = datetime.date.today()
    offer = job_offer_repository.create(db, data_dict, company=company, technologies=tech)
    return offer

def detect_and_record_change(db: Session, old_offer: JobOffer, new_offer: JobOfferCreate) -> None:
    fields_to_check = ["salary_min", "salary_max", "type_of_contract", "experience", "mode_of_work", "expiration_date", "location"]

    for field in fields_to_check:
        old_value = getattr(old_offer, field)
        new_value = getattr(new_offer, field)
        if old_value != new_value:
            offer_history_repository.create(db=db,offer_id=old_offer.offer_id,field_changed=field, old_value=str(old_value), new_value=str(new_value), change_at=datetime.date.today())

    old_offer.last_seen_at = datetime.date.today()
    db.commit()
    db.refresh(old_offer)

def process_scraped_offer(db: Session, data: JobOfferCreate) -> JobOffer:
    offer = job_offer_repository.get_by_url(db, data.url_address)
    if offer is None:
        offer = create_job_offer_from_scraped_data(db=db, data=data)
        return offer
    else:
        detect_and_record_change(db=db, old_offer=offer, new_offer=data)
        return offer
