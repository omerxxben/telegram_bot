import json

from ali_epress_api_products import AliExpressApiProducts
from general_tools import pretty_print_df
from ali_epress_api import AliExpressApi
from get_rank import getRank
from image_grid_creator import ImageGridCreator
from products_transform import ProductsTransform

if __name__ == "__main__":
    #print(json.dumps(products, indent=4, ensure_ascii=False))
    product_name = "jbl flip 6 speaker"
    products = AliExpressApi().process(product_name, 100)
    products_df = ProductsTransform().transform_to_table(products)
    products_df_detailed = AliExpressApiProducts().process(products_df)

    products_df_rank = getRank().calculate(products_df_detailed)
    #products_df_relevant = CheckRelevant().check(products_df_rank)
    creator = ImageGridCreator(grid_size=(800, 800))
    result_image = creator.save_grid(products_df_rank, r"C:\Users\User\Desktop\images\grid.jpg")
    pretty_print_df(products_df_rank)


