# tests/test_cli.py
from unittest.mock import MagicMock, patch

import requests

import cli


def fake_response(json_data, ok=True, status_code=200):
    mock = MagicMock()
    mock.json.return_value = json_data
    mock.ok = ok
    mock.status_code = status_code
    return mock


ITEM = {
    "id": 1,
    "barcode": "123",
    "product_name": "Test Item",
    "brands": "Brand",
    "ingredients_text": "stuff",
    "price": 2.5,
    "stock": 10,
}


@patch("cli.requests.request")
def test_list_command(mock_request, capsys):
    mock_request.return_value = fake_response([ITEM])
    assert cli.main(["list"]) == 0
    assert "Test Item" in capsys.readouterr().out


@patch("cli.requests.request")
def test_view_command(mock_request, capsys):
    mock_request.return_value = fake_response(ITEM)
    assert cli.main(["view", "1"]) == 0
    assert "Test Item" in capsys.readouterr().out


@patch("cli.requests.request")
def test_view_not_found(mock_request, capsys):
    mock_request.return_value = fake_response(
        {"error": "Item not found"}, ok=False, status_code=404
    )
    assert cli.main(["view", "99"]) == 1
    assert "Item not found" in capsys.readouterr().out


@patch("cli.requests.request")
def test_add_command(mock_request, capsys):
    mock_request.return_value = fake_response(ITEM)
    assert cli.main(["add", "Test Item", "--price", "2.5", "--stock", "10"]) == 0
    assert mock_request.call_args[0][0] == "POST"
    assert "Item added" in capsys.readouterr().out


def test_add_negative_price(capsys):
    assert cli.main(["add", "Bad", "--price", "-1"]) == 1
    assert "cannot be negative" in capsys.readouterr().out


@patch("cli.requests.request")
def test_update_command(mock_request, capsys):
    mock_request.return_value = fake_response(ITEM)
    assert cli.main(["update", "1", "--price", "3.0"]) == 0
    assert mock_request.call_args[0][0] == "PATCH"


def test_update_requires_a_field(capsys):
    assert cli.main(["update", "1"]) == 1
    assert "provide --price" in capsys.readouterr().out


@patch("cli.requests.request")
def test_delete_command(mock_request, capsys):
    mock_request.return_value = fake_response({"message": "Item 1 deleted"})
    assert cli.main(["delete", "1"]) == 0
    assert mock_request.call_args[0][0] == "DELETE"
    assert "deleted" in capsys.readouterr().out


@patch("cli.requests.request")
def test_lookup_command(mock_request, capsys):
    mock_request.return_value = fake_response(
        {
            "barcode": "3017620422003",
            "product_name": "Nutella",
            "brands": "Ferrero",
            "ingredients_text": "Sugar",
        }
    )
    assert cli.main(["lookup", "--barcode", "3017620422003"]) == 0
    assert "Nutella" in capsys.readouterr().out


@patch("cli.requests.request")
def test_lookup_with_save(mock_request, capsys):
    lookup_result = {
        "barcode": "3017620422003",
        "product_name": "Nutella",
        "brands": "Ferrero",
        "ingredients_text": "Sugar",
    }
    saved_item = dict(lookup_result, id=4, price=4.99, stock=12)
    mock_request.side_effect = [fake_response(lookup_result), fake_response(saved_item)]
    assert cli.main(["lookup", "--barcode", "3017620422003", "--save",
                     "--price", "4.99", "--stock", "12"]) == 0
    assert mock_request.call_count == 2
    assert "Saved to inventory" in capsys.readouterr().out


@patch("cli.requests.request")
def test_server_down(mock_request, capsys):
    mock_request.side_effect = requests.exceptions.ConnectionError()
    assert cli.main(["list"]) == 1
    assert "cannot connect" in capsys.readouterr().out