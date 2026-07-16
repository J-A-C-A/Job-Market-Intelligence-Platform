from pydantic import BaseModel

class TechnologyResponse(BaseModel):
    tech_id: int
    name: str
    class Config:
        from_attributes = True