import pandas as pd
from tabulate import tabulate
import numpy as np


def pretty_print_df(df, style='grid', float_format='.2f', max_rows=None,
                    max_cols=None, show_index=True, title=None, colors=True):
    # Make a copy to avoid modifying original
    display_df = df.copy()

    # Handle max_rows
    if max_rows and len(display_df) > max_rows:
        half_rows = max_rows // 2
        top_part = display_df.head(half_rows)
        bottom_part = display_df.tail(max_rows - half_rows)

        # Create separator row
        separator_data = ['...' for _ in range(len(display_df.columns))]
        separator_df = pd.DataFrame([separator_data], columns=display_df.columns)

        display_df = pd.concat([top_part, separator_df, bottom_part], ignore_index=True)

    # Handle max_cols
    if max_cols and len(display_df.columns) > max_cols:
        half_cols = max_cols // 2
        left_cols = display_df.columns[:half_cols].tolist()
        right_cols = display_df.columns[-half_cols:].tolist()
        separator_col = ['...'] * len(display_df)

        left_part = display_df[left_cols]
        right_part = display_df[right_cols]
        left_part['...'] = separator_col

        display_df = pd.concat([left_part, right_part], axis=1)

    # Format numeric columns
    for col in display_df.columns:
        if display_df[col].dtype in ['float64', 'float32']:
            display_df[col] = display_df[col].apply(lambda x: f"{x:{float_format}}" if pd.notna(x) else 'NaN')

    # Color codes for headers (if colors enabled)
    if colors:
        BOLD = '\033[1m'
        BLUE = '\033[94m'
        GREEN = '\033[92m'
        YELLOW = '\033[93m'
        RED = '\033[91m'
        ENDC = '\033[0m'
    else:
        BOLD = BLUE = GREEN = YELLOW = RED = ENDC = ''

    # Print title if provided
    if title:
        print(f"\n{BOLD}{BLUE}{'=' * len(title)}{ENDC}")
        print(f"{BOLD}{BLUE}{title}{ENDC}")
        print(f"{BOLD}{BLUE}{'=' * len(title)}{ENDC}")

    # Print the table
    if show_index:
        table_data = display_df
        headers = ['Index'] + list(display_df.columns)
        table_data = [[idx] + list(row) for idx, row in zip(display_df.index, display_df.values)]
    else:
        table_data = display_df.values
        headers = list(display_df.columns)

    print(f"\n{tabulate(table_data, headers=headers, tablefmt=style)}")


def quick_pretty_print(df, max_display=20):
    print(f"\nDataFrame ({df.shape[0]} rows × {df.shape[1]} columns)")
    print("=" * 50)

    if len(df) > max_display:
        print(f"Showing first {max_display // 2} and last {max_display // 2} rows:")
        display_df = pd.concat([df.head(max_display // 2), df.tail(max_display // 2)])
    else:
        display_df = df
    print(tabulate(display_df, headers=display_df.columns, tablefmt='grid', showindex=True))
    if len(df) > max_display:
        print(f"\n... ({len(df) - max_display} rows omitted) ...")
