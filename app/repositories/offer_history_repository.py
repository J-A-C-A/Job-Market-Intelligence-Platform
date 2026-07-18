import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models import OfferHistory


def get_by_offer_id(db: Session, offer_id: int):
    query = select(OfferHistory).where(OfferHistory.offer_id == offer_id)
    result = db.execute(query).scalars().all()
    return result

def create(db: Session,
           offer_id: int,
           field_changed: str,
           change_at: datetime.date,
           old_value: str | None= None,
           new_value: str | None= None):

    new_change= OfferHistory(offer_id=offer_id,field_changed=field_changed,old_value=old_value,new_value=new_value,change_at=change_at)
    db.add(new_change)
    db.commit()
    db.refresh(new_change)
    return new_change