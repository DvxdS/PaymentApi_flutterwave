# app/schemas.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict
from datetime import datetime

class CardAuthorization(BaseModel):
    mode: str = "pin"
    pin: int
    city: Optional[str] = None
    address: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    zipcode: Optional[int] = None

class PaymentCreate(BaseModel):
    amount: float = Field(..., gt=0)
    currency: str = "NGN"
    card_number: str
    cvv: str
    expiry_month: int = Field(..., ge=1, le=12)
    expiry_year: int
    email: EmailStr
    fullname: str
    phone_number: Optional[str] = None
    authorization: CardAuthorization
    redirect_url: Optional[str] = None
    tx_ref: Optional[str] = None  
    is_custom_3ds_enabled: bool = True
    a_statusreasoncode: str = "33"

class PaymentResponse(BaseModel):
    status: str
    message: str
    data: Dict
    meta: Optional[Dict] = None


class PaymentVerification(BaseModel):
    status: str
    amount: float
    currency: str
    customer_email: str
    customer_name: str
    transaction_id: str
    created_at: datetime