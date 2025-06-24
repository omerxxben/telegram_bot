import json
from ali_epress_api_products import AliExpressApiProducts
from category_filter import CategoryFilter
from general_tools import pretty_print_df
from ali_epress_api import AliExpressApi
from get_rank import getRank
from image_grid_creator import ImageGridCreator
from products_transform import ProductsTransform

if __name__ == "__main__":
    #OUTPUT_PATH = r"C:\Users\User\OneDrive\שולחן העבודה\images\grid.jpg"
    OUTPUT_PATH = r"C:\Users\User\Desktop\images\grid.jpg"
    #print(json.dumps(products, indent=4, ensure_ascii=False))
    #product_name_hebrew = "רמקול"
    #product_name_english = Translate.process(product_name_hebrew)
    product_name_english = "playstation 4 controller"
    products = AliExpressApi().process(product_name_english, 50)
    products_df = ProductsTransform().transform_to_table(products)
    products_df_relevant_category = CategoryFilter().filter(products_df, product_name_english)
    products_df_rank = getRank().sort_by_volume(products_df_relevant_category)
    pretty_print_df(products_df_relevant_category)

    #products_df_detailed = AliExpressApiProducts().process(products_df)

    #products_df_rank = getRank().calculate(products_df_detailed)
    #products_df_relevant = CheckRelevant().check(products_df_rank)
    #creator = ImageGridCreator(grid_size=(800, 800))
    #result_image = creator.save_grid(products_df_rank, OUTPUT_PATH)


