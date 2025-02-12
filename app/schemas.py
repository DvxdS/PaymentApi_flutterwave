

# app/schemas.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PaymentCreate(BaseModel):
    amount: float
    currency: str = "NGN"
    customer_email: str
    customer_name: str

class PaymentResponse(BaseModel):
    transaction_id: str
    payment_link: str
    status: str

class PaymentVerification(BaseModel):
    status: str
    amount: float
    currency: str
    customer_email: str
    customer_name: str
    transaction_id: str
    created_at: datetime