import httpx
from config import settings
from datetime import datetime

class FlutterwaveService:
    BASE_URL = "https://api.flutterwave.com/v3"
    
    

    
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {settings.FLUTTERWAVE_SECRET_KEY}",
            "Content-Type": "application/json"
        }
    
    async def initiate_payment(self, payment_data: dict) -> dict:
        endpoint = f"{self.BASE_URL}/payments"
        
        payload = {
            "tx_ref": f"tx-{payment_data['customer_email']}-{datetime.utcnow().timestamp()}",
            "amount": payment_data["amount"],
            "currency": payment_data["currency"],
            "redirect_url": "https://your-redirect-url.com/callback",
             "customer_email": payment_data["customer_email"], 
            "customer_name": payment_data["customer_name"],
            "encrypted_key":settings.FLW_ENCRYPTION_KEY
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(endpoint, json=payload, headers=self.headers)
            print(response.status_code, response.text)  # Debugging
            print("FLUTTERWAVE_SECRET_KEY:", settings.FLUTTERWAVE_SECRET_KEY)#debug
            return response.json()
    
    async def verify_payment(self, transaction_id: str) -> dict:
        endpoint = f"{self.BASE_URL}/transactions/{transaction_id}/verify"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(endpoint, headers=self.headers)
            return response.json()
