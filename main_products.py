from flask import Flask, request, jsonify
from ali_epress_api_products import AliExpressApiProducts
from general_tools import pretty_print_df
from ali_epress_api import AliExpressApi
from get_rank import getRank
from image_grid_creator import ImageGridCreator
from products_transform import ProductsTransform
from ai_manager import AIManager


class MainProducts:
    def process(self, search_query):
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
            "product_title"
        ]
        filtered_df = products_df_detailed[selected_columns].copy()
        products_list = filtered_df.to_dict(orient="records")
        return products_list, image_base_64

if __name__ == "__main__":
    products_list, image_base_64 = MainProducts().process("חפש לי jbl flip 6")
    print(products_list)