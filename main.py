import json
from ali_epress_api_products import AliExpressApiProducts
from general_tools import pretty_print_df
from ali_epress_api import AliExpressApi
from get_rank import getRank
from image_grid_creator import ImageGridCreator
from products_transform import ProductsTransform
from ai_manager import AIManager

if __name__ == "__main__":
    OUTPUT_PATH = r"C:\Users\User\OneDrive\שולחן העבודה\images\grid.jpg"
    #OUTPUT_PATH = r"C:\Users\User\Desktop\images\grid.jpg"
    creator = ImageGridCreator(grid_size=(800, 800))

    ai_manager = AIManager()
    search_query = "חפש לי שלט לפלייסטישן 5"
    product_name_english = ai_manager.translate_hebrew_query(search_query)
    products = AliExpressApi().process(product_name_english,  49)
    products_df = ProductsTransform().transform_to_table(products)
    if len(products_df) == 0:
        result_image = creator.save_grid(products_df, OUTPUT_PATH)
        print("didnt find products")
    products_df_rank = getRank().sort_by_volume(products_df)
    products_df_filtered_by_title = ai_manager.get_suitable_titles(product_name_english, products_df_rank)
    products_df_detailed = AliExpressApiProducts().process(products_df_filtered_by_title)
    pretty_print_df(products_df_detailed)
    result_image = creator.save_grid(products_df_detailed, OUTPUT_PATH)
    print("\n" + "="*50)
    print("AI USAGE STATISTICS")
    print("="*50)
    print(f"Input tokens: {ai_manager.total_tokens_used['prompt_tokens']}")
    print(f"Output tokens: {ai_manager.total_tokens_used['completion_tokens']}")
    print(f"Total runtime: {ai_manager.total_runtime:.3f}s")
    input_cost = ai_manager.total_tokens_used['prompt_tokens'] * 0.0001 / 1000
    output_cost = ai_manager.total_tokens_used['completion_tokens'] * 0.0004 / 1000
    total_cost = input_cost + output_cost
    print(f"Estimated cost: ${total_cost:.6f}")
    print("="*50)


