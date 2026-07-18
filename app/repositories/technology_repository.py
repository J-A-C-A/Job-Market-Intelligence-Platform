from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models import Technology


def get_by_name(db: Session, name: str):
    query = select(Technology).where(Technology.name == name)
    result = db.execute(query).scalar_one_or_none()
    return result

def create_technology(db: Session, name: str):
    new_tech = Technology(name=name)
    db.add(new_tech)
    db.commit()
    db.refresh(new_tech)
    return new_tech
