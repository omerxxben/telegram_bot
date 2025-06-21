import json

from ali_epress_api_products import AliExpressApiProducts
from general_tools import pretty_print_df
from ali_epress_api import AliExpressApi
from products_transform import ProductsTransform

if __name__ == "__main__":
    #print(json.dumps(products, indent=4, ensure_ascii=False))
    product_name = ("BOLBOL")
    products = AliExpressApi().process(product_name, 10)
    #print(json.dumps(products, indent=4, ensure_ascii=False))
    products_df = ProductsTransform().transform_to_table(products)
    products_df_detailed = AliExpressApiProducts().process(products_df)
    pretty_print_df(products_df_detailed)


