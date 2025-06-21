import requests
import hashlib
from GLOBAL_CONST import *
import time

class AliExpressApiProducts:
    def process(self, products):
        timestamp = int(time.time() * 1000)
        params = {
            "product_id": "1005006007667081",
            "access_token": "50000101724jWlioatvl7jgTAsRUdGdxl2lr1bf75b94VEgYHwxEJovwoNxjsqzz4udp",
            "app_key": DS_APP_KEY,
            "timestamp": timestamp,
            "method": "aliexpress.ds.product.get",
            "sign_method": "md5",
            "format": "json",
            "v": "2.0",
            "target_currency": "ILS",
            "target_language": "he",
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
        sign_str = f"{DS_APP_SECRET}{sorted_params}{DS_APP_SECRET}"
        return hashlib.md5(sign_str.encode('utf-8')).hexdigest().upper()

