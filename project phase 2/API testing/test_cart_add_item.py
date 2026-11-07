"""Test suite 2: POST /cart/add-item (Store API) - put a product into the cart.

This operation changes data (the shopper's cart). Every test uses its own new
cart from the `cart` fixture.

Input space partitioning (details in README.md):
  C1 product id : simple product | non-existent id | id 0 | missing id |
                  variable product | external product | grouped product
  C2 quantity   : missing (default 1) | 1 (min) | typical (3) | 9999 (max) |
                  0 | negative | 10000 (above max) | decimal | non-numeric
  C3 Cart-Token : valid token | no token
"""
import pytest

from conftest import (
    EXTERNAL_PRODUCT_ID,
    GROUPED_PRODUCT_ID,
    MAX_QUANTITY,
    SIMPLE_PRODUCT_ID,
    VARIABLE_PRODUCT_ID,
    price_of,
)


def assert_single_line(body, product, quantity):
    """The cart holds exactly one line of `product` with the right quantity and totals."""
    assert len(body["items"]) == 1
    line = body["items"][0]
    assert line["id"] == product["id"]
    assert line["name"] == product["name"]
    assert line["quantity"] == quantity
    assert int(line["totals"]["line_total"]) == price_of(product) * quantity
    assert body["items_count"] == quantity
    assert int(body["totals"]["total_price"]) == price_of(product) * quantity
    assert body["totals"]["currency_code"] == "THB"


# ---------------------------------------------------------------- valid quantities (C1 simple, C3 valid)

# Goal: valid quantities (min 1, typical 3, max 9999) add exactly that many and the total is price x quantity.
@pytest.mark.parametrize("quantity", [1, 3, MAX_QUANTITY], ids=["C2-min-1", "C2-typical-3", "C2-max-9999"])
def test_add_simple_product_with_valid_quantity(cart, get_product, quantity):
    product = get_product(SIMPLE_PRODUCT_ID)
    r = cart.add_item({"id": SIMPLE_PRODUCT_ID, "quantity": quantity})
    assert r.status_code == 201
    assert_single_line(r.json(), product, quantity)


# Goal: when quantity is left out the API uses its default of 1.
def test_add_without_quantity_defaults_to_one(cart, get_product):
    product = get_product(SIMPLE_PRODUCT_ID)
    r = cart.add_item({"id": SIMPLE_PRODUCT_ID})
    assert r.status_code == 201
    assert_single_line(r.json(), product, 1)


# Goal: adding the same product twice merges into one line with the summed quantity.
def test_add_same_product_twice_merges_lines(cart, get_product):
    product = get_product(SIMPLE_PRODUCT_ID)
    assert cart.add_item({"id": SIMPLE_PRODUCT_ID, "quantity": 1}).status_code == 201
    r = cart.add_item({"id": SIMPLE_PRODUCT_ID, "quantity": 2})
    assert r.status_code == 201
    assert_single_line(r.json(), product, 3)


# ---------------------------------------------------------------- invalid quantities (C2)

# Goal: zero or negative quantities are rejected with 400 and the cart stays empty.
@pytest.mark.parametrize("quantity", [0, -1], ids=["C2-zero", "C2-negative"])
def test_add_with_non_positive_quantity_is_rejected(cart, quantity):
    r = cart.add_item({"id": SIMPLE_PRODUCT_ID, "quantity": quantity})
    assert r.status_code == 400
    assert r.json()["code"] == "woocommerce_rest_product_invalid_quantity"


# Goal: a non-numeric quantity fails schema validation with 400 rest_invalid_param.
def test_add_with_non_numeric_quantity_is_rejected(cart):
    r = cart.add_item({"id": SIMPLE_PRODUCT_ID, "quantity": "abc"})
    assert r.status_code == 400
    body = r.json()
    assert body["code"] == "rest_invalid_param"
    assert "quantity" in body["data"]["params"]


# Goal: a quantity above the maximum (9999) is rejected with 400, the same way update-item rejects it.
def test_add_with_quantity_above_max_is_rejected(cart):
    r = cart.add_item({"id": SIMPLE_PRODUCT_ID, "quantity": MAX_QUANTITY + 1})
    assert r.status_code == 400
    assert r.json()["code"] in ("invalid_quantity", "woocommerce_rest_product_invalid_quantity")


# Goal: a decimal quantity is not a whole number of items, so it is rejected with 400.
def test_add_with_decimal_quantity_is_rejected(cart):
    r = cart.add_item({"id": SIMPLE_PRODUCT_ID, "quantity": 2.5})
    assert r.status_code == 400
    assert "code" in r.json()


# ---------------------------------------------------------------- invalid products (C1)

# Goal: ids that do not point to a product are rejected with 400 woocommerce_rest_cart_invalid_product.
@pytest.mark.parametrize(
    "body",
    [{"id": 999999, "quantity": 1}, {"id": 0, "quantity": 1}, {"quantity": 1}],
    ids=["C1-non-existent", "C1-zero-id", "C1-missing-id"],
)
def test_add_invalid_product_id_is_rejected(cart, body):
    r = cart.add_item(body)
    assert r.status_code == 400
    data = r.json()
    assert data["code"] == "woocommerce_rest_cart_invalid_product"
    assert data["data"]["status"] == 400


# Goal: a variable product cannot be added without choosing its attributes (size/colour).
def test_add_variable_product_without_attributes_is_rejected(cart):
    r = cart.add_item({"id": VARIABLE_PRODUCT_ID, "quantity": 1})
    assert r.status_code == 400
    assert r.json()["code"] == "woocommerce_rest_missing_attributes"


# Goal: external and grouped products are not purchasable through the cart.
@pytest.mark.parametrize("product_id", [EXTERNAL_PRODUCT_ID, GROUPED_PRODUCT_ID], ids=["C1-external", "C1-grouped"])
def test_add_non_purchasable_product_is_rejected(cart, product_id):
    r = cart.add_item({"id": product_id, "quantity": 1})
    assert r.status_code == 400
    assert r.json()["code"] == "woocommerce_rest_product_not_purchasable"


# ---------------------------------------------------------------- Cart-Token (C3)

# Goal: without a Cart-Token (and Nonce) the request is refused with 401.
def test_add_without_cart_token_is_unauthorized(cart):
    r = cart.add_item({"id": SIMPLE_PRODUCT_ID, "quantity": 1}, with_token=False)
    assert r.status_code == 401
    assert r.json()["code"] == "woocommerce_rest_missing_nonce"
