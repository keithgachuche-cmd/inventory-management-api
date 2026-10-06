# data.py
# Simulated database: a list of dictionaries that mimics OpenFoodFacts-style data.

inventory = [
    {
        "id": 1,
        "barcode": "5449000000996",
        "product_name": "Coca-Cola Original",
        "brands": "Coca-Cola",
        "ingredients_text": "Carbonated water, sugar, colour (caramel E150d), phosphoric acid, natural flavourings",
        "price": 1.99,
        "stock": 40,
    },
    {
        "id": 2,
        "barcode": "3017620422003",
        "product_name": "Nutella",
        "brands": "Ferrero",
        "ingredients_text": "Sugar, palm oil, hazelnuts, skimmed milk powder, cocoa, lecithin, vanillin",
        "price": 4.49,
        "stock": 25,
    },
    {
        "id": 3,
        "barcode": "0000000000003",
        "product_name": "Organic Almond Milk",
        "brands": "Silk",
        "ingredients_text": "Filtered water, almonds, cane sugar, sea salt",
        "price": 3.99,
        "stock": 18,
    },
]

# Tracks the next ID to assign so IDs are never reused after a delete.
next_id = 4