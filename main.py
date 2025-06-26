from flask import Flask, request, jsonify
from ali_epress_api_products import AliExpressApiProducts
from general_tools import pretty_print_df
from ali_epress_api import AliExpressApi
from get_rank import getRank
from image_grid_creator import ImageGridCreator
from products_transform import ProductsTransform
from ai_manager import AIManager
app = Flask(__name__)


@app.route("/get-cost", methods=["GET"])
def get_cost():
    try:
        creator = ImageGridCreator(grid_size=(800, 800))
        ai_manager = AIManager()
        search_query = request.args.get("product_name", "חפש לי שלט לפלייסטישן 5")
        product_name_english = ai_manager.translate_hebrew_query(search_query)
        products = AliExpressApi().process(product_name_english, 49)
        products_df = ProductsTransform().transform_to_table(products)
        if len(products_df) == 0:
            image = creator.save_grid(products_df)
            return jsonify({"message": "No products found", "total_cost": 0.0})
        products_df_rank = getRank().sort_by_volume(products_df)
        products_df_filtered_by_title = ai_manager.get_suitable_titles(product_name_english, products_df_rank)
        products_df_detailed = AliExpressApiProducts().process(products_df_filtered_by_title)
        image = creator.save_grid(products_df_detailed)
        selected_columns = [
            "target_sale_price",
            "avg_evaluation_rating",
            "sales_count",
            "evaluation_count",
            "product_title"
        ]
        filtered_df = products_df_detailed[selected_columns].copy()
        products_list = filtered_df.to_dict(orient="records")
        return jsonify({
            "message": "Success",
            "products": products_list,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
