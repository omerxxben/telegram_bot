import json
import re
from collections import defaultdict


class CategoryFinder:
    """
    A class with a static method to find the most relevant product category
    from an AliExpress category list based on a given set of keywords.
    """

    @staticmethod
    def _get_category_path(category_id, category_map):
        """
        Constructs the full name path of a category (e.g., "Electronics > Audio > Speakers").
        This is a static helper method.

        Args:
            category_id (int): The ID of the category to trace.
            category_map (dict): A pre-built map of category IDs to category objects.

        Returns:
            str: The full hierarchical name of the category.
        """
        path = []
        current_id = category_id
        while current_id in category_map:
            category = category_map[current_id]
            # *** FIX: Check if 'category_name' exists before appending to path ***
            if 'category_name' in category:
                path.append(category['category_name'])

            current_id = category.get('parent_category_id')
            # Stop if there's no parent or if the parent is the root (ID 0)
            if not current_id or current_id == 0:
                break
        return " > ".join(reversed(path))

    @staticmethod
    def process(category_json, keywords):
        """
        Processes the category data and keywords to find the best matching category.
        This can be called directly on the class: CategoryFinder.process(json, keywords).

        Args:
            category_json (str or dict): A JSON string or a Python dictionary
                                        representing the AliExpress category structure.
            keywords (str): A string of keywords, e.g., "jbl flip 6 speaker".

        Returns:
            dict: The dictionary object of the best matching category,
                  or None if no suitable category is found.
        """
        # --- Data Initialization (moved from __init__) ---
        try:
            if isinstance(category_json, str):
                full_category_data = json.loads(category_json)
            elif isinstance(category_json, dict):
                full_category_data = category_json
            else:
                raise TypeError("category_json must be a JSON string or a dictionary.")

            # *** UPDATED JSON PATHING TO MATCH API RESPONSE ***
            categories = full_category_data.get("aliexpress_affiliate_category_get_response", {}) \
                .get("resp_result", {}) \
                .get("result", {}) \
                .get("categories", {}) \
                .get("category", [])

            category_map = {cat['category_id']: cat for cat in categories}

            if not categories:
                print("Warning: No categories were found in the provided JSON data.")
                return None

        except (json.JSONDecodeError, TypeError) as e:
            print(f"Error processing category JSON: {e}")
            return None
        # --- End of Initialization ---

        if not categories:
            print("Cannot process keywords: Category list is empty.")
            return None

        # *** FIX: Split keywords and remove any that are just numbers ***
        all_tokens = re.split(r'\s+', keywords.lower())
        clean_keywords = {token for token in all_tokens if not token.isdigit()}

        best_category = None
        highest_score = -1

        print(f"Searching for best category with keywords: {clean_keywords}\n")

        for category in categories:
            # *** FIX: Check if the category has a name. If not, skip it. ***
            if 'category_name' not in category:
                continue

            current_score = 0

            category_name_lower = category['category_name'].lower()
            full_path_lower = CategoryFinder._get_category_path(category['category_id'], category_map).lower()

            # --- SCORING LOGIC ---
            for word in clean_keywords:
                if word in category_name_lower:
                    current_score += 15
                if word in full_path_lower:
                    current_score += 5

            if category.get('is_leaf', False):
                current_score += 25

            depth = len(full_path_lower.split(' > '))
            current_score += depth * 2

            # --- Update best score ---
            if current_score > highest_score:
                highest_score = current_score
                best_category = category

        if best_category:
            print(f"Best Match Found:")
            print(f"  - Category Name: {best_category['category_name']}")
            print(f"  - Category ID: {best_category['category_id']}")
            print(f"  - Full Path: {CategoryFinder._get_category_path(best_category['category_id'], category_map)}")
            print(f"  - Score: {highest_score}")
        else:
            print("No suitable category found.")

        return best_category
