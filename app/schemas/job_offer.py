import datetime
from pydantic import BaseModel
from app import enums
from app.schemas.technology import TechnologyResponse
from app.schemas.company import CompanyResponse

class JobOfferResponse(BaseModel):
    type_of_contract: enums.ContractType
    status: enums.OfferStatus
    experience: enums.ExperienceLevel
    mode_of_work: enums.WorkMode
    publication_date: datetime.date
    expiration_date: datetime.date
    last_seen_at: datetime.date
    company: CompanyResponse
    technologies: list[TechnologyResponse]
    salary_min: float
    salary_max: float
    location:str
    offer_id: int
    class Config:
        from_attributes = True

class JobOfferCreate(BaseModel):
    company_name: str
    technologies: list[str]
    salary_min: float
    salary_max: float
    location: str
    type_of_contract: enums.ContractType
    experience: enums.ExperienceLevel
    mode_of_work: enums.WorkMode
    publication_date: datetime.date
    expiration_date: datetime.date


