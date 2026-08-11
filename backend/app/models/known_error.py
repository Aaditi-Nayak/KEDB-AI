from sqlalchemy import String,Text,DateTime,ForeignKey
from sqlalchemy.orm import Mapped, mapped_column,relationship
from datetime import datetime

from app.database import Base

class KnownError(Base):
    __tablename__="known_errors"

    id:Mapped[int]=mapped_column(primary_key=True)

    title:Mapped[str]=mapped_column(
        String(200),
        nullable=False
    )

    application:Mapped[str]=mapped_column(
        String(100),
        nullable=False
    )

    category_id:Mapped[int]=mapped_column(
        ForeignKey("categories.id"),
        nullable=False
    )

    category=relationship("Category",back_populates="known_errors")

    symptoms: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    root_cause: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    workaround: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    resolution: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="Open"
    )

    created_by:Mapped[int]=mapped_column(
        ForeignKey("users.id")
    )

    created_at:Mapped[datetime]=mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at:Mapped[datetime]=mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    embedding:Mapped[str|None]=mapped_column(
        Text,
        nullable=True
    )