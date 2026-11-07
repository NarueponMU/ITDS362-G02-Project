"""Shared fixtures for the WooCommerce Store API test suites (Group 02, ITDS362).

Every test that touches the cart gets its own brand-new Cart-Token from the
`cart` fixture, so no test depends on another test, on run order, or on a
cart that another group could change.
"""
import os

import pytest
import requests

BASE_URL = os.environ.get(
    "STORE_API_URL", "http://157.85.104.96/shop/wp-json/wc/store/v1"
).rstrip("/")
TIMEOUT = 30

# Sample products from the demo catalog. Tests read their price from the API at
# run time instead of hard-coding it.
SIMPLE_PRODUCT_ID = 15      # Belt (simple, purchasable)
SECOND_PRODUCT_ID = 16      # Cap (simple, purchasable)
VARIABLE_PRODUCT_ID = 11    # Hoodie (variable: needs a size/colour)
EXTERNAL_PRODUCT_ID = 33    # WordPress Pennant (external: not purchasable here)
GROUPED_PRODUCT_ID = 32     # Logo Collection (grouped: not purchasable directly)
MAX_QUANTITY = 9999         # add_to_cart.maximum reported by the API


class StoreCart:
    """One shopper's cart, identified by its own Cart-Token."""

    def __init__(self, session):
        self.session = session
        r = session.get(f"{BASE_URL}/cart", timeout=TIMEOUT)
        r.raise_for_status()
        self.token = r.headers["Cart-Token"]
        self.nonce = r.headers.get("Nonce", "")

    def post(self, path, body, with_token=True):
        headers = {"Content-Type": "application/json"}
        if with_token:
            headers["Cart-Token"] = self.token
            headers["Nonce"] = self.nonce
        r = self.session.post(f"{BASE_URL}{path}", json=body, headers=headers, timeout=TIMEOUT)
        self.nonce = r.headers.get("Nonce", self.nonce)
        return r

    def add_item(self, body, with_token=True):
        return self.post("/cart/add-item", body, with_token)

    def update_item(self, body):
        return self.post("/cart/update-item", body)


@pytest.fixture
def session():
    with requests.Session() as s:
        yield s


@pytest.fixture
def cart(session):
    """A fresh, empty cart that belongs to this test only."""
    return StoreCart(session)


@pytest.fixture
def get_product(session):
    """Read one product from the Store API (used to compute expected totals)."""

    def _get(product_id):
        r = session.get(f"{BASE_URL}/products/{product_id}", timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()

    return _get


@pytest.fixture
def all_products(session):
    """The whole catalog, used as the oracle for filter and sort tests."""
    r = session.get(f"{BASE_URL}/products", params={"per_page": 100}, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()


def price_of(product):
    """Current price in the smallest currency unit (satang), as an int."""
    return int(product["prices"]["price"])
