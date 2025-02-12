# app/main.py
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
import models
import schemas
from services.payments import FlutterwaveService
from database import SessionLocal, engine
from typing import Optional

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/payments/initiate", response_model=schemas.PaymentResponse)
async def initiate_payment(
    payment: schemas.PaymentCreate,
    db: Session = Depends(get_db)
):
    flutterwave = FlutterwaveService()
    
    # Initiate payment with Flutterwave
    payment_response = await flutterwave.initiate_payment(payment.dict())
    
    if payment_response.get("status") != "success":
        raise HTTPException(status_code=400, detail="Payment initiation failed")
    
    
    db_payment = models.Payment(
        transaction_id=payment_response["data"]["tx_ref"],
        amount=payment.amount,
        currency=payment.currency,
        status="pending",
        customer_email=payment.customer_email,
        customer_name=payment.customer_name,
        payment_link=payment_response["data"]["link"]
    )
    
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    
    return schemas.PaymentResponse(
        transaction_id=db_payment.transaction_id,
        payment_link=db_payment.payment_link,
        status=db_payment.status
    )

@app.get("/payments/verify", response_model=schemas.PaymentVerification)
async def verify_payment(
    transaction_id: str,
    db: Session = Depends(get_db)
):
    flutterwave = FlutterwaveService()
    
    
    verification_response = await flutterwave.verify_payment(transaction_id)
    
    if verification_response.get("status") != "success":
        raise HTTPException(status_code=400, detail="Payment verification failed")
    
    
    payment = db.query(models.Payment).filter(
        models.Payment.transaction_id == transaction_id
    ).first()
    
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    payment.status = verification_response["data"]["status"]
    db.commit()
    db.refresh(payment)
    
    return schemas.PaymentVerification(
        status=payment.status,
        amount=payment.amount,
        currency=payment.currency,
        customer_email=payment.customer_email,
        customer_name=payment.customer_name,
        transaction_id=payment.transaction_id,
        created_at=payment.created_at
    )