from general_tools import pretty_print_df

from ali_epress_api import AliExpressApi
from products_transform import ProductsTransform

if __name__ == "__main__":
    product_name = "coat"
    products = AliExpressApi().process(product_name)
    #print(json.dumps(products, indent=4, ensure_ascii=False))
    table = ProductsTransform().transform_to_table(products)
    pretty_print_df(table)