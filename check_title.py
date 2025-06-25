from ai_manager import AIManager

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
            result, input_tokens, output_tokens = AIManager().find_suitable_titles(product_name, batch)
            total_input_tokens += input_tokens
            total_output_tokens += output_tokens
            adjusted_result = [i + offset for i in result]
            final_numbers.extend(adjusted_result)
            offset += batch_size

        print(f"Total tokens used - Prompt: {total_input_tokens}, Completion: {total_output_tokens}")
        top_indices = final_numbers[:4]
        filtered_df = products_df.iloc[top_indices].reset_index(drop=True)
        return filtered_df