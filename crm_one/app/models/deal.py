import enum
from datetime import datetime, timezone
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, DateTime, Integer, Float, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.account import Account
    from app.models.contact import Contact
    from app.models.task import Task


class DealStage(str, enum.Enum):
    QUALIFICATION = "QUALIFICATION"
    NEEDS_ANALYSIS = "NEEDS_ANALYSIS"
    PROPOSAL = "PROPOSAL"
    NEGOTIATION = "NEGOTIATION"
    CLOSED_WON = "CLOSED_WON"
    CLOSED_LOST = "CLOSED_LOST"


class Deal(Base):
    __tablename__ = "deals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    amount: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    stage: Mapped[DealStage] = mapped_column(Enum(DealStage), default=DealStage.QUALIFICATION, nullable=False)
    probability: Mapped[int] = mapped_column(Integer, default=10, nullable=False)  # 0 to 100%
    expected_close_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    account_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("accounts.id", ondelete="CASCADE"), nullable=True)
    contact_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("contacts.id", ondelete="SET NULL"), nullable=True)
    owner_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    account: Mapped[Optional["Account"]] = relationship("Account", back_populates="deals")
    contact: Mapped[Optional["Contact"]] = relationship("Contact", back_populates="deals")
    owner: Mapped[Optional["User"]] = relationship("User", back_populates="deals")
    tasks: Mapped[List["Task"]] = relationship("Task", back_populates="deal")
