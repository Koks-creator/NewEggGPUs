from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from AleMoc.config import Config

engine = create_engine(
    Config.SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def create_database():
    return Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


