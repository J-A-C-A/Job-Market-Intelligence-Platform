from sqlalchemy.orm import Session
from app.models import Technology
from app.repositories.technology_repository import  get_by_name, create_technology

def get_or_create_tech(db:Session, name:str) -> Technology:
    formatted_name = name.title().strip()
    tech = get_by_name(db,formatted_name)
    if tech is None:
        tech = create_technology(db,formatted_name)
    return tech