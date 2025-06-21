from ali_epress_api_products import AliExpressApiProducts
from general_tools import pretty_print_df
from ali_epress_api import AliExpressApi
from get_rank import getRank
from image_grid_creator import ImageGridCreator
from products_transform import ProductsTransform

if __name__ == "__main__":
    #print(json.dumps(products, indent=4, ensure_ascii=False))
    product_name = ("tennis ball")
    products = AliExpressApi().process(product_name, 10)
    #print(json.dumps(products, indent=4, ensure_ascii=False))
    products_df = ProductsTransform().transform_to_table(products)
    products_df_detailed = AliExpressApiProducts().process(products_df)
    products_df_rank = getRank().calculate(products_df_detailed)
    #products_df_relevant = CheckRelevant().check(products_df_rank)
    creator = ImageGridCreator(grid_size=(800, 600))
    urls = [
        "https://ae-pic-a1.aliexpress-media.com/kf/Sb1dc4ea309384a7a807cd0a6b8b2f8845.jpg",
        "https://ae-pic-a1.aliexpress-media.com/kf/HTB1mEK0fBUSMeJjy1zjq6A0dXXak.jpg",
        "https://ae-pic-a1.aliexpress-media.com/kf/S808417db5f8249488b13a521d251644bA.jpg",
        "https://ae-pic-a1.aliexpress-media.com/kf/S3f3aceb465a84688889de26fed16989fT.jpeg"
    ]

    result_image = creator.save_grid(urls, f"""C:\\Users\\User\\Desktop\\images""")
    pretty_print_df(products_df_rank)


