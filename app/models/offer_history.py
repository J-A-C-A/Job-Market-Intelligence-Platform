import datetime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import Mapped
from app.database import Base

class OfferHistory(Base):
    __tablename__ = "offer_history"
    change_id: Mapped[int] = mapped_column(primary_key=True,autoincrement=True)
    offer_id: Mapped[int] = mapped_column(ForeignKey("job_offers.offer_id"),nullable=False)
    field_changed: Mapped[str] = mapped_column(nullable=False)
    old_value: Mapped[str] = mapped_column(nullable=True)
    new_value: Mapped[str] = mapped_column(nullable=True)
    change_at: Mapped[datetime.date] = mapped_column(nullable=False)