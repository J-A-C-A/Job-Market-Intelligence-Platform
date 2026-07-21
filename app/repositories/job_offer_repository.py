import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.enums import ExperienceLevel, ContractType, WorkMode, OfferStatus
from app.models import JobOffer, Company, Technology


def get_by_id(db: Session, offer_id: int):
    query = select(JobOffer).where(JobOffer.offer_id == offer_id)
    result = db.execute(query).scalar_one_or_none()
    return result

def get_by_url(db: Session, url: str):
    query = select(JobOffer).where(JobOffer.url_address == url)
    result = db.execute(query).scalar_one_or_none()
    return result

def create(db: Session, offer_data:dict, company:Company, technologies: list[Technology]):
    new_offer = JobOffer(**offer_data,company=company,technologies=technologies)
    db.add(new_offer)
    db.commit()
    db.refresh(new_offer)
    return new_offer

def search(db: Session,
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
    query = select(JobOffer)
    if technology is not None:
        query = query.join(JobOffer.technologies).where(Technology.name == technology)
    if location is not None:
        query = query.where(JobOffer.location == location)
    if experience is not None:
        query = query.where(JobOffer.experience == experience)
    if salary_min is not None:
        query = query.where(JobOffer.salary_min >= salary_min)
    if salary_max is not None:
        query = query.where(JobOffer.salary_max <= salary_max)
    if type_of_contract is not None:
        query = query.where(JobOffer.type_of_contract == type_of_contract)
    if mode_of_work is not None:
        query = query.where(JobOffer.mode_of_work == mode_of_work)
    if status is not None:
        query = query.where(JobOffer.status == status)
    if publish_date is not None:
        query = query.where(JobOffer.publication_date >= publish_date)
    if expiration_date is not None:
        query = query.where(JobOffer.expiration_date <= expiration_date)
    if last_seen_at is not None:
        query = query.where(JobOffer.last_seen_at >= last_seen_at)
    if company_name is not None:
        query = query.join(JobOffer.company).where(Company.name == company_name)

    result = db.execute(query).scalars().all()
    return result

