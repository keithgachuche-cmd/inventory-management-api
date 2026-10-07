# Inventory Management System

A Flask REST API for managing retail inventory, with a command-line interface and OpenFoodFacts integration for looking up product details by barcode or name.

## Features

- REST API with full CRUD operations on an in-memory inventory
- Product lookup from the OpenFoodFacts API (by barcode or name)
- CLI tool to manage inventory without writing HTTP requests
- Unit tests with pytest and unittest.mock

## Project Structure

```
inventory-management-api/
├── app.py            # Flask API routes
├── cli.py            # Command-line interface
├── data.py           # Mock database (in-memory array)
├── conftest.py       # pytest fixtures
├── tests/
│   ├── test_api.py   # API endpoint tests
│   └── test_cli.py   # CLI tests
├── requirements.txt
└── README.md
```

## Installation and Setup

1. Clone the repository:
```bash
   git clone https://github.com/keithgachuche-cmd/inventory-management-api.git
   cd inventory-management-api
```
2. Create and activate a virtual environment:
```bash
   python -m venv venv
   source venv/bin/activate      # Windows: venv\Scripts\activate
```
3. Install dependencies:
```bash
   python -m pip install -r requirements.txt
```
4. Start the API server:
```bash
   python app.py
```
   The API runs at `http://127.0.0.1:5000`.

## API Endpoints

| Method | Endpoint | Description | Success | Errors |
|---|---|---|---|---|
| GET | `/inventory` | List all items | 200 | |
| GET | `/inventory/<id>` | Get one item | 200 | 404 |
| POST | `/inventory` | Add an item (`product_name` required) | 201 | 400 |
| PATCH | `/inventory/<id>` | Update item fields (e.g. price, stock) | 200 | 400, 404 |
| DELETE | `/inventory/<id>` | Remove an item | 200 | 404 |
| GET | `/lookup?barcode=...` or `?name=...` | Fetch product details from OpenFoodFacts (does not save) | 200 | 400, 404, 502 |

### Item format

```json
{
  "id": 1,
  "barcode": "5449000000996",
  "product_name": "Coca-Cola Original",
  "brands": "Coca-Cola",
  "ingredients_text": "Carbonated water, sugar, ...",
  "price": 1.99,
  "stock": 40
}
```

## CLI Usage

Keep the server running in one terminal, and use the CLI in a second terminal.

```bash
python cli.py list                                   # list all items
python cli.py view 2                                 # view one item
python cli.py add "Test Cereal" --brand Kellogg --price 2.5 --stock 10
python cli.py update 1 --price 2.49 --stock 35       # update price and/or stock
python cli.py delete 3                               # delete an item
python cli.py lookup --barcode 3017620422003         # find on OpenFoodFacts
python cli.py lookup --name nutella
python cli.py lookup --barcode 3017620422003 --save --price 4.99 --stock 12   # find and add to inventory
```

## Running the Tests

```bash
python -m pytest -v
```

The tests use Flask's test client and `unittest.mock`, so they run offline and do not need the server running.

## Notes and Limitations

- Data is stored in memory, so it resets every time the server restarts.
- The API does not check for duplicate barcodes.
- Name searches on OpenFoodFacts can be slow; barcode lookup is more reliable.

## Data Source

Product data comes from [OpenFoodFacts](https://world.openfoodfacts.org/).
