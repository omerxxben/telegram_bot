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

        # Try up to 4 times for promotion link issues
        max_promotion_retries = 4
        current_retry = 0

        while current_retry < max_promotion_retries:
            # Determine which credentials to use (alternate between primary and secondary)
            current_cred_index = primary_cred_index if current_retry % 2 == 0 else secondary_cred_index

            result, success = self._make_api_call(product_name, number_of_rows, current_cred_index)

            if success:
                # Check if promotion links are empty
                if self._has_empty_promotion_links(result):
                    current_retry += 1
                    if current_retry < max_promotion_retries:
                        print(
                            f"Empty promotion links detected, retrying... (attempt {current_retry + 1}/{max_promotion_retries})")
                        time.sleep(1)  # Short delay between retries
                        continue
                    else:
                        print("Max retries reached for promotion links, returning result anyway")
                        total_time = time.time() - start_time
                        return result, total_time
                else:
                    # Success with valid promotion links
                    total_time = time.time() - start_time
                    return result, total_time

            # Handle API limit errors
            if self._is_api_limit_error(result):
                print(
                    f"API limit error with {'primary' if current_cred_index == primary_cred_index else 'secondary'} credentials, trying {'secondary' if current_cred_index == primary_cred_index else 'primary'}...")
                other_cred_index = secondary_cred_index if current_cred_index == primary_cred_index else primary_cred_index
                result, success = self._make_api_call(product_name, number_of_rows, other_cred_index)

                if success:
                    # Check promotion links for the successful call
                    if self._has_empty_promotion_links(result):
                        current_retry += 1
                        if current_retry < max_promotion_retries:
                            print(
                                f"Empty promotion links detected after API limit retry, retrying... (attempt {current_retry + 1}/{max_promotion_retries})")
                            time.sleep(1)
                            continue
                        else:
                            print("Max retries reached for promotion links, returning result anyway")
                            total_time = time.time() - start_time
                            return result, total_time
                    else:
                        total_time = time.time() - start_time
                        return result, total_time

                if self._is_api_limit_error(result):
                    print("API limit error with both credentials, waiting 3 seconds...")
                    time.sleep(3)
                    result, success = self._make_api_call(product_name, number_of_rows, primary_cred_index)

                    if success:
                        # Check promotion links
                        if self._has_empty_promotion_links(result):
                            current_retry += 1
                            if current_retry < max_promotion_retries:
                                print(
                                    f"Empty promotion links detected after wait retry, retrying... (attempt {current_retry + 1}/{max_promotion_retries})")
                                time.sleep(1)
                                continue
                            else:
                                print("Max retries reached for promotion links, returning result anyway")
                                total_time = time.time() - start_time
                                return result, total_time
                        else:
                            total_time = time.time() - start_time
                            return result, total_time

                    if self._is_api_limit_error(result):
                        print("Still API limit error, trying secondary credentials one more time...")
                        result, success = self._make_api_call(product_name, number_of_rows, secondary_cred_index)

                        if success:
                            # Check promotion links
                            if self._has_empty_promotion_links(result):
                                current_retry += 1
                                if current_retry < max_promotion_retries:
                                    print(
                                        f"Empty promotion links detected in final API limit retry, retrying... (attempt {current_retry + 1}/{max_promotion_retries})")
                                    time.sleep(1)
                                    continue
                                else:
                                    print("Max retries reached for promotion links, returning result anyway")
                                    total_time = time.time() - start_time
                                    return result, total_time
                            else:
                                total_time = time.time() - start_time
                                return result, total_time

                        if self._is_api_limit_error(result):
                            total_time = time.time() - start_time
                            return "no api available", total_time

            # If we get here, there was an error but not API limit related
            current_retry += 1
            if current_retry < max_promotion_retries:
                print(f"API call failed, retrying... (attempt {current_retry + 1}/{max_promotion_retries})")
                time.sleep(1)

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

    def _has_empty_promotion_links(self, response):
        """Check if any products have empty promotion_link values"""
        try:
            if not isinstance(response, dict):
                return False

            # Navigate through the response structure
            resp_result = response.get('aliexpress_affiliate_product_query_response', {}).get('resp_result', {})
            result = resp_result.get('result', {})
            products = result.get('products', {})
            product_list = products.get('product', [])

            if not product_list:
                return False

            # Check if any product has empty or missing promotion_link
            for product in product_list:
                promotion_link = product.get('promotion_link', '')
                if not promotion_link or promotion_link.strip() == '':
                    return True

            return False
        except Exception as e:
            print(f"Error checking promotion links: {e}")
            return False