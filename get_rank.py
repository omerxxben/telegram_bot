import pandas as pd
from typing import Optional


class getRank:
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        try:
            df = df.copy()
            df['avg_evaluation_rating_num'] = pd.to_numeric(df['avg_evaluation_rating'], errors='coerce')
            df['target_sale_price_num'] = pd.to_numeric(df['target_sale_price'], errors='coerce')
            df['sales_count_num'] = df['sales_count'].astype(str).str.replace(',', '').str.replace('+', '').apply(
                pd.to_numeric, errors='coerce')
            df['evaluation_count_num'] = df['evaluation_count'].astype(str).str.replace(',', '').str.replace('+','').apply(
                pd.to_numeric, errors='coerce')
            df['grade'] = (
                                  df['avg_evaluation_rating_num'] *
                                  df['sales_count_num'] *
                                  df['evaluation_count_num']
                          ) / df['target_sale_price_num']
            df['grade'] = df['grade'].replace([float('inf'), float('-inf')], pd.NA)
            df['grade'] = df['grade'].round(2)
            df = df.drop(columns=['avg_evaluation_rating_num', 'target_sale_price_num',
                                  'sales_count_num', 'evaluation_count_num'])
            return df

        except Exception as e:
            print(f"Error calculating grade: {e}")
            df['grade'] = pd.NA
            return df
