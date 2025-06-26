import pandas as pd
from typing import Dict, List, Any, Optional


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

    def transform_to_table(self, products: Dict[str, Any]) -> pd.DataFrame:
        try:
            products_data = products.get(
                'aliexpress_affiliate_hotproduct_query_response', {}
            ).get('resp_result', {}).get('result', {}).get('products', {}).get('product', [])

            if not products_data:
                return pd.DataFrame(columns=self.columns)

            # Extract specified columns from each product
            transformed_data = []
            for product in products_data:
                row = {}
                for column in self.columns:
                    row[column] = product.get(column, '')
                transformed_data.append(row)
            print(f"pulled this number of rows from hotproducts api: {len(transformed_data)}")

            return pd.DataFrame(transformed_data)

        except Exception as e:
            print(f"Error transforming data: {e}")
            return pd.DataFrame(columns=self.columns)

    def transform_product_names(self, product):
        return {
            "rating": product.get("avg_evaluation_rating"),
            "reviews_count": int(product.get("evaluation_count", 0)),
            "product_title": product.get("subject"),
            "sales_count": int(product.get("sales_count", 0)),
            "price": float(product.get("target_sale_price", 0)),
            "affiliate_link": product.get("promotion_link")
        }
