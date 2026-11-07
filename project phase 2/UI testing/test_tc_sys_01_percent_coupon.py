"""Automated version of TC-SYS-01 (see System testing/system_test_cases.md).

Staff creates a product and a 10% coupon -> customer buys 3 with the coupon
(with wrong inputs and going back to the cart on the way) -> staff completes the order.
"""
from pages import baht

PRICE = 250
CUSTOMER = {
    "first_name": "G02",
    "last_name": "Tester",
    "address_1": "99 Test Road",
    "city": "Bangkok",
    "state": "TH-10",
    "postcode": "10200",
    "phone": "0800000002",
}


# Goal: a percentage coupon made by staff gives the right discount after the customer
# changes the quantity, the order total is correct, and staff can mark the order Completed.
def test_tc_sys_01_percent_coupon_order_completed(staff, customer, ts):
    product = f"G02 ST01 Mug {ts}"
    coupon = f"G02ST01-{ts}"

    # Steps 1-3: staff logs in (fixture), creates the product and the 10% coupon
    product_url = staff.create_product(product, PRICE)
    staff.create_coupon(coupon, "percent", 10)

    # Step 4: customer searches for the product
    page = customer.search(product)
    assert baht(PRICE) in page

    # Step 5: quantity 0 is refused and the cart stays empty
    customer.open_product(product_url)
    message = customer.try_add_invalid_quantity(0)
    assert message != ""
    assert customer.cart_count_label().endswith(": 0")

    # Step 6: add 2 to the cart
    notice = customer.add_to_cart(2)
    assert f"2 × “{product}” have been added to your cart." in notice

    # Step 7: cart shows 2 x 250 = 500
    customer.open_cart()
    assert customer.wait_cart_total(baht(500)) == baht(500)

    # Step 8: a coupon that does not exist is rejected and the total does not change
    customer.apply_coupon("G02WRONG")
    assert 'Coupon "g02wrong" cannot be applied because it does not exist.' in customer.coupon_error()
    assert customer.cart_total() == baht(500)

    # Step 9: the real coupon gives 10% off
    customer.apply_coupon(coupon)
    assert customer.wait_cart_total(baht(450)) == baht(450)
    assert baht(50) in customer.discount()

    # Step 10: checkout shows the discounted total
    customer.proceed_to_checkout()
    assert customer.checkout_summary_total() == baht(450)

    # Step 11: go BACK to the cart, change quantity to 3; coupon still applies (750 - 75)
    customer.d.back()
    customer.set_cart_quantity(product, 3)
    assert customer.wait_cart_total(baht(675)) == baht(675)
    assert baht(75) in customer.discount()

    # Step 12: Place Order with an empty form shows required-field errors
    customer.proceed_to_checkout()
    customer.place_order_click()
    errors = customer.validation_errors()
    assert "Please enter a valid email address" in errors
    assert "order-received" not in customer.d.current_url

    # Step 13: an invalid e-mail address is rejected
    customer.fill_billing({**CUSTOMER, "email": "g02.buyer@"})
    customer.place_order_click()
    assert "Please enter a valid email address" in customer.validation_errors()

    # Step 14: valid data places the order; confirmation shows the total and payment method
    customer.fill_billing({**CUSTOMER, "email": f"g02.buyer.{ts}@example.com"})
    order_id, confirmation = customer.place_order()
    assert "Thank you. Your order has been received." in confirmation
    assert str(order_id) in confirmation
    assert baht(675) in confirmation
    assert "Cash on delivery" in confirmation

    # Step 15: staff finds the order: Processing, coupon and discount recorded, total 675
    staff.open_order(order_id)
    assert staff.order_status() == "wc-processing"
    items = staff.order_items_text()
    assert coupon.lower() in items.lower()
    assert baht(75) in items
    assert baht(675) in items

    # Step 16: staff marks the order Completed; the order list shows Completed
    staff.set_order_status("Completed")
    assert staff.order_status() == "wc-completed"
    assert staff.order_list_status(order_id) == "Completed"
