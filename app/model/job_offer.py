import datetime
from typing import List
from app.database import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy.orm import Mapped
from app.enums import ContractType, OfferStatus, WorkMode,ExperienceLevel

class JobOffer(Base):
    __tablename__ = "job_offers"
    offer_id: Mapped[int] = mapped_column(primary_key=True,autoincrement=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.company_id"))
    company: Mapped["Company"] = relationship(back_populates="job_offers")
    type_of_contract: Mapped[ContractType] = mapped_column(nullable=False)
    salary_min: Mapped[float] = mapped_column(nullable=False)
    salary_max: Mapped[float] = mapped_column(nullable=False)
    status: Mapped[OfferStatus] = mapped_column(nullable=False)
    experience: Mapped[ExperienceLevel] = mapped_column(nullable=False)
    location: Mapped[str] = mapped_column(nullable=False)
    mode_of_work: Mapped[WorkMode] = mapped_column(nullable=False)
    publication_date: Mapped[datetime.date] = mapped_column(nullable=True)
    expiration_date: Mapped[datetime.date] = mapped_column(nullable=True)
    last_seen_at: Mapped[datetime.date] = mapped_column(nullable=True)
    technologies: Mapped[List["Technology"]] = relationship(secondary="offer_tech", back_populates="offers")
