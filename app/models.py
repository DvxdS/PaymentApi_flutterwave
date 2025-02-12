from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(Integer, unique=True, index=True)
    flw_ref = Column(String, unique=True, nullable=True)
    amount = Column(Float)
    currency = Column(String)
    status = Column(String)
    payment_type = Column(String, default="card")
    customer_email = Column(String)
    customer_name = Column(String)
    card_last4 = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)