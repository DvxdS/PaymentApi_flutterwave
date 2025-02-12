import logging
from fastapi import FastAPI, HTTPException, Depends, Request
from sqlalchemy.orm import Session
import models
import schemas
from services.payments import FlutterwaveService
from database import SessionLocal, engine
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/payments/card", response_model=schemas.PaymentResponse)
async def charge_card(
    request: Request,
    payment: schemas.PaymentCreate,
    db: Session = Depends(get_db)
):
    logger.info("Received charge request: %s", await request.json())
    try:
        flutterwave = FlutterwaveService()
        payment_response = await flutterwave.charge_card(payment.dict())
        
        if payment_response.get("status") != "success":
            logger.error("Payment failed: %s", payment_response)
            raise HTTPException(
                status_code=400, 
                detail=payment_response.get("message", "Card charge failed")
            )
        
        db_payment = models.Payment(
            transaction_id=payment_response["data"]["id"],
            flw_ref=payment_response["data"].get("flw_ref"),
            amount=payment.amount,
            currency=payment.currency,
            status=payment_response["data"]["status"],
            customer_email=payment.email,
            customer_name=payment.fullname,
            card_last4=payment_response["data"].get("card", {}).get("last_4digits")
        )
        db.add(db_payment)
        db.commit()
        db.refresh(db_payment)
        
        return schemas.PaymentResponse(
        status=payment_response.get("status", "unknown"),
        message=payment_response.get("message", "No message provided"),
        data=payment_response.get("data", {}),  # Ensure it's a dictionary
        meta=payment_response.get("meta")  # Optional, can be None
        )
    except Exception as e:
        logger.exception("Unexpected error during charge request")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/payments/verify", response_model=schemas.PaymentVerification)
async def verify_payment(
    transaction_id: int,
    db: Session = Depends(get_db)
):
    logger.info("Verifying payment for transaction_id: %s", transaction_id)
    try:
        flutterwave = FlutterwaveService()
        verification_response = await flutterwave.verify_payment(transaction_id)
        
        if verification_response.get("status") != "success":
            logger.error("Payment verification failed: %s", verification_response)
            raise HTTPException(status_code=400, detail="Payment verification failed")
        
        payment = db.query(models.Payment).filter(
            models.Payment.transaction_id == transaction_id
        ).first()
        
        if not payment:
            logger.warning("Payment not found for transaction_id: %s", transaction_id)
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
    except Exception as e:
        logger.exception("Unexpected error during payment verification")
        raise HTTPException(status_code=500, detail="Internal Server Error")
