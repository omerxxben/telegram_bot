from ai_manager import AIManager


class CategoryFilter:
    def filter(self, products_df, product_name_english):
        category_set = set()
        for _, row in products_df.iterrows():
            category_str = f"{row['first_level_category_name']}:{row['second_level_category_name']}"
            category_set.add(category_str)
        the_best_category = self.ai_picker(category_set, product_name_english)
        print("the best category found by ai is: " + the_best_category)
        print("other categories: " + str(category_set))

        filtered_df = self.remove_matching_category(products_df, the_best_category)
        print(f"numer of rows remaining after category filtered: {len(filtered_df)}")
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
        return AIManager().match_category(product_name_english, category_list)
