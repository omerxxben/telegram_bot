import requests
import hashlib
from GLOBAL_CONST import *
import time
import pandas as pd
from typing import Dict, Any


class AliExpressApiProducts:
    def process(self, products_df: pd.DataFrame) -> pd.DataFrame:
        products_df = products_df.copy()
        products_df['avg_evaluation_rating'] = None
        products_df['sales_count'] = None
        products_df['evaluation_count'] = None

        # Process each product
        for index, row in products_df.iterrows():
            product_id = str(row['product_id'])
            print(f"Processing product {index + 1}/{len(products_df)}: {product_id}")

            # Get product details from API
            product_data = self.get_product_details(product_id)

            # Extract the required fields
            if product_data and 'error' not in product_data:
                try:
                    base_info = product_data.get('aliexpress_ds_product_get_response', {}).get('result', {}).get(
                        'ae_item_base_info_dto', {})

                    # Extract the fields
                    avg_rating = base_info.get('avg_evaluation_rating')
                    sales_count = base_info.get('sales_count')
                    eval_count = base_info.get('evaluation_count')

                    # Convert to appropriate types
                    products_df.at[index, 'avg_evaluation_rating'] = float(avg_rating) if avg_rating else None
                    products_df.at[index, 'sales_count'] = int(sales_count) if sales_count else None
                    products_df.at[index, 'evaluation_count'] = int(eval_count) if eval_count else None

                    print(f"  ✓ Rating: {avg_rating}, Sales: {sales_count}, Reviews: {eval_count}")

                except (KeyError, ValueError, TypeError) as e:
                    print(f"  ✗ Error extracting data for product {product_id}: {e}")
            else:
                error_msg = product_data.get('error', 'Unknown error') if product_data else 'No response'
                print(f"  ✗ API error for product {product_id}: {error_msg}")

            # Add a small delay to avoid rate limiting
            time.sleep(0.1)

        return products_df

    def get_product_details(self, product_id: str) -> Dict[str, Any]:
        timestamp = int(time.time() * 1000)
        params = {
            "product_id": product_id,
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
        except requests.exceptions.RequestException as e:
            return {"error": f"Request failed: {str(e)}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}

    def generate_signature(self, params: dict) -> str:
        sorted_params = ''.join(f'{k}{v}' for k, v in sorted(params.items()))
        sign_str = f"{DS_APP_SECRET}{sorted_params}{DS_APP_SECRET}"
        return hashlib.md5(sign_str.encode('utf-8')).hexdigest().upper()
