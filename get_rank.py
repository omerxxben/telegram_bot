import pandas as pd
from typing import Optional


class getRank:
    def __init__(self):
        """
        Initialize getRank class for calculating product grades.
        """
        pass

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate grade column based on formula:
        grade = (avg_evaluation_rating * sales_count * evaluation_count) / target_sale_price

        Args:
            df: DataFrame with the required columns

        Returns:
            DataFrame with added 'grade' column
        """
        try:
            df = df.copy()

            # Convert columns to numeric, handling various formats
            df['avg_evaluation_rating_num'] = pd.to_numeric(df['avg_evaluation_rating'], errors='coerce')
            df['target_sale_price_num'] = pd.to_numeric(df['target_sale_price'], errors='coerce')

            # Parse sales_count and evaluation_count (handle strings with commas, '+' signs, etc.)
            df['sales_count_num'] = df['sales_count'].astype(str).str.replace(',', '').str.replace('+', '').apply(
                pd.to_numeric, errors='coerce')
            df['evaluation_count_num'] = df['evaluation_count'].astype(str).str.replace(',', '').str.replace('+',
                                                                                                             '').apply(
                pd.to_numeric, errors='coerce')

            # Calculate grade with error handling for division by zero
            df['grade'] = (
                                  df['avg_evaluation_rating_num'] *
                                  df['sales_count_num'] *
                                  df['evaluation_count_num']
                          ) / df['target_sale_price_num']

            # Replace inf and -inf with NaN (division by zero cases)
            df['grade'] = df['grade'].replace([float('inf'), float('-inf')], pd.NA)

            # Round grade to 2 decimal places
            df['grade'] = df['grade'].round(2)

            # Drop temporary numeric columns
            df = df.drop(columns=['avg_evaluation_rating_num', 'target_sale_price_num',
                                  'sales_count_num', 'evaluation_count_num'])

            print(f"Grade calculated for {len(df)} products")
            return df

        except Exception as e:
            print(f"Error calculating grade: {e}")
            df['grade'] = pd.NA
            return df

    def get_top_products(self, df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
        """
        Get top N products based on rank.

        Args:
            df: DataFrame with rank column
            top_n: Number of top products to return

        Returns:
            DataFrame with top N products sorted by rank (ascending)
        """
        try:
            if 'rank' not in df.columns:
                df = self.calculate(df)

            # Get top N products by rank (lowest rank numbers = best products)
            top_products = df.nsmallest(top_n, 'rank')
            print(f"Retrieved top {len(top_products)} products by rank")
            return top_products

        except Exception as e:
            print(f"Error getting top products: {e}")
            return df

    def filter_by_min_grade(self, df: pd.DataFrame, min_grade: float) -> pd.DataFrame:
        """
        Filter products by minimum grade threshold.

        Args:
            df: DataFrame with grade column
            min_grade: Minimum grade threshold

        Returns:
            DataFrame with products above minimum grade
        """
        try:
            if 'grade' not in df.columns:
                df = self.calculate(df)

            filtered_df = df[df['grade'] >= min_grade]
            print(f"Filtered {len(filtered_df)} products with grade >= {min_grade}")
            return filtered_df

        except Exception as e:
            print(f"Error filtering by grade: {e}")
            return df

    def get_grade_summary(self, df: pd.DataFrame) -> dict:
        """
        Get summary statistics for grades and ranks.

        Args:
            df: DataFrame with grade and rank columns

        Returns:
            Dictionary with grade and rank statistics
        """
        try:
            if 'grade' not in df.columns or 'rank' not in df.columns:
                df = self.calculate(df)

            grade_stats = {
                'count': len(df),
                'grade_mean': df['grade'].mean(),
                'grade_median': df['grade'].median(),
                'grade_min': df['grade'].min(),
                'grade_max': df['grade'].max(),
                'grade_std': df['grade'].std(),
                'products_with_grade': df['grade'].notna().sum(),
                'products_without_grade': df['grade'].isna().sum(),
                'top_rank': df['rank'].min(),
                'bottom_rank': df['rank'].max(),
                'products_with_rank': df['rank'].notna().sum()
            }

            return grade_stats

        except Exception as e:
            print(f"Error getting grade summary: {e}")
            return {}