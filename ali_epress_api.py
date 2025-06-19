import json
import requests
import hashlib
import time

class AliExpressApi:
    def __init__(self):
        self.URL = "https://api-sg.aliexpress.com/sync"
        self.APP_KEY = "516014"
        self.APP_SECRET = "b5EEHi2TlMY4hIqU2LkuT0lc3NztGsN5"
        self.TRACKING_ID = "your_tracking_id"

    def process(self, product_name):
        timestamp = int(time.time() * 1000)
        params = {
            "keywords": product_name,
            "app_key": self.APP_KEY,
            "timestamp": timestamp,
            "method": "aliexpress.affiliate.product.query",
            "sign_method": "md5",
            "format": "json",
            "v": "2.0",
            "fields": "commission_rate,sale_price,product_title,product_main_image_url",
            "page_no": "1",
            "page_size": "1",
            "target_currency": "ILS",
            "target_language": "he",
            "sort": "SALE_PRICE_ASC",
            "platform_product_type": "ALL",
            "ship_to_country": "IL",
        }
        params["sign"] = self.generate_signature(params)
        try:
            response = requests.get(self.URL, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    def generate_signature(self, params: dict) -> str:
        sorted_params = ''.join(f'{k}{v}' for k, v in sorted(params.items()))
        sign_str = f"{self.APP_SECRET}{sorted_params}{self.APP_SECRET}"
        return hashlib.md5(sign_str.encode('utf-8')).hexdigest().upper()


