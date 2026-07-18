from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models import Company


def get_by_name(db: Session, name: str):
    query = select(Company).where(Company.name == name)
    result = db.execute(query).scalar_one_or_none()
    return result

def create_company(db: Session, name:str):
    new_company = Company(name=name)
    db.add(new_company)
    db.commit()
    db.refresh(new_company)
    return new_company