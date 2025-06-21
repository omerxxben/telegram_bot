import requests
import hashlib
from GLOBAL_CONST import *
import time
import pandas as pd
from typing import Dict, Any, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading


class AliExpressApiProducts:
    def __init__(self, max_workers: int = 10, rate_limit_delay: float = 0.1):
        """
        Initialize with threading configuration

        Args:
            max_workers: Maximum number of concurrent threads
            rate_limit_delay: Delay between requests in seconds to avoid rate limiting
        """
        self.max_workers = max_workers
        self.rate_limit_delay = rate_limit_delay
        self._rate_limit_lock = threading.Lock()
        self._last_request_time = 0

    def process(self, products_df: pd.DataFrame) -> pd.DataFrame:
        products_df = products_df.copy()
        products_df['avg_evaluation_rating'] = None
        products_df['sales_count'] = None
        products_df['evaluation_count'] = None

        # Create a list of (index, product_id) tuples for threading
        tasks = [(index, str(row['product_id'])) for index, row in products_df.iterrows()]
        # Use ThreadPoolExecutor for concurrent API calls
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_task = {
                executor.submit(self._process_single_product, index, product_id): (index, product_id)
                for index, product_id in tasks
            }

            # Process completed tasks
            completed = 0
            for future in as_completed(future_to_task):
                index, product_id = future_to_task[future]
                try:
                    result = future.result()
                    if result:
                        avg_rating, sales_count, eval_count = result
                        products_df.at[index, 'avg_evaluation_rating'] = avg_rating
                        products_df.at[index, 'sales_count'] = sales_count
                        products_df.at[index, 'evaluation_count'] = eval_count

                    completed += 1
                    if completed % 10 == 0:  # Progress indicator
                        print(f"  Completed {completed}/{len(tasks)} products")

                except Exception as e:
                    print(f"  ✗ Error processing product {product_id}: {e}")

        print(f"✓ Completed processing all {len(tasks)} products")
        return products_df

    def _process_single_product(self, index: int, product_id: str) -> Tuple[float, int, int] or None:
        """
        Process a single product with rate limiting

        Returns:
            Tuple of (avg_rating, sales_count, eval_count) or None if failed
        """
        # Rate limiting
        with self._rate_limit_lock:
            current_time = time.time()
            time_since_last = current_time - self._last_request_time
            if time_since_last < self.rate_limit_delay:
                time.sleep(self.rate_limit_delay - time_since_last)
            self._last_request_time = time.time()

        product_data = self.get_product_details(product_id)

        if product_data and 'error' not in product_data:
            try:
                base_info = product_data.get('aliexpress_ds_product_get_response', {}).get('result', {}).get(
                    'ae_item_base_info_dto', {})

                avg_rating = base_info.get('avg_evaluation_rating')
                sales_count = base_info.get('sales_count')
                eval_count = base_info.get('evaluation_count')

                return (
                    float(avg_rating) if avg_rating else None,
                    int(sales_count) if sales_count else None,
                    int(eval_count) if eval_count else None
                )
            except (KeyError, ValueError, TypeError) as e:
                print(f"  ✗ Error extracting data for product {product_id}: {e}")
                return None
        else:
            error_msg = product_data.get('error', 'Unknown error') if product_data else 'No response'
            print(f"  ✗ API error for product {product_id}: {error_msg}")
            return None

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
            response = requests.get(URL, params=params, timeout=30)
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

# Usage example:
# api = AliExpressApiProducts(max_workers=5, rate_limit_delay=0.2)  # 5 threads, 200ms delay
# result_df = api.process(your_products_df)