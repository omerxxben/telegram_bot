import pandas as pd
from tabulate import tabulate
import numpy as np
import unicodedata
import re


def get_display_width(text):
    """Calculate the display width of text, accounting for Hebrew and other scripts."""
    if pd.isna(text):
        return 3  # width of 'NaN'

    text = str(text)
    width = 0

    # Remove ANSI color codes for width calculation
    text_no_ansi = re.sub(r'\033\[[0-9;]*m', '', text)

    for char in text_no_ansi:
        # Hebrew characters
        if 0x0590 <= ord(char) <= 0x05FF:
            width += 1
        # Arabic characters
        elif 0x0600 <= ord(char) <= 0x06FF:
            width += 1
        # East Asian wide characters
        elif unicodedata.east_asian_width(char) in ('F', 'W'):
            width += 2
        # Regular characters
        else:
            width += 1

    return width


def format_cell_content(content, target_width, align='left'):
    """Format cell content with proper padding, handling Hebrew text."""
    if pd.isna(content):
        content = 'NaN'
    else:
        content = str(content)

    display_width = get_display_width(content)

    if display_width >= target_width:
        return content

    padding = target_width - display_width

    if align == 'right':
        return ' ' * padding + content
    elif align == 'center':
        left_pad = padding // 2
        right_pad = padding - left_pad
        return ' ' * left_pad + content + ' ' * right_pad
    else:  # left align
        return content + ' ' * padding


def normalize_hebrew_text(text):
    """Normalize Hebrew text for better display in tables."""
    if pd.isna(text):
        return text

    text = str(text)

    # Force LTR direction for the entire text to prevent table layout issues
    # This is crucial for terminal table display
    ltr_mark = '\u200E'  # Left-to-right mark

    # Add LTR mark at the beginning to force overall direction
    text = ltr_mark + text

    # For mixed Hebrew-English text, add directional marks
    if any('\u0590' <= c <= '\u05FF' for c in text):  # Contains Hebrew
        # Add LTR mark after Hebrew segments to stabilize direction
        text = re.sub(r'([א-ת]+)', r'\1' + ltr_mark, text)

    return text


def pretty_print_df(df, style='grid', float_format='.2f', max_rows=None,
                    max_cols=None, show_index=True, title=None, colors=True,
                    hebrew_support=True, min_col_width=8, force_ltr=True):
    """
    Pretty print DataFrame with enhanced Hebrew text support.

    Parameters:
    -----------
    hebrew_support : bool
        Enable Hebrew text normalization and width calculation
    min_col_width : int
        Minimum width for columns (helpful for Hebrew text)
    force_ltr : bool
        Force left-to-right text direction for table stability
    """

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

    # Process Hebrew text if enabled
    if hebrew_support:
        for col in display_df.columns:
            if display_df[col].dtype == 'object':  # String columns
                display_df[col] = display_df[col].apply(normalize_hebrew_text)

        # Also normalize column names if they contain Hebrew
        new_columns = []
        for col in display_df.columns:
            if isinstance(col, str) and any('\u0590' <= c <= '\u05FF' for c in col):
                new_columns.append(normalize_hebrew_text(col))
            else:
                new_columns.append(col)
        display_df.columns = new_columns

    # Format numeric columns
    for col in display_df.columns:
        if display_df[col].dtype in ['float64', 'float32']:
            display_df[col] = display_df[col].apply(
                lambda x: f"{x:{float_format}}" if pd.notna(x) else 'NaN'
            )

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
        title_display = normalize_hebrew_text(title) if hebrew_support else title
        separator_line = '=' * max(len(title), 40)
        print(f"\n{BOLD}{BLUE}{separator_line}{ENDC}")
        print(f"{BOLD}{BLUE}{title_display}{ENDC}")
        print(f"{BOLD}{BLUE}{separator_line}{ENDC}")

    # Force LTR environment for the entire table if requested
    if force_ltr:
        print('\u202D', end='')  # Left-to-right override

    # Prepare table data with proper formatting
    if show_index:
        headers = ['Index'] + list(display_df.columns)
        table_data = []

        for idx, row in zip(display_df.index, display_df.values):
            formatted_row = [str(idx)] + [str(val) for val in row]
            table_data.append(formatted_row)
    else:
        headers = list(display_df.columns)
        table_data = [[str(val) for val in row] for row in display_df.values]

    # Use tabulate with Hebrew-friendly settings
    table_str = tabulate(
        table_data,
        headers=headers,
        tablefmt=style,
        stralign='left',  # Force left alignment
        numalign='left',  # Also force numbers to left for consistency
        floatfmt=float_format
    )

    print(f"\n{table_str}")

    # End LTR override
    if force_ltr:
        print('\u202C', end='')  # Pop directional formatting


def quick_pretty_print(df, max_display=20, hebrew_support=True):
    """Quick pretty print with Hebrew support."""
    shape_info = f"DataFrame ({df.shape[0]} rows × {df.shape[1]} columns)"
    print(f"\n{shape_info}")
    print("=" * len(shape_info))

    if len(df) > max_display:
        print(f"Showing first {max_display // 2} and last {max_display // 2} rows:")
        display_df = pd.concat([df.head(max_display // 2), df.tail(max_display // 2)])
    else:
        display_df = df.copy()

    # Apply Hebrew normalization if enabled
    if hebrew_support:
        for col in display_df.columns:
            if display_df[col].dtype == 'object':
                display_df[col] = display_df[col].apply(normalize_hebrew_text)

    table_str = tabulate(
        display_df,
        headers=display_df.columns,
        tablefmt='grid',
        showindex=True,
        stralign='left'
    )

    print(table_str)

    if len(df) > max_display:
        omitted_count = len(df) - max_display
        print(f"\n... ({omitted_count} rows omitted) ...")


def create_sample_hebrew_df():
    """Create a sample DataFrame with Hebrew text for testing."""
    data = {
        'Name': ['אביב כהן', 'שרה לוי', 'David Smith', 'מרים ישראל'],
        'City': ['תל אביב', 'Jerusalem ירושלים', 'New York', 'חיפה'],
        'Age': [25, 30, 35, 28],
        'Score': [95.5, 87.2, 92.8, 88.9],
        'Status': ['פעיל', 'Active פעיל', 'Inactive', 'חדש']
    }
    return pd.DataFrame(data)


# Example usage
if __name__ == "__main__":
    # Create sample data with Hebrew
    df = create_sample_hebrew_df()

    print("=== Testing Hebrew DataFrame Display ===")

    # Test the enhanced pretty print
    pretty_print_df(
        df,
        title="Sample Hebrew Data דוגמה",
        hebrew_support=True,
        style='grid'
    )

    print("\n" + "=" * 50)
    print("Quick Pretty Print Test:")
    quick_pretty_print(df, hebrew_support=True)