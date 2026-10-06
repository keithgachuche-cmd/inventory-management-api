# conftest.py
import copy

import pytest

import data
from app import app as flask_app

ORIGINAL_INVENTORY = copy.deepcopy(data.inventory)
ORIGINAL_NEXT_ID = data.next_id


@pytest.fixture
def client():
    """A Flask test client with fresh data for every test."""
    data.inventory[:] = copy.deepcopy(ORIGINAL_INVENTORY)
    data.next_id = ORIGINAL_NEXT_ID
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as test_client:
        yield test_client