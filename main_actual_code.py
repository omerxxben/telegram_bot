import json
import time

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
    def process(self, search_query, IS_LOGS=True, IS_PRINT_IMAGE=False):
        self.creator = ImageGridCreator(grid_size=(800, 800))
        self.ai_manager = AIManager()
        start_time = time.time()
        timings = {}

        product_name_english = self.ai_manager.translate_hebrew_query(search_query)
        if not product_name_english:
            print("No product name")
            return []

        products, timings['get_products'] = AliExpressApi().process(product_name_english, 50)
        products_df, timings['transform_table'] = ProductsTransform().transform_to_table(products)

        if products_df.empty:
            print("Didn't find products")
            return []

        ranked_df = getRank().sort_by_volume(products_df)
        filtered_df = self.ai_manager.get_suitable_titles(product_name_english, ranked_df)

        if filtered_df.empty:
            print("Didn't find matching products via AI")
            return []

        products_df_detailed, timings['get_details'] = AliExpressApiProducts().process(filtered_df)
        products_df_detailed, timings['get_short_link'] = AliExpressApiShortLink().process(products_df_detailed)
        image_bytes_io, timings['get_image'] = self.creator.save_grid(products_df_detailed, IS_PRINT_IMAGE)

        selected_columns = [
            "target_sale_price",
            "avg_evaluation_rating",
            "sales_count",
            "evaluation_count",
            "subject",
            "promotion_link",
        ]
        filtered_df = products_df_detailed[selected_columns].copy()
        products_list = filtered_df.to_dict(orient="records")

        if IS_LOGS:
            timings['total'] = time.time() - start_time
            self.log_runtime_and_costs(
                search_query,
                product_name_english,
                products_df_detailed,
                self.ai_manager,
                timings,
            )

        transformed_products = [
            ProductsTransform().transform_product_names(product) for product in products_list
        ]

        return {
            "image_bytes_io": image_bytes_io,
            "products_list": transformed_products,
        }
    def log_runtime_and_costs(self,search_query, product_name_english, products_df_detailed,ai_manager, timings,):
        print(f"product name hebrew: {search_query}")
        print(f"product name english: {product_name_english}")
        pretty_print_df(products_df_detailed)

        print("\n" + "=" * 50)
        print("AI USAGE STATISTICS")
        print("=" * 50)
        print(f"Input tokens: {ai_manager.total_tokens_used['prompt_tokens']}")
        print(f"Output tokens: {ai_manager.total_tokens_used['completion_tokens']}")
        print(f"Total runtime of ai: {ai_manager.total_runtime:.3f}s")
        print(f"Total runtime of get products: {timings['get_products']:.3f}s")
        print(f"Total runtime of transform to table: {timings['transform_table']:.3f}s")
        print(f"Total runtime of get details: {timings['get_details']:.3f}s")
        print(f"Total runtime of get image: {timings['get_image']:.3f}s")
        print(f"Total runtime of get short link: {timings['get_short_link']:.3f}s")
        print(f"Total runtime: {timings['total']:.3f}s")

        input_cost = ai_manager.total_tokens_used['prompt_tokens'] * 0.0001 / 1000
        output_cost = ai_manager.total_tokens_used['completion_tokens'] * 0.0004 / 1000
        total_cost = input_cost + output_cost
        print(f"Estimated cost: ${total_cost:.6f}")
        print("=" * 50)
if __name__ == "__main__":
    response = MainProducts().process("מטען", True, True)
    print(response)
    #print(json.dumps(response, indent=2, ensure_ascii=False))
    #print(products_list)