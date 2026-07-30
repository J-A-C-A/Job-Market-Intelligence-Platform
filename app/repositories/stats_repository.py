from sqlalchemy import select,func
from sqlalchemy.orm import Session
from app.enums import ExperienceLevel, ContractType, WorkMode
from app.models import JobOffer, Technology

def count_offers_by_experience(db: Session) -> list[tuple[ExperienceLevel,int]]:
    query = (select(JobOffer.experience, func.count(JobOffer.offer_id)).group_by(JobOffer.experience))
    result = db.execute(query).all()
    return result

def count_offers_by_technology(db: Session) -> list[tuple[str,int]]:
    query = (select(Technology.name, func.count(JobOffer.offer_id)).join(JobOffer.technologies).group_by(Technology.name))
    result = db.execute(query).all()
    return result

def count_offers_by_location(db: Session) -> list[tuple[str,int]]:
    query = (select(JobOffer.location, func.count(JobOffer.offer_id)).group_by(JobOffer.location))
    result = db.execute(query).all()
    return result

def count_offers_by_contract(db: Session) -> list[tuple[ContractType,int]]:
    query = (select(JobOffer.type_of_contract, func.count(JobOffer.offer_id)).group_by(JobOffer.type_of_contract))
    result = db.execute(query).all()
    return result

def count_offers_by_work_mode(db: Session) -> list[tuple[WorkMode,int]]:
    query = (select(JobOffer.mode_of_work, func.count(JobOffer.offer_id)).group_by(JobOffer.mode_of_work))
    result = db.execute(query).all()
    return result

def avg_salary_by_tech_and_contract(db: Session) -> list[tuple[str, ContractType,float,int]]:
    query = (select(Technology.name,JobOffer.type_of_contract,func.avg( (JobOffer.salary_min + JobOffer.salary_max)/2 ), func.count(JobOffer.offer_id)).join(JobOffer.technologies).group_by(Technology.name, JobOffer.type_of_contract))
    result = db.execute(query).all()
    return result

def avg_salary_by_experience_and_contract(db: Session) -> list[tuple[ExperienceLevel, ContractType,float,int]]:
    query = (select(JobOffer.experience, JobOffer.type_of_contract, func.avg((JobOffer.salary_min + JobOffer.salary_max)/2), func.count(JobOffer.offer_id)).group_by(JobOffer.experience, JobOffer.type_of_contract))
    result = db.execute(query).all()
    return result

def avg_salary_by_mode_of_work_and_contract(db: Session) -> list[tuple[WorkMode, ContractType,float,int]]:
    query = (select(JobOffer.mode_of_work, JobOffer.type_of_contract, func.avg((JobOffer.salary_min + JobOffer.salary_max)/2), func.count(JobOffer.offer_id)).group_by(JobOffer.mode_of_work, JobOffer.type_of_contract))
    result = db.execute(query).all()
    return result

def avg_salary_by_location_and_contract(db: Session) -> list[tuple[str | None, ContractType,float,int]]:
    query = ( select(JobOffer.location,JobOffer.type_of_contract, func.avg((JobOffer.salary_min + JobOffer.salary_max)/2), func.count(JobOffer.offer_id)).group_by(JobOffer.location, JobOffer.type_of_contract))
    result = db.execute(query).all()
    return result