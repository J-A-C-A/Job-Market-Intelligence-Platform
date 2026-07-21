import datetime
from app.enums import OfferStatus
from app.repositories import job_offer_repository
from app.models import JobOffer
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