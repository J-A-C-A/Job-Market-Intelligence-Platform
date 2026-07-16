from pydantic import BaseModel
class CompanyResponse(BaseModel):
    name: str
    company_id: int
    class Config:
        from_attributes = True