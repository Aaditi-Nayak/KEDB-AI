from sqlalchemy import String,Boolean,DateTime
from sqlalchemy.orm import Mapped,mapped_column
from datetime import datetime

from app.database import Base

class User(Base):

    __tablename__="users"

    id:Mapped[int]=mapped_column(primary_key=True,index=True)

    username:Mapped[str]=mapped_column(
        String(50),
        nullable=False
    )

    email:Mapped[str]=mapped_column(
        String(255),
        nullable=False
    )

    password_hash:Mapped[str]=mapped_column(
        String(255),
        nullable=False
    )

    role:Mapped[str]=mapped_column(
        String(20),
        default="Engineer"
    )

    status:Mapped[bool]=mapped_column(
        Boolean,
        default=True
    )

    last_login:Mapped[datetime|None]=mapped_column(
        DateTime,
        nullable=True
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