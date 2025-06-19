import json
from ali_epress_api import AliExpressApi
from products_transform import ProductsTransform

if __name__ == "__main__":
    product_name = "coat"
    products = AliExpressApi().process(product_name)
    #print(json.dumps(products, indent=4, ensure_ascii=False))
    table = ProductsTransform.transform_to_table(products)
    print("DataFrame:")
    print(table)
    print("\n" + "=" * 50 + "\n")
