import httpx
import logging
from config import settings
from datetime import datetime
from utils.encryption import EncryptionService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FlutterwaveService:
    BASE_URL = "https://api.flutterwave.com/v3"
    
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {settings.FLUTTERWAVE_SECRET_KEY}",
            "Content-Type": "application/json",
            "accept": "application/json"
        }
    
    async def charge_card(self, payment_data: dict) -> dict:
        endpoint = f"{self.BASE_URL}/charges?type=card"
        
        try:
            # Validate required fields
            required_fields = ["card_number", "cvv", "expiry_month", "expiry_year", "amount", "currency", "email", "fullname", "authorization"]
            for field in required_fields:
                if field not in payment_data:
                    logger.error(f"Missing required field: {field}")
                    return {"status": "error", "message": f"Missing required field: {field}"}
            
            # Validate authorization structure
            authorization_data = payment_data.get("authorization", {})
            if not isinstance(authorization_data, dict) or "pin" not in authorization_data:
                logger.error("Missing required field: authorization.pin")
                return {"status": "error", "message": "Missing required field: authorization.pin"}
            
            payload = {
                "card_number": payment_data["card_number"],
                "cvv": payment_data["cvv"],
                "expiry_month": payment_data["expiry_month"],
                "expiry_year": payment_data["expiry_year"],
                "amount": payment_data["amount"],
                "currency": payment_data["currency"],
                "email": payment_data["email"],
                "fullname": payment_data["fullname"],
                "tx_ref": f"tx-{datetime.utcnow().timestamp()}",
                "authorization": {
                    "mode": "pin",
                    "pin": authorization_data["pin"]
                },
                "eci": "03",
                "a_authenticationtoken": "zPkn+YYYYYY53434HFHDss=",
                "a_amount": "100",
                "a_version": "2.1.0",
                "a_transactionid": "1F3Uciah9cnh4mrnPPtyT_RA_test",
                "a_transactionstatus": "Y",
                "a_statusreasoncode": "33",
                "is_custom_3ds_enabled": True,
                "redirect_url": "https://your-redirect-url.com/callback"
            }
            
            # Encrypt payload
            encrypted_payload = {"client":  EncryptionService.encrypt_data(payload)}
            
            async with httpx.AsyncClient() as client:
                response = await client.post(endpoint, json=encrypted_payload, headers=self.headers)
                response_data = response.json()
                
                if response.status_code != 200:
                    logger.error(f"Error from Flutterwave API: {response_data}")
                    return {"status": "error", "message": "Payment processing failed", "details": response_data}
                
                return response_data
            
        except Exception as e:
            logger.exception("Exception occurred while charging card")
            return {"status": "error", "message": str(e)}
    
    async def verify_payment(self, transaction_id: str) -> dict:
        endpoint = f"{self.BASE_URL}/transactions/{transaction_id}/verify"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(endpoint, headers=self.headers)
                response_data = response.json()
                
                if response.status_code != 200:
                    logger.error(f"Error verifying payment: {response_data}")
                    return {"status": "error", "message": "Payment verification failed", "details": response_data}
                
                return response_data
            
        except Exception as e:
            logger.exception("Exception occurred while verifying payment")
            return {"status": "error", "message": str(e)}
