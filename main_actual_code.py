import time
from Classes.ale_express_api_short_link import AliExpressApiShortLink
from Classes.ali_epress_api_products import AliExpressApiProducts
from Classes.ali_epress_api import AliExpressApi
from Classes.get_rank import getRank
from Classes.image_grid_creator import ImageGridCreator
from Classes.logger import Logger
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
        transformed_products = [
            ProductsTransform().transform_product_names(product) for product in products_list
        ]
        if IS_LOGS:
            timings['total'] = time.time() - start_time
            Logger().ali_express_log( search_query, product_name_english, products_df_detailed, self.ai_manager, timings,
            )
        return {
            "image_bytes_io": image_bytes_io,
            "products_list": transformed_products,
        }
if __name__ == "__main__":
    response = MainProducts().process("מטען", True, True)
    #print(response)
    #print(json.dumps(response, indent=2, ensure_ascii=False))
    #print(products_list)