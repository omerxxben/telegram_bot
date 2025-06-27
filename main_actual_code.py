import json
from PIL import Image
from IPython.display import display

from Classes.ale_express_api_short_link import AliExpressApiShortLink
from Classes.ali_epress_api_products import AliExpressApiProducts
from Classes.general_tools import pretty_print_df
from Classes.ali_epress_api import AliExpressApi
from Classes.get_rank import getRank
from Classes.image_grid_creator import ImageGridCreator
from Classes.products_transform import ProductsTransform
from Classes.ai_manager import AIManager


class MainProducts:
    def process(self, search_query, IS_LOGS = False, IS_PRINT_IMAGE = False):
        creator = ImageGridCreator(grid_size=(800, 800))
        ai_manager = AIManager()
        product_name_english = ai_manager.translate_hebrew_query(search_query)
        products = AliExpressApi().process(product_name_english, 50)
        products_df = ProductsTransform().transform_to_table(products)
        if len(products_df) == 0:
            return []
        products_df_rank = getRank().sort_by_volume(products_df)
        products_df_filtered_by_title = ai_manager.get_suitable_titles(product_name_english, products_df_rank)
        if len(products_df_filtered_by_title) == 0:
            return []
        products_df_detailed = AliExpressApiProducts().process(products_df_filtered_by_title)
        products_df_detailed = AliExpressApiShortLink().process(products_df_detailed)
        image_bytes_io = creator.save_grid(products_df_detailed, IS_PRINT_IMAGE)
        selected_columns = [
            "target_sale_price",
            "avg_evaluation_rating",
            "sales_count",
            "evaluation_count",
            "subject",
            "promotion_link"
        ]
        filtered_df = products_df_detailed[selected_columns].copy()
        products_list = filtered_df.to_dict(orient="records")
        if IS_LOGS:
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
        transformed_products = [ProductsTransform().transform_product_names(product) for product in products_list]
        number_of_products = len(transformed_products)
        response = {
            "number_of_products": number_of_products,
            "image_bytes_io": image_bytes_io,
            "products_list": transformed_products
        }
        return response

if __name__ == "__main__":
    response = MainProducts().process("חפש לי מטען", True, True)
    print(response)
    #print(json.dumps(response, indent=2, ensure_ascii=False))
    #print(products_list)