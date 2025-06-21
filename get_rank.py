import pandas as pd
import numpy as np
from typing import Optional


class getRank:
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        try:
            df = df.copy()

            # Convert columns to numeric
            df['rating'] = pd.to_numeric(df['avg_evaluation_rating'], errors='coerce')
            df['price'] = pd.to_numeric(df['target_sale_price'], errors='coerce')
            df['saleCount'] = df['sales_count'].astype(str).str.replace(',', '').str.replace('+', '').apply(
                pd.to_numeric, errors='coerce')
            df['ratingCount'] = df['evaluation_count'].astype(str).str.replace(',', '').str.replace('+', '').apply(
                pd.to_numeric, errors='coerce')

            # Handle missing or invalid values
            df['rating'] = df['rating'].fillna(0)
            df['ratingCount'] = df['ratingCount'].fillna(0)
            df['saleCount'] = df['saleCount'].fillna(0)

            min_rating = df['rating'].min()
            max_rating = df['rating'].max()
            min_ratingCount = df['ratingCount'].min()
            max_ratingCount = df['ratingCount'].max()
            min_saleCount = df['saleCount'].min()
            max_saleCount = df['saleCount'].max()
            min_price = df['price'].min()
            max_price = df['price'].max()

            rating_range = max_rating - min_rating
            ratingCount_range = max_ratingCount - min_ratingCount
            saleCount_range = max_saleCount - min_saleCount
            price_range = max_price - min_price

            if rating_range == 0:
                df['norm_rating'] = 1.0
            else:
                df['norm_rating'] = (df['rating'] - min_rating) / rating_range

            if ratingCount_range == 0:
                df['norm_ratingCount'] = 1.0
            else:
                df['norm_ratingCount'] = (df['ratingCount'] - min_ratingCount) / ratingCount_range

            if saleCount_range == 0:
                df['norm_saleCount'] = 1.0
            else:
                df['norm_saleCount'] = (df['saleCount'] - min_saleCount) / saleCount_range

            if price_range == 0:
                df['norm_priceScore'] = 1.0
            else:
                df['norm_priceScore'] = 1 - (df['price'] - min_price) / price_range

            # Calculate Quality Score with equal weights
            df['QualityScoreValue'] = (
                    0.33 * df['norm_rating'] +
                    0.33 * df['norm_ratingCount'] +
                    0.34 * df['norm_saleCount']
            )

            # Calculate Final Score - "The Value Product" formula
            df['grade'] = (
                    0.5 * df['QualityScoreValue'] +
                    0.5 * df['norm_priceScore']
            )

            # Round the grade
            df['grade'] = df['grade'].round(4)

            # Add ranking: highest grade gets lowest rank (1, 2, 3, ...)
            df_shuffled = df.sample(frac=1, random_state=None).reset_index(drop=True)
            df_shuffled['rank'] = df_shuffled['grade'].rank(method='first', ascending=False, na_option='bottom')
            df_shuffled['rank'] = df_shuffled['rank'].astype('Int64')

            # Sort back to maintain original order logic but with ranks assigned
            df = df_shuffled.sort_index()

            # Clean up temporary columns
            df = df.drop(columns=['rating', 'price', 'saleCount', 'ratingCount',
                                  'norm_rating', 'norm_ratingCount', 'norm_saleCount',
                                  'norm_priceScore', 'QualityScoreValue'])

            # Sort the final dataframe by rank (ascending order)
            df = df.sort_values('rank', ascending=True, na_position='last').reset_index(drop=True)

            return df

        except Exception as e:
            print(f"Error calculating grade: {e}")
            df['grade'] = pd.NA
            df['rank'] = pd.NA
            return df