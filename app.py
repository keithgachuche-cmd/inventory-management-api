# app.py
from flask import Flask, jsonify
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


if __name__ == "__main__":
    app.run(debug=True)