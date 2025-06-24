from openai import OpenAI
import json

from GLOBAL_CONST import API_KEY_OPEN_AI


class CheckTitle:
    def check(self, product_name, products_df):
        title_list = list(products_df['product_title'])
        final_numbers = []
        batch_size = 5
        offset = 0
        while offset < len(title_list) and len(final_numbers) < 4:
            batch = title_list[offset:offset + batch_size]
            result = ProductMatcher().find_suitable_titles(product_name, batch)
            adjusted_result = [i + offset for i in result]
            final_numbers.extend(adjusted_result)
            offset += batch_size
        top_indices = final_numbers[:4]
        filtered_df = products_df.iloc[top_indices].reset_index(drop=True)
        return filtered_df

class ProductMatcher:
    def __init__(self):
        self.client = OpenAI(api_key=API_KEY_OPEN_AI)

    def check_all_titles(self, search_query: str, product_titles: list) -> dict:
        titles_text = "\n".join([f"{i}: {title}" for i, title in enumerate(product_titles)])
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a strict product matching expert. Analyze if each product title is an EXACT match for the search query category. Be very strict: only return 0 (suitable) if the product IS the actual item being searched for, not accessories, parts, or related items. For example: if searching 'wireless headphones', only actual headphones/earbuds should be 0, NOT charging cables, cases, stands, or other accessories. Return ONLY a JSON object with format: {\"0\": 0, \"1\": 1, \"2\": 0, ...} where each key is the title index and each value is: 0 = exact category match, 1 = not exact match."
                    },
                    {
                        "role": "user",
                        "content": f"Search query: \"{search_query}\"\n\nProduct titles to analyze:\n{titles_text}\n\nReturn JSON with 0 for relevant titles, 1 for irrelevant titles:"
                    }
                ],
                max_tokens=1000,
                temperature=0.1
            )

            result = response.choices[0].message.content.strip()
            return json.loads(result)

        except Exception as e:
            print(f"Error checking titles: {str(e)}")
            return {}

    def find_suitable_titles(self, search_query: str, product_titles: list) -> list:

        if not product_titles:
            print("No product titles provided")
            return []

        # Check all titles at once
        results = self.check_all_titles(search_query, product_titles)

        if not results:
            print("Failed to get results from AI model")
            return []

        # Convert string keys to integers for cleaner output
        int_results = {int(k): v for k, v in results.items()}
        print(f"AI returned: {int_results}")  # Debug output

        # Extract suitable indexes (where value is 0)
        suitable_indexes = []
        for idx_str, value in results.items():
            idx = int(idx_str)
            if value == 0:
                suitable_indexes.append(idx)
                print(f"Found suitable at index {idx}: {product_titles[idx]}")  # Debug output

        # Return first 3 suitable indexes
        return suitable_indexes[:4]