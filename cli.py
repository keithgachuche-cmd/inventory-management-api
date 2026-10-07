# cli.py
import argparse
import sys

import requests

API_URL = "http://127.0.0.1:5000"


def api_request(method, path, **kwargs):
    """Send a request to the Flask API. Returns the JSON body, or None on failure."""
    try:
        response = requests.request(method, f"{API_URL}{path}", timeout=15, **kwargs)
    except requests.exceptions.ConnectionError:
        print("Error: cannot connect to the API. Is the server running? (python app.py)")
        return None
    except requests.exceptions.Timeout:
        print("Error: the request timed out. Try again.")
        return None
    except requests.exceptions.RequestException as exc:
        print(f"Error: request failed ({exc})")
        return None

    try:
        body = response.json()
    except ValueError:
        print(f"Error: unexpected response from the API (status {response.status_code})")
        return None

    if not response.ok:
        print(f"Error: {body.get('error', 'Request failed')}")
        return None
    return body


def print_item(item):
    print(f"ID:           {item['id']}")
    print(f"Name:         {item['product_name']}")
    print(f"Brand:        {item['brands']}")
    print(f"Barcode:      {item['barcode']}")
    print(f"Price:        {item['price']}")
    print(f"Stock:        {item['stock']}")
    print(f"Ingredients:  {item['ingredients_text']}")
    print("-" * 40)


def cmd_list(args):
    items = api_request("GET", "/inventory")
    if items is None:
        return 1
    if not items:
        print("Inventory is empty.")
        return 0
    for item in items:
        print(f"[{item['id']}] {item['product_name']} | price: {item['price']} | stock: {item['stock']}")
    return 0


def cmd_view(args):
    item = api_request("GET", f"/inventory/{args.id}")
    if item is None:
        return 1
    print_item(item)
    return 0


def cmd_add(args):
    if args.price < 0 or args.stock < 0:
        print("Error: price and stock cannot be negative.")
        return 1
    payload = {
        "product_name": args.name,
        "brands": args.brand,
        "barcode": args.barcode,
        "price": args.price,
        "stock": args.stock,
    }
    item = api_request("POST", "/inventory", json=payload)
    if item is None:
        return 1
    print("Item added:")
    print_item(item)
    return 0


def cmd_update(args):
    payload = {}
    if args.price is not None:
        payload["price"] = args.price
    if args.stock is not None:
        payload["stock"] = args.stock
    if not payload:
        print("Error: provide --price and/or --stock to update.")
        return 1
    if any(value < 0 for value in payload.values()):
        print("Error: price and stock cannot be negative.")
        return 1
    item = api_request("PATCH", f"/inventory/{args.id}", json=payload)
    if item is None:
        return 1
    print("Item updated:")
    print_item(item)
    return 0


def cmd_delete(args):
    result = api_request("DELETE", f"/inventory/{args.id}")
    if result is None:
        return 1
    print(result["message"])
    return 0


def cmd_lookup(args):
    params = {"barcode": args.barcode} if args.barcode else {"name": args.name}
    product = api_request("GET", "/lookup", params=params)
    if product is None:
        return 1

    print("Found on OpenFoodFacts:")
    print(f"Name:         {product['product_name']}")
    print(f"Brand:        {product['brands']}")
    print(f"Barcode:      {product['barcode']}")
    print(f"Ingredients:  {product['ingredients_text']}")
    print("-" * 40)

    if args.save:
        if args.price < 0 or args.stock < 0:
            print("Error: price and stock cannot be negative.")
            return 1
        product["price"] = args.price
        product["stock"] = args.stock
        item = api_request("POST", "/inventory", json=product)
        if item is None:
            return 1
        print("Saved to inventory:")
        print_item(item)
    else:
        print("Add --save (with --price and --stock) to put it in your inventory.")
    return 0


def build_parser():
    parser = argparse.ArgumentParser(description="Inventory management CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="List all items").set_defaults(func=cmd_list)

    p = sub.add_parser("view", help="View one item")
    p.add_argument("id", type=int)
    p.set_defaults(func=cmd_view)

    p = sub.add_parser("add", help="Add a new item")
    p.add_argument("name")
    p.add_argument("--brand", default="")
    p.add_argument("--barcode", default="")
    p.add_argument("--price", type=float, default=0.0)
    p.add_argument("--stock", type=int, default=0)
    p.set_defaults(func=cmd_add)

    p = sub.add_parser("update", help="Update price and/or stock")
    p.add_argument("id", type=int)
    p.add_argument("--price", type=float)
    p.add_argument("--stock", type=int)
    p.set_defaults(func=cmd_update)

    p = sub.add_parser("delete", help="Delete an item")
    p.add_argument("id", type=int)
    p.set_defaults(func=cmd_delete)

    p = sub.add_parser("lookup", help="Find a product on OpenFoodFacts")
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("--barcode")
    group.add_argument("--name")
    p.add_argument("--save", action="store_true", help="Add the result to inventory")
    p.add_argument("--price", type=float, default=0.0)
    p.add_argument("--stock", type=int, default=0)
    p.set_defaults(func=cmd_lookup)

    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())