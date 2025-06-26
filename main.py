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
        OUTPUT_PATH = "images/grid.jpg"  # must exist or be created on Render
        creator = ImageGridCreator(grid_size=(800, 800))
        ai_manager = AIManager()

        # Get Hebrew query from query parameter or use default
        search_query = request.args.get("query", "חפש לי שלט לפלייסטישן 5")
        product_name_english = ai_manager.translate_hebrew_query(search_query)

        products = AliExpressApi().process(product_name_english, 49)
        products_df = ProductsTransform().transform_to_table(products)

        if len(products_df) == 0:
            creator.save_grid(products_df, OUTPUT_PATH)
            return jsonify({"message": "No products found", "total_cost": 0.0})

        products_df_rank = getRank().sort_by_volume(products_df)
        products_df_filtered_by_title = ai_manager.get_suitable_titles(product_name_english, products_df_rank)
        products_df_detailed = AliExpressApiProducts().process(products_df_filtered_by_title)

        creator.save_grid(products_df_detailed, OUTPUT_PATH)

        # Cost calculation
        input_tokens = ai_manager.total_tokens_used['prompt_tokens']
        output_tokens = ai_manager.total_tokens_used['completion_tokens']
        input_cost = input_tokens * 0.0001 / 1000
        output_cost = output_tokens * 0.0004 / 1000
        total_cost = input_cost + output_cost

        return jsonify({
            "message": "Success",
            "total_cost": round(total_cost, 6),
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "runtime_seconds": round(ai_manager.total_runtime, 3)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
