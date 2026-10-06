# app.py
from flask import Flask, jsonify, request
import requests
import data

app = Flask(__name__)

OFF_BASE_URL = "https://world.openfoodfacts.org"
OFF_HEADERS = {"User-Agent": "InventoryLab/1.0 (student project)"}


def find_item(item_id):
    """Return the item with the given ID, or None if it doesn't exist."""
    for item in data.inventory:
        if item["id"] == item_id:
            return item
    return None


def clean_product(product):
    """Pick out the fields we care about from an OpenFoodFacts product."""
    return {
        "barcode": product.get("code", ""),
        "product_name": product.get("product_name", "Unknown"),
        "brands": product.get("brands", ""),
        "ingredients_text": product.get("ingredients_text", ""),
    }


@app.route("/inventory", methods=["GET"])
def get_all_items():
    return jsonify(data.inventory), 200


@app.route("/inventory/<int:item_id>", methods=["GET"])
def get_item(item_id):
    item = find_item(item_id)
    if item is None:
        return jsonify({"error": "Item not found"}), 404
    return jsonify(item), 200


@app.route("/inventory", methods=["POST"])
def add_item():
    body = request.get_json(silent=True)
    if not body or "product_name" not in body:
        return jsonify({"error": "product_name is required"}), 400

    new_item = {
        "id": data.next_id,
        "barcode": body.get("barcode", ""),
        "product_name": body["product_name"],
        "brands": body.get("brands", ""),
        "ingredients_text": body.get("ingredients_text", ""),
        "price": body.get("price", 0.0),
        "stock": body.get("stock", 0),
    }
    data.inventory.append(new_item)
    data.next_id += 1
    return jsonify(new_item), 201


@app.route("/inventory/<int:item_id>", methods=["PATCH"])
def update_item(item_id):
    item = find_item(item_id)
    if item is None:
        return jsonify({"error": "Item not found"}), 404

    body = request.get_json(silent=True)
    if not body:
        return jsonify({"error": "Request body must be JSON"}), 400

    # Only allow updating fields that already exist, and never the id.
    for key, value in body.items():
        if key in item and key != "id":
            item[key] = value
    return jsonify(item), 200


@app.route("/inventory/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    item = find_item(item_id)
    if item is None:
        return jsonify({"error": "Item not found"}), 404

    data.inventory.remove(item)
    return jsonify({"message": f"Item {item_id} deleted"}), 200


@app.route("/lookup", methods=["GET"])
def lookup_product():
    barcode = request.args.get("barcode")
    name = request.args.get("name")

    if not barcode and not name:
        return jsonify({"error": "Provide a barcode or name"}), 400

    try:
        if barcode:
            url = f"{OFF_BASE_URL}/api/v2/product/{barcode}.json"
            response = requests.get(url, headers=OFF_HEADERS, timeout=10)
            response.raise_for_status()
            result = response.json()
            if result.get("status") != 1:
                return jsonify({"error": "Product not found"}), 404
            return jsonify(clean_product(result["product"])), 200

        url = f"{OFF_BASE_URL}/cgi/search.pl"
        params = {
            "search_terms": name,
            "search_simple": 1,
            "json": 1,
            "page_size": 1,
        }
        response = requests.get(url, params=params, headers=OFF_HEADERS, timeout=10)
        response.raise_for_status()
        products = response.json().get("products", [])
        if not products:
            return jsonify({"error": "Product not found"}), 404
        return jsonify(clean_product(products[0])), 200

    except requests.exceptions.RequestException:
        return jsonify({"error": "Could not reach OpenFoodFacts"}), 502


if __name__ == "__main__":
    app.run(debug=True)