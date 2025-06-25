from openai import OpenAI
import json
from GLOBAL_CONST import API_KEY_OPEN_AI


class CheckTitle:
    def check(self, product_name, products_df):
        title_list = list(products_df['product_title'])
        final_numbers = []
        batch_size = 10
        offset = 0
        total_input_tokens = 0
        total_output_tokens = 0

        while offset < len(title_list) and len(final_numbers) < 4:
            print(f"Checking titles of rows {offset + 1} to {min(offset + batch_size, len(title_list))}")
            batch = title_list[offset:offset + batch_size]
            result, input_tokens, output_tokens = ProductMatcher().find_suitable_titles(product_name, batch)
            total_input_tokens += input_tokens
            total_output_tokens += output_tokens
            adjusted_result = [i + offset for i in result]
            final_numbers.extend(adjusted_result)
            offset += batch_size

        print(f"Total tokens used - Prompt: {total_input_tokens}, Completion: {total_output_tokens}")
        top_indices = final_numbers[:4]
        filtered_df = products_df.iloc[top_indices].reset_index(drop=True)
        return filtered_df


class ProductMatcher:
    def __init__(self):
        self.client = OpenAI(api_key=API_KEY_OPEN_AI)

    def check_all_titles(self, search_query: str, product_titles: list):
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
                max_tokens=1200,
                temperature=0.1
            )

            result = response.choices[0].message.content.strip()
            if not result:
                print("Error: Empty response from API")
                return {}, {"prompt_tokens": 0, "completion_tokens": 0}

            if result.startswith("```json"):
                result = result[7:]
            if result.startswith("```"):
                result = result[3:]
            if result.endswith("```"):
                result = result[:-3]
            result = result.strip()
            try:
                parsed = json.loads(result)
                usage = {
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "completion_tokens": response.usage.completion_tokens if response.usage else 0
                }
                return parsed, usage
            except json.JSONDecodeError as json_error:
                print(f"JSON parsing error: {json_error}")
                print(f"Failed to parse: '{result}'")
                return {}, {"prompt_tokens": 0, "completion_tokens": 0}
        except Exception as e:
            print(f"Error checking titles: {str(e)}")
            return {}, {"prompt_tokens": 0, "completion_tokens": 0}

    def find_suitable_titles(self, search_query: str, product_titles: list):
        if not product_titles:
            return [], 0, 0

        results, usage = self.check_all_titles(search_query, product_titles)
        if not results:
            return [], usage.get("prompt_tokens", 0), usage.get("completion_tokens", 0)

        suitable_indexes = [int(idx_str) for idx_str, value in results.items() if value == 0]
        return suitable_indexes[:4], usage.get("prompt_tokens", 0), usage.get("completion_tokens", 0)
