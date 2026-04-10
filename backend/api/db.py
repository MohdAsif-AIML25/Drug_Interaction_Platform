from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base
import os
from dotenv import load_dotenv

from urllib.parse import quote_plus

# Load .env if not already loaded (useful for local runs)
load_dotenv(override=True)

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # Try to construct from individual parts securely
    user = os.getenv("MYSQL_USER", "root")
    password = os.getenv("MYSQL_PASSWORD", "your_mysql_password_here")
    host = os.getenv("MYSQL_HOST", "localhost")
    port = os.getenv("MYSQL_PORT", "3306")
    db_name = os.getenv("MYSQL_DB", "drug_interaction")
    
    encoded_password = quote_plus(password)
    DATABASE_URL = f"mysql+pymysql://{user}:{encoded_password}@{host}:{port}/{db_name}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def save_event(drug_a: str, drug_b: str, events: list):
    """
    Save the raw search results to MySQL for future audit trail.
    """
    from .models import DrugEvent
    import json
    db = SessionLocal()
    try:
        new_event = DrugEvent(
            drug_a=drug_a,
            drug_b=drug_b,
            source="OpenFDA",
            raw_text=events
        )
        db.add(new_event)
        db.commit()
    except Exception as e:
        print(f"Error saving event: {e}")
        db.rollback()
    finally:
        db.close()