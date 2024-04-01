from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fleecekmbackend.core.config import DATABASE_URL
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine(DATABASE_URL)
session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    Base.metadata.create_all(bind=engine)

def create_tables_if_not_exist():
    create_tables()

def delete_tables():
    Base.metadata.drop_all(bind=engine)

