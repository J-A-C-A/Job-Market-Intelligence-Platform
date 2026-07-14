from typing import List
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy.orm import Mapped
from app.database import Base

class Technology(Base):
    __tablename__ = "technologies"
    tech_id: Mapped[int] = mapped_column(primary_key=True,autoincrement=True)
    name: Mapped[str] = mapped_column(unique=True,nullable=False)
    offers: Mapped[List["JobOffer"]] = relationship(secondary="offer_tech",back_populates="technologies")