import hashlib
import time
import requests

import pandas as pd
from typing import Dict, List, Any, Optional

from Classes.GLOBAL_CONST import *
from Classes.general_tools import pretty_print_df


class AliExpressApiShortLink:
    def process(self, products_df_detailed: pd.DataFrame) -> (pd.DataFrame, float):
        start_time = time.time()
        unique_source_links = list(dict.fromkeys(products_df_detailed['promotion_link'].dropna().tolist()))
        source_values = ','.join(unique_source_links)
        timestamp = int(time.time() * 1000)
        params = {
            "app_key": APP_KEY,
            "timestamp": str(timestamp),
            "method": "aliexpress.affiliate.link.generate",
            "sign_method": "md5",
            "format": "json",
            "promotion_link_type": "2",  # Should be string based on API docs
            "source_values": source_values,
            "tracking_id": "default",
        }
        params["sign"] = self.generate_signature(params)
        link_map = {}
        max_retries = 3
        retry_count = 0
        while retry_count <= max_retries:
            try:
                response = requests.post(URL, data=params)
                response.raise_for_status()
                data = response.json()

                # Check for API call limit error
                if 'error_response' in data:
                    error_code = data['error_response'].get('code')
                    error_msg = data['error_response'].get('msg', '')

                    if error_code == 'ApiCallLimit' and retry_count < max_retries:
                        print(
                            f"API call limit exceeded. Waiting 5 seconds before retry... (Attempt {retry_count + 1}/{max_retries + 1})")
                        time.sleep(5)
                        retry_count += 1
                        # Update timestamp for retry
                        params["timestamp"] = str(int(time.time() * 1000))
                        params["sign"] = self.generate_signature(params)
                        continue
                    else:
                        print(f"API error: {error_msg}")
                        break

                # Process successful response
                promo_links_data = (
                    data.get("aliexpress_affiliate_link_generate_response", {})
                    .get("resp_result", {})
                    .get("result", {})
                    .get("promotion_links", {})
                    .get("promotion_link", [])
                )

                if promo_links_data and isinstance(promo_links_data, list):
                    link_map = {
                        link.get("source_value"): link.get("promotion_link")
                        for link in promo_links_data
                        if link.get("source_value") and link.get("promotion_link")
                    }
                    print(f"Successfully generated {len(link_map)} affiliate links.")
                else:
                    error_message = data.get("error_response", {}).get("msg", "No promotion links found.")
                    print(error_message)
                    print(f"API call did not return promotion links. Reason: {error_message}")

                break

            except requests.exceptions.RequestException as e:
                print(f"Error fetching short links from API: {e}")
                if retry_count < max_retries:
                    print(f"Retrying in 5 seconds... (Attempt {retry_count + 1}/{max_retries + 1})")
                    time.sleep(5)
                    retry_count += 1
                else:
                    break
            except Exception as e:
                print(f"An unexpected error occurred during API processing: {e}")
                break

        if link_map:
            original_links = products_df_detailed['promotion_link']
            products_df_detailed['promotion_link'] = original_links.map(link_map).fillna(original_links)

        total_time = time.time() - start_time
        return products_df_detailed, total_time

    def generate_signature(self, params: dict) -> str:
        sorted_params = ''.join(f'{k}{v}' for k, v in sorted(params.items()))
        sign_str = f"{APP_SECRET}{sorted_params}{APP_SECRET}"
        return hashlib.md5(sign_str.encode('utf-8')).hexdigest().upper()