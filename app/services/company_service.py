from sqlalchemy.orm import Session
from app.models import Company
from app.repositories.company_repository import get_by_name, create_company

def get_or_create_company(db: Session, name: str) -> Company:
    formatted_name = name.title().strip()
    company = get_by_name(db, name=formatted_name)
    if company is None:
        company = create_company(db, formatted_name)
    return company