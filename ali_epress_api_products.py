import requests
import hashlib
from GLOBAL_CONST import *
import time

class AliExpressApiProducts:
    def process(self, products):
        timestamp = int(time.time() * 1000)
        params = {
            "app_key": APP_KEY,
            "method": "aliexpress.affiliate.product.sku.detail.get",
            "sign_method": "md5",
            "format": "json",
            "v": "2.0",
            "timestamp": timestamp,
            "ship_to_country": "IL",
            "product_id": 1005007859139314,
            "target_currency": "ILS",
            "target_language": "HE",
        }
        params["sign"] = self.generate_signature(params)
        try:
            response = requests.get(URL, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    def generate_signature(self, params: dict) -> str:
        sorted_params = ''.join(f'{k}{v}' for k, v in sorted(params.items()))
        sign_str = f"{APP_SECRET}{sorted_params}{APP_SECRET}"
        return hashlib.md5(sign_str.encode('utf-8')).hexdigest().upper()


