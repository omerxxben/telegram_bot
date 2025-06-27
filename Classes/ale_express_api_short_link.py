import hashlib
import time
import requests

import pandas as pd
from typing import Dict, List, Any, Optional

from Classes.GLOBAL_CONST import *
from Classes.general_tools import pretty_print_df


class AliExpressApiShortLink:
    def process(self, products_df_detailed: pd.DataFrame):
        start_time = time.time()

        short_links = []

        for index, row in products_df_detailed.iterrows():
            source_link = row['promotion_link']
            timestamp = int(time.time() * 1000)

            params = {
                "app_key": APP_KEY,
                "timestamp": timestamp,
                "method": "aliexpress.affiliate.link.generate",
                "sign_method": "md5",
                "format": "json",
                "promotion_link_type": 2,
                "source_values": source_link,
                "tracking_id": "default",
            }
            params["sign"] = self.generate_signature(params)
            try:
                response = requests.get(URL, params=params)
                response.raise_for_status()
                data = response.json()
                promo_links = (
                    data.get("aliexpress_affiliate_link_generate_response", {})
                        .get("resp_result", {})
                        .get("result", {})
                        .get("promotion_links", {})
                        .get("promotion_link", [])
                )
                if promo_links and isinstance(promo_links, list):
                    short_link = promo_links[0].get("promotion_link")
                else:
                    short_link = None
            except Exception as e:
                print(f"Error fetching short link for row {index}: {e}")
                short_link = None
            short_links.append(short_link)
        products_df_detailed['promotion_link'] = short_links
        total_time = time.time() - start_time

        return products_df_detailed, total_time

    def generate_signature(self, params: dict) -> str:
        sorted_params = ''.join(f'{k}{v}' for k, v in sorted(params.items()))
        sign_str = f"{APP_SECRET}{sorted_params}{APP_SECRET}"
        return hashlib.md5(sign_str.encode('utf-8')).hexdigest().upper()
