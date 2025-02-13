

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
import sys
import os


current_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, current_dir)

from app.main import app, get_db
from app.models import Payment


client = TestClient(app)


def override_get_db():
    try:
        db = MagicMock()
        yield db
    finally:
        pass

app.dependency_overrides[get_db] = override_get_db


sample_payment_request = {
    "card_number": "5531886652142950",
    "cvv": "564",
    "expiry_month": "09",
    "expiry_year": "32",
    "amount": 100,
    "currency": "USD",
    "email": "test@example.com",
    "fullname": "Test User",
    "authorization": {
        "pin": "3310"
    }
}

sample_flw_success_response = {
    "status": "success",
    "message": "Charge initiated",
    "data": {
        "id": 12345,
        "flw_ref": "FLW-MOCK-123456789",
        "status": "successful",
        "card": {
            "last_4digits": "2950"
        }
    }
}

sample_verification_response = {
    "status": "success",
    "message": "Transaction verified successfully",
    "data": {
        "id": 12345,
        "status": "successful",
        "amount": 100,
        "currency": "USD"
    }
}

@pytest.mark.asyncio
class TestPaymentEndpoints:
    
    @patch('app.services.payments.FlutterwaveService.charge_card')
    async def test_initiate_payment_success(self, mock_charge_card):
        
        mock_charge_card.return_value = sample_flw_success_response
        mock_db = next(override_get_db())
        mock_db.commit = MagicMock()
        mock_db.refresh = MagicMock()
        
        
        response = client.post("/payments/initiate", json=sample_payment_request)
        
        
        assert response.status_code == 200
        assert response.json()["status"] == "success"
        assert response.json()["data"]["id"] == 12345
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

    @patch('app.services.payments.FlutterwaveService.charge_card')
    async def test_initiate_payment_failure(self, mock_charge_card):
        
        mock_charge_card.return_value = {
            "status": "error",
            "message": "Card charge failed"
        }
        
        
        response = client.post("/payments/initiate", json=sample_payment_request)
        
        
        assert response.status_code == 400
        assert response.json()["detail"] == "Card charge failed"

    @patch('app.services.payments.FlutterwaveService.verify_payment')
    async def test_verify_payment_success(self, mock_verify_payment):
        
        mock_verify_payment.return_value = sample_verification_response
        mock_db = next(override_get_db())
        
        
        mock_payment = MagicMock()
        mock_payment.status = "successful"
        mock_payment.amount = 100
        mock_payment.currency = "USD"
        mock_payment.customer_email = "test@example.com"
        mock_payment.customer_name = "Test User"
        mock_payment.transaction_id = 12345
        mock_payment.created_at = datetime.utcnow()
        
        mock_db.query.return_value.filter.return_value.first.return_value = mock_payment
        
        
        response = client.get("/payments/verify?transaction_id=12345")
        
        
        assert response.status_code == 200
        assert response.json()["status"] == "successful"
        assert response.json()["amount"] == 100
        assert response.json()["currency"] == "USD"
        mock_db.commit.assert_called_once()

    @patch('app.services.payments.FlutterwaveService.verify_payment')
    async def test_verify_payment_not_found(self, mock_verify_payment):
       
        mock_verify_payment.return_value = sample_verification_response
        mock_db = next(override_get_db())
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        
        response = client.get("/payments/verify?transaction_id=99999")
        
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Payment not found"

    @patch('app.services.payments.FlutterwaveService.verify_payment')
    async def test_verify_payment_verification_failed(self, mock_verify_payment):
        
        mock_verify_payment.return_value = {
            "status": "error",
            "message": "Verification failed"
        }
        
        
        response = client.get("/payments/verify?transaction_id=12345")
        
        
        assert response.status_code == 400
        assert response.json()["detail"] == "Payment verification failed"