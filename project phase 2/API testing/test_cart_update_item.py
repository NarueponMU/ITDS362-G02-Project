"""Test suite 3: POST /cart/update-item (Store API) - change the quantity of a cart line.

This operation changes data (the shopper's cart). Every test first builds its
own cart holding 2 x Cap, so it never depends on another test.

Input space partitioning (details in README.md):
  C1 item key : key of an item in this cart | key that does not exist | missing key
  C2 quantity : increase (5) | decrease to min (1) | max (9999) | missing (no change) |
                0 | negative | 10000 (above max) | decimal | non-numeric
"""
import pytest

from conftest import MAX_QUANTITY, SECOND_PRODUCT_ID, price_of

START_QUANTITY = 2


@pytest.fixture
def cart_with_item(cart, get_product):
    """A new cart with 2 x Cap. Returns (cart, product, item key)."""
    product = get_product(SECOND_PRODUCT_ID)
    r = cart.add_item({"id": SECOND_PRODUCT_ID, "quantity": START_QUANTITY})
    assert r.status_code == 201, r.text
    return cart, product, r.json()["items"][0]["key"]


def assert_quantity(body, product, key, quantity):
    """The cart line `key` has `quantity` and totals match price x quantity."""
    assert len(body["items"]) == 1
    line = body["items"][0]
    assert line["key"] == key
    assert line["id"] == product["id"]
    assert line["quantity"] == quantity
    assert int(line["totals"]["line_total"]) == price_of(product) * quantity
    assert body["items_count"] == quantity
    assert int(body["totals"]["total_price"]) == price_of(product) * quantity


# ---------------------------------------------------------------- valid updates

# Goal: valid new quantities (increase to 5, decrease to the min 1, the max 9999) update the line and its total.
@pytest.mark.parametrize("quantity", [5, 1, MAX_QUANTITY], ids=["C2-increase-5", "C2-min-1", "C2-max-9999"])
def test_update_to_valid_quantity(cart_with_item, quantity):
    cart, product, key = cart_with_item
    r = cart.update_item({"key": key, "quantity": quantity})
    assert r.status_code == 200
    assert_quantity(r.json(), product, key, quantity)


# Goal: leaving quantity out changes nothing and the line keeps its old quantity.
def test_update_without_quantity_keeps_quantity(cart_with_item):
    cart, product, key = cart_with_item
    r = cart.update_item({"key": key})
    assert r.status_code == 200
    assert_quantity(r.json(), product, key, START_QUANTITY)


# ---------------------------------------------------------------- invalid quantities (C2)

# Goal: 0, negative or above-max quantities are rejected with 400 invalid_quantity.
@pytest.mark.parametrize(
    "quantity", [0, -3, MAX_QUANTITY + 1], ids=["C2-zero", "C2-negative", "C2-above-max-10000"]
)
def test_update_to_out_of_range_quantity_is_rejected(cart_with_item, quantity):
    cart, _, key = cart_with_item
    r = cart.update_item({"key": key, "quantity": quantity})
    assert r.status_code == 400
    body = r.json()
    assert body["code"] == "invalid_quantity"
    assert body["data"]["status"] == 400


# Goal: a non-numeric quantity fails schema validation with 400 rest_invalid_param.
def test_update_to_non_numeric_quantity_is_rejected(cart_with_item):
    cart, _, key = cart_with_item
    r = cart.update_item({"key": key, "quantity": "two"})
    assert r.status_code == 400
    assert r.json()["code"] == "rest_invalid_param"


# Goal: a decimal quantity is not a whole number of items, so it is rejected with 400.
def test_update_to_decimal_quantity_is_rejected(cart_with_item):
    cart, _, key = cart_with_item
    r = cart.update_item({"key": key, "quantity": 2.7})
    assert r.status_code == 400
    assert "code" in r.json()


# ---------------------------------------------------------------- invalid keys (C1)

# Goal: a key that is not in this cart, or no key at all, is refused with 409 woocommerce_rest_cart_invalid_key.
@pytest.mark.parametrize(
    "body",
    [{"key": "0" * 28 + "dead", "quantity": 3}, {"quantity": 3}],
    ids=["C1-non-existent-key", "C1-missing-key"],
)
def test_update_with_invalid_key_is_rejected(cart_with_item, body):
    cart, _, _ = cart_with_item
    r = cart.update_item(body)
    assert r.status_code == 409
    assert r.json()["code"] == "woocommerce_rest_cart_invalid_key"


# Goal: a key from another shopper's cart cannot change this cart (carts are isolated).
def test_update_with_key_from_another_cart_is_rejected(cart_with_item, session):
    from conftest import StoreCart

    _, _, key = cart_with_item
    other = StoreCart(session.__class__())
    r = other.update_item({"key": key, "quantity": 3})
    assert r.status_code == 409
    assert r.json()["code"] == "woocommerce_rest_cart_invalid_key"
