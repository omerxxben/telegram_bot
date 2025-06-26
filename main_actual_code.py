from Classes.ali_epress_api_products import AliExpressApiProducts
from Classes.general_tools import pretty_print_df
from Classes.ali_epress_api import AliExpressApi
from Classes.get_rank import getRank
from Classes.image_grid_creator import ImageGridCreator
from Classes.products_transform import ProductsTransform
from Classes.ai_manager import AIManager


class MainProducts:
    def process(self, search_query, logs_flag = False):
        creator = ImageGridCreator(grid_size=(800, 800))
        ai_manager = AIManager()
        product_name_english = ai_manager.translate_hebrew_query(search_query)
        products = AliExpressApi().process(product_name_english, 49)
        products_df = ProductsTransform().transform_to_table(products)
        if len(products_df) == 0:
            return [], "no image found"
        products_df_rank = getRank().sort_by_volume(products_df)
        products_df_filtered_by_title = ai_manager.get_suitable_titles(product_name_english, products_df_rank)
        if len(products_df) == 0:
            return [], "no image found"
        products_df_detailed = AliExpressApiProducts().process(products_df_filtered_by_title)
        image_base_64 = creator.save_grid(products_df_detailed)
        selected_columns = [
            "target_sale_price",
            "avg_evaluation_rating",
            "sales_count",
            "evaluation_count",
            "subject"
        ]
        filtered_df = products_df_detailed[selected_columns].copy()
        products_list = filtered_df.to_dict(orient="records")
        if logs_flag:
            pretty_print_df(products_df_detailed)
            print("\n" + "=" * 50)
            print("AI USAGE STATISTICS")
            print("=" * 50)
            print(f"Input tokens: {ai_manager.total_tokens_used['prompt_tokens']}")
            print(f"Output tokens: {ai_manager.total_tokens_used['completion_tokens']}")
            print(f"Total runtime: {ai_manager.total_runtime:.3f}s")
            input_cost = ai_manager.total_tokens_used['prompt_tokens'] * 0.0001 / 1000
            output_cost = ai_manager.total_tokens_used['completion_tokens'] * 0.0004 / 1000
            total_cost = input_cost + output_cost
            print(f"Estimated cost: ${total_cost:.6f}")
            print("=" * 50)
        return products_list, image_base_64

if __name__ == "__main__":
    products_list, image_base_64 = MainProducts().process("חפש לי jbl flip 6", True)
    print(products_list)