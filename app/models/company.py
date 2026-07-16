from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy.orm import Mapped
from app.database import Base


class Company(Base):
    __tablename__ = 'companies'
    company_id: Mapped[int] = mapped_column(primary_key=True,autoincrement=True)
    name: Mapped[str] = mapped_column(unique=True,nullable=False)
    job_offers: Mapped[list["JobOffer"]] = relationship(back_populates="company")