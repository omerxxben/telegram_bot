import json

from flask import Flask, request, jsonify
from main_actual_code import MainProducts

app = Flask(__name__)


@app.route("/get-cost", methods=["GET"])
def get_cost():
    try:
        search_query = request.args.get("product_name")
        if not search_query:
            return jsonify({"error": "Missing required parameter: product_name"}), 400
        products_list, image_base_64 =  MainProducts().process(search_query)
        if not products_list:
            return jsonify({
            "message": "No products found",
            "image": "No image found",
            "products": [],
            })
        return jsonify({
            "message": "Success",
            "image": image_base_64,
            "products": products_list,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)