# app.py
from flask import Flask, jsonify, request
import data

app = Flask(__name__)


def find_item(item_id):
    """Return the item with the given ID, or None if it doesn't exist."""
    for item in data.inventory:
        if item["id"] == item_id:
            return item
    return None


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


if __name__ == "__main__":
    app.run(debug=True)