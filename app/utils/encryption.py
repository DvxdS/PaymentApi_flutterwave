import json
import base64
from Crypto.Cipher import DES3
from config import settings

class EncryptionService:
    @staticmethod
    def encrypt_data(payload: dict) -> str:
        
        
        plain_text = json.dumps(payload)
        
        
        key = settings.FLW_ENCRYPTION_KEY
        
        
        block_size = 8
        pad_diff = block_size - (len(plain_text) % block_size)
        padded_text = f"{plain_text}{''.join(chr(pad_diff) * pad_diff)}"
        
        
        cipher = DES3.new(key.encode(), DES3.MODE_ECB)
        encrypted = base64.b64encode(cipher.encrypt(padded_text.encode()))
        
        return encrypted.decode()