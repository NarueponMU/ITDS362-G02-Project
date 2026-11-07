"""Test suite 1: GET /products (Store API) - list, search, filter and sort products.

Input space partitioning (details in README.md):
  C1 search    : matching keyword | different letter case | no match | empty
  C2 price     : valid range | min > max | negative min | non-numeric min
  C3 per_page  : below min (0) | min (1) | max (100) | above max (101)
  C4 orderby   : price asc | price desc | invalid value
  C5 category  : existing category | non-existent category
"""
import pytest

from conftest import BASE_URL, TIMEOUT, price_of


def list_products(session, **params):
    return session.get(f"{BASE_URL}/products", params=params, timeout=TIMEOUT)


def text_of(product):
    return " ".join(
        [product["name"], product.get("description", ""), product.get("short_description", "")]
    ).lower()


# ---------------------------------------------------------------- C1 search

# Goal: a keyword that exists returns only products that contain it, including every sample hoodie.
@pytest.mark.parametrize("keyword", ["hoodie", "HOODIE"], ids=["C1-lowercase", "C1-uppercase"])
def test_search_matching_keyword_returns_only_matching_products(session, keyword):
    r = list_products(session, search=keyword, per_page=100)
    assert r.status_code == 200
    body = r.json()
    assert len(body) > 0
    assert all("hoodie" in text_of(p) for p in body)
    assert {11, 12, 18, 19}.issubset({p["id"] for p in body})
    assert int(r.headers["X-WP-Total"]) == len(body)


# Goal: a keyword that matches nothing returns 200 with an empty list, not an error.
def test_search_no_match_returns_empty_list(session):
    r = list_products(session, search="zzqqxxnotaproduct")
    assert r.status_code == 200
    assert r.json() == []
    assert r.headers["X-WP-Total"] == "0"


# Goal: an empty keyword behaves like no filter and returns the whole catalog.
def test_search_empty_keyword_returns_all_products(session, all_products):
    r = list_products(session, search="", per_page=100)
    assert r.status_code == 200
    assert {p["id"] for p in r.json()} == {p["id"] for p in all_products}


# ---------------------------------------------------------------- C2 price range

# Goal: a valid range returns exactly the products whose price is inside the range (10.00-20.00 THB).
def test_price_range_returns_every_product_in_range(session, all_products):
    low, high = 1000, 2000
    r = list_products(session, min_price=low, max_price=high, per_page=100)
    assert r.status_code == 200
    returned = {p["id"] for p in r.json()}
    expected = {p["id"] for p in all_products if low <= price_of(p) <= high}
    assert all(low <= price_of(p) <= high for p in r.json())
    assert returned == expected


# Goal: min_price greater than max_price is an impossible range, so the list is empty.
def test_price_range_min_greater_than_max_returns_empty(session):
    r = list_products(session, min_price=2000, max_price=1000)
    assert r.status_code == 200
    assert r.json() == []


# Goal: a negative min_price is below every price, so every product should be returned.
def test_price_negative_min_returns_all_products(session, all_products):
    r = list_products(session, min_price=-100, per_page=100)
    assert r.status_code == 200
    assert {p["id"] for p in r.json()} == {p["id"] for p in all_products}


# Goal: a non-numeric min_price is invalid input and must be rejected with 400, not crash the server.
def test_price_non_numeric_min_is_rejected(session):
    r = list_products(session, min_price="abc")
    assert r.status_code == 400
    assert r.json()["code"] == "rest_invalid_param"


# ---------------------------------------------------------------- C3 per_page

# Goal: per_page values inside 1..100 are accepted and the page never has more items than asked for.
@pytest.mark.parametrize("per_page", [1, 100], ids=["C3-min-1", "C3-max-100"])
def test_per_page_valid_boundaries(session, per_page):
    r = list_products(session, per_page=per_page)
    assert r.status_code == 200
    body = r.json()
    total = int(r.headers["X-WP-Total"])
    assert len(body) == min(per_page, total)
    assert int(r.headers["X-WP-TotalPages"]) == -(-total // per_page)


# Goal: per_page just outside 1..100 is rejected with 400 rest_invalid_param.
@pytest.mark.parametrize("per_page", [0, 101], ids=["C3-below-min-0", "C3-above-max-101"])
def test_per_page_invalid_boundaries(session, per_page):
    r = list_products(session, per_page=per_page)
    assert r.status_code == 400
    body = r.json()
    assert body["code"] == "rest_invalid_param"
    assert "per_page" in body["data"]["params"]


# ---------------------------------------------------------------- C4 orderby / order

# Goal: orderby=price returns products sorted by price in the requested direction.
@pytest.mark.parametrize("order", ["asc", "desc"], ids=["C4-price-asc", "C4-price-desc"])
def test_order_by_price_is_sorted(session, order):
    r = list_products(session, orderby="price", order=order, per_page=100, type="simple")
    assert r.status_code == 200
    prices = [price_of(p) for p in r.json()]
    assert prices == sorted(prices, reverse=(order == "desc"))


# Goal: an unknown orderby value is rejected with 400.
def test_order_by_invalid_value_is_rejected(session):
    r = list_products(session, orderby="colour")
    assert r.status_code == 400
    assert r.json()["code"] == "rest_invalid_param"


# ---------------------------------------------------------------- C5 category

# Goal: filtering by an existing category returns only products in that category.
def test_category_existing_returns_only_that_category(session, all_products):
    accessories = 25
    r = list_products(session, category=accessories, per_page=100)
    assert r.status_code == 200
    body = r.json()
    assert len(body) > 0
    assert all(any(c["id"] == accessories for c in p["categories"]) for p in body)
    expected = {p["id"] for p in all_products if any(c["id"] == accessories for c in p["categories"])}
    assert {p["id"] for p in body} == expected


# Goal: a category id that does not exist returns an empty list.
def test_category_non_existent_returns_empty(session):
    r = list_products(session, category=999999)
    assert r.status_code == 200
    assert r.json() == []
