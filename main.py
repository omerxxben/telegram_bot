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
        response =  MainProducts().process(search_query)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)