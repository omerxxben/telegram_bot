import json
import requests
import hashlib
import time
import os
import datetime

from GLOBAL_CONST import *

CATEGORY_FILE_PATH = "category.json"
CACHE_DURATION_HOURS = 24


class AliExpressApiCategories:
    def process(self):
        # Check if the cache file exists and is recent
        if os.path.exists(CATEGORY_FILE_PATH):
            last_modified_time = os.path.getmtime(CATEGORY_FILE_PATH)
            if (time.time() - last_modified_time) < (CACHE_DURATION_HOURS * 3600):
                with open(CATEGORY_FILE_PATH, 'r') as f:
                    return json.load(f)

        print("Fetching new category data from API.")
        timestamp = int(time.time() * 1000)
        params = {
            "app_key": APP_KEY,
            "timestamp": timestamp,
            "method": "aliexpress.affiliate.category.get",
            "sign_method": "md5",
            "format": "json",
            "v": "2.0",
        }
        params["sign"] = self.generate_signature(params)
        try:
            response = requests.get(URL, params=params)
            response.raise_for_status()
            data = response.json()
            with open(CATEGORY_FILE_PATH, 'w') as f:
                json.dump(data, f, indent=4)
            return data
        except requests.exceptions.RequestException as e:
            return {"error": f"Request failed: {e}"}
        except json.JSONDecodeError:
            return {"error": "Failed to decode JSON response."}
        except Exception as e:
            return {"error": str(e)}

    def generate_signature(self, params: dict) -> str:
        sorted_params = ''.join(f'{k}{v}' for k, v in sorted(params.items()))
        sign_str = f"{APP_SECRET}{sorted_params}{APP_SECRET}"
        return hashlib.md5(sign_str.encode('utf-8')).hexdigest().upper()