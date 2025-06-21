import pandas as pd
from typing import Dict, List, Any, Optional


class ProductsTransform:
    def __init__(self):
        self.columns = [
            'rank',
            'grade',
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
                'aliexpress_affiliate_product_query_response', {}
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

            return pd.DataFrame(transformed_data)
        except Exception as e:
            print(f"Error transforming data: {e}")
            return pd.DataFrame(columns=self.columns)

    def transform_to_dict_list(self, api_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        try:
            # Navigate through the nested structure
            products_data = api_result.get(
                'aliexpress_affiliate_product_query_response', {}
            ).get('resp_result', {}).get('result', {}).get('products', {}).get('product', [])

            if not products_data:
                return []

            # Extract specified columns from each product
            transformed_data = []
            for product in products_data:
                row = {}
                for column in self.columns:
                    row[column] = product.get(column, '')
                transformed_data.append(row)

            return transformed_data

        except Exception as e:
            print(f"Error transforming data: {e}")
            return []

    def filter_by_commission_rate(self, api_result: Dict[str, Any]) -> pd.DataFrame:
        """
        Filter products to remove rows where commission_rate is empty, None, or zero.
        Returns a DataFrame with only products that have a valid commission rate.
        """
        try:
            df = self.transform_to_table(api_result)
            #return df
            if df.empty:
                return df

            # Filter out rows where commission_rate is empty, None, NaN, or zero
            # This handles various "no value" scenarios
            filtered_df = df[
                (df['commission_rate'] != '') &
                (df['commission_rate'].notna()) &
                (df['commission_rate'] != '0') &
                (df['commission_rate'] != 0)
                ]

            print(f"Original rows: {len(df)}, Filtered rows: {len(filtered_df)}")
            return filtered_df

        except Exception as e:
            print(f"Error filtering data: {e}")
            return pd.DataFrame(columns=self.columns)

    def print_table(self, api_result: Dict[str, Any]) -> None:
        df = self.transform_to_table(api_result)

        if df.empty:
            print("No data to display")
            return

        # Set display options for better formatting
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        pd.set_option('display.max_colwidth', 50)

        print(df.to_string(index=False))

    def save_to_csv(self, api_result: Dict[str, Any], filename: str = 'aliexpress_products.csv') -> None:
        df = self.transform_to_table(api_result)
        if df.empty:
            print("No data to save")
            return
        df.to_csv(filename, index=False, encoding='utf-8')
        print(f"Data saved to {filename}")

    def save_filtered_to_csv(self, api_result: Dict[str, Any],
                             filename: str = 'aliexpress_products_filtered.csv') -> None:
        """
        Save filtered products (with valid commission rates) to CSV.
        """
        df = self.filter_by_commission_rate(api_result)
        if df.empty:
            print("No filtered data to save")
            return
        df.to_csv(filename, index=False, encoding='utf-8')
        print(f"Filtered data saved to {filename}")

    def get_summary_stats(self, api_result: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # Get basic info from the API response
            resp_result = api_result.get('aliexpress_affiliate_product_query_response', {}).get('resp_result', {})
            result = resp_result.get('result', {})

            return {
                'total_record_count': result.get('total_record_count', 0),
                'current_record_count': result.get('current_record_count', 0),
                'current_page_no': result.get('current_page_no', 1),
                'columns_extracted': self.columns,
                'response_code': resp_result.get('resp_code', 'Unknown'),
                'response_message': resp_result.get('resp_msg', 'Unknown')
            }
        except Exception as e:
            return {'error': f"Error getting summary: {e}"}