import json
import random

import requests
import hashlib
import time

from Classes.GLOBAL_CONST import *


class AliExpressApi:
    def process(self, product_name, number_of_rows):
        start_time = time.time()
        number_of_rows = number_of_rows + 1
        primary_cred_index = random.randint(0, 1)
        secondary_cred_index = 1 - primary_cred_index  # The other set
        result, success = self._make_api_call(product_name, number_of_rows, primary_cred_index)
        if success:
            total_time = time.time() - start_time
            return result, total_time
        if self._is_api_limit_error(result):
            print("API limit error with primary credentials, trying secondary...")
            result, success = self._make_api_call(product_name, number_of_rows, secondary_cred_index)
            if success:
                total_time = time.time() - start_time
                return result, total_time
            if self._is_api_limit_error(result):
                print("API limit error with secondary credentials, waiting 3 seconds...")
                time.sleep(3)
                result, success = self._make_api_call(product_name, number_of_rows, primary_cred_index)
                if success:
                    total_time = time.time() - start_time
                    return result, total_time
                if self._is_api_limit_error(result):
                    print("Still API limit error, trying secondary credentials one more time...")
                    result, success = self._make_api_call(product_name, number_of_rows, secondary_cred_index)
                    if success:
                        total_time = time.time() - start_time
                        return result, total_time
                    if self._is_api_limit_error(result):
                        total_time = time.time() - start_time
                        return "no api available", total_time
        total_time = time.time() - start_time
        return result, total_time

    def _make_api_call(self, product_name, number_of_rows, cred_index):
        try:
            credentials = [
                {"app_key": APP_KEY, "app_secret": APP_SECRET},
                {"app_key": SECOND_APP_KEY, "app_secret": SECOND_APP_SECRET}
            ]
            credentials = credentials[cred_index]
            timestamp = int(time.time() * 1000)
            params = {
                "keywords": product_name,
                "app_key": credentials["app_key"],
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
            params["sign"] = self._generate_signature(params, credentials["app_secret"])
            response = requests.get(URL, params=params)
            response.raise_for_status()
            response_json = response.json()
            if self._is_api_limit_error(response_json):
                return response_json, False
            return response_json, True

        except Exception as e:
            print(f"Error from get products: {e}")
            return [], False

    def _generate_signature(self, params: dict, app_secret: str) -> str:
        sorted_params = ''.join(f'{k}{v}' for k, v in sorted(params.items()))
        sign_str = f"{app_secret}{sorted_params}{app_secret}"
        return hashlib.md5(sign_str.encode('utf-8')).hexdigest().upper()

    def _is_api_limit_error(self, response):
        if isinstance(response, dict) and 'error_response' in response:
            error_response = response['error_response']
            if (error_response.get('type') == 'ISV' and
                    error_response.get('code') == 'ApiCallLimit'):
                return True
        return False