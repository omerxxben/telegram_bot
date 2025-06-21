import json

from ali_epress_api_products import AliExpressApiProducts
from general_tools import pretty_print_df
from ali_epress_api import AliExpressApi
from products_transform import ProductsTransform

if __name__ == "__main__":
    product_name = ("BOLBOL")
    products = AliExpressApi().process(product_name, 5)
    #print(json.dumps(products, indent=4, ensure_ascii=False))
    products_df = ProductsTransform().transform_to_table(products)
    products_df = AliExpressApiProducts().process(products_df)
    pretty_print_df(products_df)

    #print(json.dumps(products, indent=4, ensure_ascii=False))

