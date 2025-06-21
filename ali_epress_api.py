import json
import requests
import hashlib
import time

from GLOBAL_CONST import *


class AliExpressApi:
    def process(self, product_name, number_of_rows):
        timestamp = int(time.time() * 1000)
        params = {
            "keywords": product_name,
            "app_key": APP_KEY,
            "timestamp": timestamp,
            "method": "aliexpress.affiliate.product.query",
            "sign_method": "md5",
            "format": "json",
            "v": "2.0",
            "page_no": "1",
            "page_size": number_of_rows,
            "target_currency": "ILS",
            "target_language": "EN",
            "sort": "SALE_PRICE_ASC",
            "platform_product_type": "ALL",
            "ship_to_country": "IL",
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


