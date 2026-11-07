"""Automated version of TC-SYS-03 (see System testing/system_test_cases.md).

Staff creates a product and a 100 THB coupon with a 500 THB minimum spend ->
customer is refused below the minimum, removes an item, raises the quantity,
then uses the coupon -> staff completes the order and sees the coupon was used once.
"""
from pages import baht

PRICE = 200
SAMPLE = "Beanie"
SAMPLE_PRICE = 18
CUSTOMER = {
    "first_name": "G02",
    "last_name": "Tester",
    "address_1": "99 Test Road",
    "city": "Bangkok",
    "state": "TH-10",
    "postcode": "10200",
    "phone": "0800000002",
}


# Goal: a fixed-cart coupon with a minimum spend is refused below 500 THB, works once the
# cart reaches 500 THB, the order total is right, and staff sees the coupon used 1 time.
def test_tc_sys_03_minimum_spend_coupon(staff, customer, ts):
    product = f"G02 ST03 Tote {ts}"
    coupon = f"G02ST03-{ts}"

    # Steps 1-3: staff creates the product and the coupon (100 off, minimum spend 500)
    product_url = staff.create_product(product, PRICE)
    staff.create_coupon(coupon, "fixed_cart", 100, minimum_spend=500)

    # Step 4: customer adds 1 tote
    customer.open_product(product_url)
    assert f"“{product}” has been added to your cart." in customer.add_to_cart(1)

    # Step 5: browse the Accessories category, open Beanie and add 1
    names = customer.open_category("accessories")
    assert SAMPLE in names
    customer.open_product_from_list(SAMPLE)
    assert f"“{SAMPLE}” has been added to your cart." in customer.add_to_cart(1)

    # Step 6: cart has 2 lines, 200 + 18 = 218
    customer.open_cart()
    assert customer.wait_cart_total(baht(PRICE + SAMPLE_PRICE)) == baht(218)
    assert set(customer.cart_product_names()) == {product, SAMPLE}

    # Step 7: coupon refused because the cart is below the minimum spend
    customer.apply_coupon(coupon)
    assert f'The minimum spend for coupon "{coupon.lower()}" is ฿500.00.' in customer.coupon_error()
    assert customer.cart_total() == baht(218)

    # Step 8: remove Beanie from the cart
    customer.remove_from_cart(SAMPLE)
    assert customer.wait_cart_total(baht(PRICE)) == baht(200)

    # Step 9: raise the tote quantity to 3 -> 600
    customer.set_cart_quantity(product, 3)
    assert customer.wait_cart_total(baht(600)) == baht(600)

    # Step 10: the coupon now applies: 600 - 100 = 500
    customer.apply_coupon(coupon)
    assert customer.wait_cart_total(baht(500)) == baht(500)
    assert baht(100) in customer.discount()

    # Step 11: place the order
    customer.proceed_to_checkout()
    customer.fill_billing({**CUSTOMER, "email": f"g02.coupon.{ts}@example.com"})
    order_id, confirmation = customer.place_order()
    assert baht(500) in confirmation
    assert str(order_id) in confirmation

    # Step 12: staff sees the order with the coupon and the 100 discount
    staff.open_order(order_id)
    assert staff.order_status() == "wc-processing"
    items = staff.order_items_text()
    assert coupon.lower() in items.lower()
    assert baht(100) in items
    assert baht(500) in items

    # Step 13: staff completes the order
    staff.set_order_status("Completed")
    assert staff.order_status() == "wc-completed"

    # Step 14: the coupon list shows it was used once
    assert staff.coupon_usage(coupon).startswith("1 /")
