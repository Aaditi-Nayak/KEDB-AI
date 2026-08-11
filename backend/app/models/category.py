from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column,relationship

from app.database import Base

class Category(Base):
    __tablename__="categories"

    id:Mapped[int]=mapped_column(
        primary_key=True,
        index=True
    )
    name:Mapped[str]=mapped_column(
        String(100),
        unique=True,
        nullable=True
    )
    description:Mapped[str]=mapped_column(
        Text,
        nullable=True
    )

    known_errors=relationship(
        "KnownError",
        back_populates="category"
    )