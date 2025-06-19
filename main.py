import json

from ali_epress_api_products import AliExpressApiProducts
from general_tools import pretty_print_df
from ali_epress_api import AliExpressApi
from products_transform import ProductsTransform

if __name__ == "__main__":
    product_name = "iphone 16 screen protector"
    products = AliExpressApi().process(product_name, 1)
    print(json.dumps(products, indent=4, ensure_ascii=False))
    products = AliExpressApiProducts().process(products)
    table = ProductsTransform().transform_to_table(products)
    pretty_print_df(table)