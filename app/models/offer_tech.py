from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import Mapped
from app.database import Base

class OfferTech(Base):
    __tablename__ = "offer_tech"
    offer_id: Mapped[int] = mapped_column(ForeignKey("job_offers.offer_id"), primary_key=True)
    tech_id: Mapped[int] = mapped_column(ForeignKey("technologies.tech_id"), primary_key=True)
