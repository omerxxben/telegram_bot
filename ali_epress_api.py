import json

import pandas as pd
import requests
import hashlib
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from GLOBAL_CONST import *
from products_transform import ProductsTransform


class AliExpressApi:
    def process(self, product_name, number_of_rows):
        number_of_rows = number_of_rows + 1
        max_batch_size = 50
        results = []

        if number_of_rows <= max_batch_size:
            results = self._make_request(product_name, 1, number_of_rows)
            results_pd = ProductsTransform().transform_to_table(results)
            return results_pd

        total_pages = (number_of_rows + max_batch_size - 1) // max_batch_size
        print(total_pages)
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            for page_no in range(1, total_pages + 1):
                if page_no < total_pages:
                    batch_size = max_batch_size
                else:
                    batch_size = number_of_rows - max_batch_size * (total_pages - 1)
                futures.append(executor.submit(self._make_request, product_name, page_no, batch_size))

            for future in as_completed(futures):
                try:
                    data = future.result()
                    data_pd = ProductsTransform().transform_to_table(data)
                    results.append(data_pd)
                except Exception as e:
                    results.append({"error": f"Page {page_no}: {str(e)}"})

        merged_df = pd.concat(results, ignore_index=True)
        return merged_df

    def _make_request(self, product_name, page_no, page_size):
        timestamp = int(time.time() * 1000)
        params = {
            "keywords": product_name,
            "app_key": APP_KEY,
            "timestamp": timestamp,
            "method": "aliexpress.affiliate.hotproduct.query",
            "sign_method": "md5",
            "format": "json",
            "page_no": page_no,
            "page_size": page_size,
            "target_currency": "ILS",
            "target_language": "ENG",
            "platform_product_type": "ALL",
            "ship_to_country": "IL",
            "sort": "LAST_VOLUME_DESC"
        }
        params["sign"] = self.generate_signature(params)

        response = requests.get(URL, params=params)
        response.raise_for_status()
        return response.json()

    def generate_signature(self, params: dict) -> str:
        sorted_params = ''.join(f'{k}{v}' for k, v in sorted(params.items()))
        sign_str = f"{APP_SECRET}{sorted_params}{APP_SECRET}"
        return hashlib.md5(sign_str.encode('utf-8')).hexdigest().upper()
