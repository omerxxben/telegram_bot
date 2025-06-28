import json
import requests
import hashlib
import time

from Classes.GLOBAL_CONST import *


class AliExpressApi:
    def process(self, product_name, number_of_rows):
        start_time = time.time()
        number_of_rows = number_of_rows + 1
        timestamp = int(time.time() * 1000)
        params = {
            "keywords": product_name,
            "app_key": APP_KEY,
            "timestamp": timestamp,
            "method": get_products_api,
            "sign_method": "md5",
            "format": "json",
            "page_no": 1,
            "page_size": number_of_rows,
            "target_currency": "ILS",
            "target_language": "ENG",
            "platform_product_type": "ALL",
            "ship_to_country": "IL",
            "sort": "LAST_VOLUME_DESC"
        }
        params["sign"] = self.generate_signature(params)

        try:
            response = requests.get(URL, params=params)
            response.raise_for_status()
            total_time = time.time() - start_time
            return response.json(), total_time
        except Exception as e:
            print(f"error from get products {e}")
            total_time = time.time() - start_time
            return [], total_time

    def generate_signature(self, params: dict) -> str:
        sorted_params = ''.join(f'{k}{v}' for k, v in sorted(params.items()))
        sign_str = f"{APP_SECRET}{sorted_params}{APP_SECRET}"
        return hashlib.md5(sign_str.encode('utf-8')).hexdigest().upper()