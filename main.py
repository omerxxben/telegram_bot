import json
from ali_epress_api_products import AliExpressApiProducts
from general_tools import pretty_print_df
from ali_epress_api import AliExpressApi
from get_rank import getRank
from image_grid_creator import ImageGridCreator
from products_transform import ProductsTransform
from ai_manager import AIManager

if __name__ == "__main__":
    #OUTPUT_PATH = r"C:\Users\User\OneDrive\שולחן העבודה\images\grid.jpg"
    OUTPUT_PATH = r"C:\Users\User\Desktop\images\grid.jpg"
    #print(json.dumps(products, indent=4, ensure_ascii=False))
    
    # Initialize AI manager once to track cumulative stats
    ai_manager = AIManager()
    
    search_query = "חפש לי jbl flip 6"
    product_name_english = ai_manager.translate_hebrew_query(search_query)
    
    products = AliExpressApi().process(product_name_english,  50)
    products_df = ProductsTransform().transform_to_table(products)
    products_df_rank = getRank().sort_by_volume(products_df)
    #pretty_print_df(products_df_rank)
    
    products_df_filtered_by_title = ai_manager.get_suitable_titles(product_name_english, products_df_rank)
    pretty_print_df(products_df_filtered_by_title)
    
    products_df_detailed = AliExpressApiProducts().process(products_df_filtered_by_title)
    #products_df_rank = getRank().calculate(products_df_detailed)
    #creator = ImageGridCreator(grid_size=(800, 800))
    #result_image = creator.save_grid(products_df_rank, OUTPUT_PATH)
    
    # Print AI usage statistics
    print("\n" + "="*50)
    print("AI USAGE STATISTICS")
    print("="*50)
    print(f"Input tokens: {ai_manager.total_tokens_used['prompt_tokens']}")
    print(f"Output tokens: {ai_manager.total_tokens_used['completion_tokens']}")
    print(f"Total runtime: {ai_manager.total_runtime:.3f}s")
    
    # Calculate cost
    input_cost = ai_manager.total_tokens_used['prompt_tokens'] * 0.0001 / 1000
    output_cost = ai_manager.total_tokens_used['completion_tokens'] * 0.0004 / 1000
    total_cost = input_cost + output_cost
    print(f"Estimated cost: ${total_cost:.6f}")
    print("="*50)


