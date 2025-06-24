from openai import OpenAI

from GLOBAL_CONST import API_KEY_OPEN_AI


class CategoryFilter:
    def filter(self, products_df, product_name_english):
        category_set = set()
        for _, row in products_df.iterrows():
            category_str = f"{row['first_level_category_name']}:{row['second_level_category_name']}"
            category_set.add(category_str)
        the_best_category = self.ai_picker(category_set, product_name_english)
        print(the_best_category)
        filtered_df = self.remove_matching_category(products_df, the_best_category)
        print(filtered_df)
        return filtered_df

    def remove_matching_category(self, products_df, category_str):
        if not category_str:
            return products_df  # Nothing to remove
        first_cat, second_cat = category_str.split(':', 1)
        filtered_df = products_df[
            (
                    (products_df['first_level_category_name'] == first_cat) &
                    (products_df['second_level_category_name'] == second_cat)
            )
        ]
        return filtered_df

    def ai_picker(self, category_set, product_name_english):
        category_list = list(category_set)
        if not category_list:
            return None
        matcher = self.CategoryMatcher()
        return matcher.match_category(product_name_english, category_list)

    class CategoryMatcher:
        def __init__(self):
            self.client = OpenAI(api_key=API_KEY_OPEN_AI)

        def match_category(self, product_name: str, category_variations: list) -> str:
            if not category_variations:
                return "Error: No category variations provided"

            # Format the variations for the prompt
            variations_text = "\n".join([f"variation {i + 1}: {cat}" for i, cat in enumerate(category_variations)])

            try:
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a product categorization expert. Given a product name and a list of category variations in the format 'first_level:second_level', you must select the BEST matching category. Return ONLY the exact category string from the provided variations, nothing else."
                        },
                        {
                            "role": "user",
                            "content": f"Product name: {product_name}\n\nAvailable category variations:\n{variations_text}\n\nSelect the best matching category:"
                        }
                    ],
                    max_tokens=100,
                    temperature=0.1
                )

                result = response.choices[0].message.content.strip()

                # Validate that the result is one of the provided variations
                if result in category_variations:
                    return result
                else:
                    # If not exact match, find the closest one
                    for variation in category_variations:
                        if variation in result or result in variation:
                            return variation
                    # Fallback to first variation if no match found
                    return category_variations[0]

            except Exception as e:
                return f"Categorization error: {str(e)}"
