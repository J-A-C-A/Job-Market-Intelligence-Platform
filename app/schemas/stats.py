from pydantic import BaseModel
from app.enums import ContractType, ExperienceLevel, WorkMode


class CountFunction(BaseModel):
    group_name: str | ExperienceLevel | WorkMode | ContractType | None
    number_of_offers: int

class AverageFunction(BaseModel):
    avg_salary: float
    contract_type: ContractType
    group_name: str | ExperienceLevel | WorkMode | None
    number_of_offers: int