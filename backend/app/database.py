# this will tell how fastapi will talk to the database

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,declarative_base

from app.config import settings


# engine connects fastapi to the sqllite
engine=create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# creates a db session for each req
SessionLocal=sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# parent class for all database models
Base=declarative_base()