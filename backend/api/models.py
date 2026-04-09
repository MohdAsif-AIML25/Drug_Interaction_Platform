from sqlalchemy import Column, Integer, String, JSON, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class DrugEvent(Base):
    __tablename__ = "drug_events"

    id = Column(Integer, primary_key=True, index=True)
    drug_a = Column(String(255), nullable=False)
    drug_b = Column(String(255), nullable=False)
    source = Column(String(100), default="OpenFDA")
    raw_text = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

class InteractionResult(Base):
    __tablename__ = "interaction_results"

    id = Column(Integer, primary_key=True, index=True)
    drug_a = Column(String(255), nullable=False)
    drug_b = Column(String(255), nullable=False)
    severity = Column(String(50))
    confidence = Column(Float)
    explanation = Column(String(1000))
    created_at = Column(DateTime, default=datetime.utcnow)

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    sub_category = Column(String(255))
    product_name = Column(String(255))
    salt_composition = Column(String(255))
    medicine_desc = Column(String(1000))
    side_effects = Column(String(1000))
    drug_interactions = Column(String(1000))

class RagDocument(Base):
    __tablename__ = "rag_documents"

    id = Column(Integer, primary_key=True, index=True)
    drug_a = Column(String(255))
    drug_b = Column(String(255))
    text = Column(String(2000))
    severity = Column(String(50))

