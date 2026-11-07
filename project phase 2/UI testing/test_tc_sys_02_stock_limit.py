"""Automated version of TC-SYS-02 (see System testing/system_test_cases.md).

Staff creates a product with only 3 in stock -> customer cannot buy more than 3,
buys all 3 -> product is out of stock for both sides -> staff cancels the order
and the stock comes back.
"""
from pages import baht

PRICE = 300
STOCK = 3
CUSTOMER = {
    "first_name": "G02",
    "last_name": "Tester",
    "address_1": "99 Test Road",
    "city": "Bangkok",
    "state": "TH-10",
    "postcode": "10200",
    "phone": "0800000002",
}


# Goal: stock limits are enforced on the web page, stock goes to 0 after the order,
# both staff and customer see "Out of stock", and cancelling the order restores the stock.
def test_tc_sys_02_stock_limit_and_cancel_restores_stock(staff, customer, ts):
    product = f"G02 ST02 Limited Cap {ts}"

    # Steps 1-2: staff creates a product with stock tracking, quantity 3
    product_url = staff.create_product(product, PRICE, stock=STOCK)

    # Step 3: customer sees the price and "3 in stock"
    customer.open_product(product_url)
    assert baht(PRICE) in customer.body_text()
    assert customer.stock_text() == f"{STOCK} in stock"

    # Step 4: asking for 5 (more than in stock) is refused; cart stays empty
    message = customer.try_add_invalid_quantity(5)
    assert message != ""
    assert customer.cart_count_label().endswith(": 0")

    # Step 5: add all 3
    notice = customer.add_to_cart(STOCK)
    assert f"{STOCK} × “{product}” have been added to your cart." in notice

    # Step 6: cart total 3 x 300 = 900
    customer.open_cart()
    assert customer.wait_cart_total(baht(900)) == baht(900)

    # Step 7: go BACK to the product page and try to add 1 more -> not enough stock
    customer.d.back()
    notice = customer.add_to_cart(1)
    assert f"we have {STOCK} in stock and you already have {STOCK} in your cart" in notice
    customer.open_cart()
    assert customer.wait_cart_total(baht(900)) == baht(900)

    # Step 8: empty Town / City is rejected at checkout
    customer.proceed_to_checkout()
    customer.fill_billing({**CUSTOMER, "city": "", "email": f"g02.stock.{ts}@example.com"})
    customer.place_order_click()
    assert "Please enter a valid town / city" in customer.validation_errors()

    # Step 9: complete the form and place the order
    customer.fill_billing({**CUSTOMER, "email": f"g02.stock.{ts}@example.com"})
    order_id, confirmation = customer.place_order()
    assert baht(900) in confirmation
    assert str(order_id) in confirmation

    # Step 10: the customer now sees Out of stock and no Add to cart button
    customer.open_product(product_url)
    assert customer.stock_text() == "Out of stock"
    assert not customer.has_add_to_cart()

    # Step 11: staff sees Out of stock (0) in the product list
    assert "Out of stock (0)" in staff.product_stock_label(product)

    # Step 12: staff cancels the order
    staff.open_order(order_id)
    assert staff.order_status() == "wc-processing"
    staff.set_order_status("Cancelled")
    assert staff.order_status() == "wc-cancelled"

    # Step 13: stock is back to 3 for staff
    assert f"In stock ({STOCK})" in staff.product_stock_label(product)

    # Step 14: and for the customer
    customer.open_product(product_url)
    assert customer.stock_text() == f"{STOCK} in stock"
    assert customer.has_add_to_cart()
