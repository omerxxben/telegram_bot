import time

import pandas as pd
from typing import Dict, List, Any, Optional

from Classes.GLOBAL_CONST import get_products_api


class ProductsTransform:
    def __init__(self):
        self.columns = [
            'rank',
            'grade',
            'lastest_volume',
            'first_level_category_name',
            'second_level_category_name',
            'product_id',
            'target_sale_price',
            'commission_rate',
            'avg_evaluation_rating',
            'sales_count',
            'evaluation_count',
            'product_title',
            'product_main_image_url',
            'promotion_link',
        ]

    def transform_to_table(self, products: Dict[str, Any]):
        start_time = time.time()
        new_get_products_api = get_products_api.replace('.', '_')
        try:
            products_data = products.get(
                f"{new_get_products_api}_response", {}
            ).get('resp_result', {}).get('result', {}).get('products', {}).get('product', [])

            if not products_data:
                return pd.DataFrame(columns=self.columns), 0

            # Extract specified columns from each product
            transformed_data = []
            for product in products_data:
                row = {}
                for column in self.columns:
                    row[column] = product.get(column, '')
                transformed_data.append(row)
            print(f"pulled this number of rows from hotproducts api: {len(transformed_data)}")
            total_time =  time.time() - start_time
            return pd.DataFrame(transformed_data), total_time

        except Exception as e:
            total_time =  time.time() - start_time
            print(f"Error transforming data: {e}")
            return pd.DataFrame(columns=self.columns), total_time

    def transform_product_names(self, product):
        return {
            "rating": product.get("avg_evaluation_rating"),
            "reviews_count": product.get("evaluation_count"),
            "product_title": product.get("subject"),
            "sales_count": product.get("sales_count"),
            "price": product.get("target_sale_price"),
            "affiliate_link": product.get("promotion_link"),
            "product_main_image_url": product.get("product_main_image_url")
        }

    def parse_to_list(self, products_df_detailed):
        selected_columns = [
            "target_sale_price",
            "avg_evaluation_rating",
            "sales_count",
            "evaluation_count",
            "subject",
            "promotion_link",
            "product_main_image_url",
        ]
        filtered_df = products_df_detailed[selected_columns].copy()
        products_list = filtered_df.to_dict(orient="records")
        transformed_products = [
            ProductsTransform().transform_product_names(product) for product in products_list
        ]
        return transformed_products