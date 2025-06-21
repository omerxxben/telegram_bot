import pandas as pd
import numpy as np
from typing import Optional


class getRank:
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        try:
            df = df.copy()
            df['avg_evaluation_rating_num'] = pd.to_numeric(df['avg_evaluation_rating'], errors='coerce')
            df['target_sale_price_num'] = pd.to_numeric(df['target_sale_price'], errors='coerce')
            df['sales_count_num'] = df['sales_count'].astype(str).str.replace(',', '').str.replace('+', '').apply(
                pd.to_numeric, errors='coerce')
            df['evaluation_count_num'] = df['evaluation_count'].astype(str).str.replace(',', '').str.replace('+',
                                                                                                             '').apply(
                pd.to_numeric, errors='coerce')
            # Replace zeros with 1 for the multiplication components
            df['avg_evaluation_rating_num'] = df['avg_evaluation_rating_num'].replace(0, 1)
            df['sales_count_num'] = df['sales_count_num'].replace(0, 1)
            df['evaluation_count_num'] = df['evaluation_count_num'].replace(0, 1)

            df['grade'] = (
                                  df['avg_evaluation_rating_num'] *
                                  df['sales_count_num'] *
                                  df['evaluation_count_num']
                          ) / df['target_sale_price_num']
            df['grade'] = df['grade'].replace([float('inf'), float('-inf')], pd.NA)
            df['grade'] = df['grade'].round(2)

            # Add ranking: highest grade gets lowest rank (1, 2, 3, ...)
            # For ties, random selection is achieved by shuffling before ranking
            df_shuffled = df.sample(frac=1, random_state=None).reset_index(drop=True)
            df_shuffled['rank'] = df_shuffled['grade'].rank(method='first', ascending=False, na_option='bottom')
            df_shuffled['rank'] = df_shuffled['rank'].astype('Int64')  # Use nullable integer type

            # Sort back to maintain original order logic but with ranks assigned
            df = df_shuffled.sort_index()

            df = df.drop(columns=['avg_evaluation_rating_num', 'target_sale_price_num',
                                  'sales_count_num', 'evaluation_count_num'])

            # Sort the final dataframe by rank (ascending order)
            df = df.sort_values('rank', ascending=True, na_position='last').reset_index(drop=True)

            return df

        except Exception as e:
            print(f"Error calculating grade: {e}")
            df['grade'] = pd.NA
            df['rank'] = pd.NA
            return df