"""Page helpers for the WooCommerce shop (storefront and staff panel).

Locators use IDs and names where the page has them (staff panel, checkout form).
The block-based cart has no IDs, so it is located by its fixed WooCommerce block
class names and aria-labels. Every wait is an explicit WebDriverWait for an
element or a text; there are no fixed sleeps.
"""
import re
from urllib.parse import quote_plus

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

WAIT = 30


def baht(amount):
    """250 -> '฿250.00' (the format the shop shows)."""
    return f"฿{amount:,.2f}"


class BasePage:
    def __init__(self, driver, shop_url, shot):
        self.d = driver
        self.url = shop_url
        self.shot = shot
        self.wait = WebDriverWait(driver, WAIT)

    def find(self, by, value):
        return self.wait.until(EC.visibility_of_element_located((by, value)))

    def clickable(self, by, value):
        return self.wait.until(EC.element_to_be_clickable((by, value)))

    def click(self, by, value):
        el = self.clickable(by, value)
        self.d.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
        el.click()

    def type(self, by, value, text):
        el = self.find(by, value)
        self.clear(el)
        if text:
            el.send_keys(text)
        return el

    @staticmethod
    def clear(el):
        """Delete the value with real key presses. el.clear() does not reach the React
        state of the checkout form, so the old text would come back."""
        el.send_keys(Keys.END + Keys.BACKSPACE * len(el.get_attribute("value") or ""))

    def wait_text(self, by, value, text):
        """Wait until `text` appears inside the element, then return the element's text."""
        self.wait.until(EC.text_to_be_present_in_element((by, value), text))
        return self.d.find_element(by, value).text

    def body_text(self):
        return self.d.find_element(By.TAG_NAME, "body").text


# --------------------------------------------------------------------------- staff panel


class StaffPanel(BasePage):
    @property
    def admin(self):
        return f"{self.url}/wp-admin"

    def login(self, user, password):
        self.d.get(f"{self.url}/wp-login.php")
        self.type(By.ID, "user_login", user)
        self.type(By.ID, "user_pass", password)
        self.click(By.ID, "wp-submit")
        self.find(By.ID, "wpadminbar")
        self.shot(self.d, "staff-dashboard")

    def _close_tour(self):
        """WooCommerce sometimes shows a product tour pop-up on first visit."""
        for btn in self.d.find_elements(By.CSS_SELECTOR, ".woocommerce-tour-kit button[aria-label='Close Tour']"):
            if btn.is_displayed():
                btn.click()

    def _publish(self, expected_message):
        self.click(By.ID, "publish")
        message = self.wait_text(By.ID, "message", expected_message)
        return message

    def create_product(self, name, price, stock=None):
        """Products > Add New. Returns the product's storefront URL."""
        self.d.get(f"{self.admin}/post-new.php?post_type=product")
        self._close_tour()
        self.type(By.ID, "title", name)
        self.type(By.ID, "_regular_price", str(price))
        if stock is not None:
            self.click(By.CSS_SELECTOR, "li.inventory_options > a")
            manage = self.clickable(By.ID, "_manage_stock")
            if not manage.is_selected():
                manage.click()
            self.type(By.ID, "_stock", str(stock))
        self._publish("Product published")
        self.shot(self.d, "staff-product-published")
        return self.find(By.CSS_SELECTOR, "#message a").get_attribute("href")

    def create_coupon(self, code, discount_type, amount, minimum_spend=None):
        """Marketing > Coupons > Add coupon. discount_type: percent | fixed_cart | fixed_product."""
        self.d.get(f"{self.admin}/post-new.php?post_type=shop_coupon")
        self._close_tour()
        self.type(By.ID, "title", code)
        Select(self.find(By.ID, "discount_type")).select_by_value(discount_type)
        self.type(By.ID, "coupon_amount", str(amount))
        if minimum_spend is not None:
            self.click(By.CSS_SELECTOR, "li.usage_restriction_options > a")
            self.type(By.ID, "minimum_amount", str(minimum_spend))
        self._publish("Coupon updated")
        self.shot(self.d, "staff-coupon-published")

    def open_order(self, order_id):
        """Open the order edit screen (HPOS URL first, then the classic post URL)."""
        for url in (
            f"{self.admin}/admin.php?page=wc-orders&action=edit&id={order_id}",
            f"{self.admin}/post.php?post={order_id}&action=edit",
        ):
            self.d.get(url)
            try:
                WebDriverWait(self.d, 10).until(EC.presence_of_element_located((By.ID, "order_status")))
                return
            except TimeoutException:
                continue
        raise AssertionError(f"Order {order_id} edit page not found")

    def order_status(self):
        return self.d.find_element(By.ID, "order_status").get_attribute("value")

    def order_items_text(self):
        return self.find(By.ID, "woocommerce-order-items").text

    def set_order_status(self, label):
        """Pick a status from the (select2) Status box and press Update."""
        self.click(By.ID, "select2-order_status-container")
        self.click(By.XPATH, f"//li[contains(@class,'select2-results__option') and normalize-space()='{label}']")
        self.click(By.CSS_SELECTOR, "button.save_order")
        self.wait_text(By.ID, "message", "Order updated")
        self.shot(self.d, f"staff-order-{label.lower()}")

    def order_list_status(self, order_id):
        """Status label of one order in the WooCommerce > Orders list."""
        for url in (
            f"{self.admin}/admin.php?page=wc-orders&s={order_id}",
            f"{self.admin}/edit.php?post_type=shop_order&s={order_id}",
        ):
            self.d.get(url)
            marks = self.d.find_elements(
                By.XPATH, f"//tr[contains(@id,'-{order_id}')]//mark[contains(@class,'order-status')]"
            )
            # The row also holds a hidden copy of the label (shown on small screens),
            # whose .text is ''. textContent reads both; keep the first non-empty one.
            labels = [m.get_attribute("textContent").strip() for m in marks]
            labels = [label for label in labels if label]
            if labels:
                self.shot(self.d, "staff-order-list")
                return labels[0]
        raise AssertionError(f"Order {order_id} not found in the order list")

    def product_stock_label(self, name):
        """Text of the Stock column for one product in Products list."""
        self.d.get(f"{self.admin}/edit.php?post_type=product&s={quote_plus(name)}")
        row = self.find(By.XPATH, f"//tr[.//a[contains(@class,'row-title') and normalize-space()='{name}']]")
        self.shot(self.d, "staff-product-list")
        return row.find_element(By.CSS_SELECTOR, "td.is_in_stock").text

    def coupon_usage(self, code):
        """Text of the Usage / Limit column for one coupon."""
        self.d.get(f"{self.admin}/edit.php?post_type=shop_coupon&s={quote_plus(code)}")
        row = self.find(By.XPATH, f"//tr[.//a[contains(@class,'row-title') and normalize-space()='{code.lower()}']]")
        self.shot(self.d, "staff-coupon-list")
        return row.find_element(By.CSS_SELECTOR, "td.usage").text


# --------------------------------------------------------------------------- storefront


class Shop(BasePage):
    NOTICE = ".woocommerce-message, .woocommerce-error, .wc-block-components-notice-banner"
    CART_TOTAL = ".wc-block-components-totals-footer-item .wc-block-components-totals-item__value"
    DISCOUNT = ".wc-block-components-totals-discount .wc-block-components-totals-item__value"

    # ----- catalog and product page

    def search(self, keyword):
        self.d.get(f"{self.url}/?s={quote_plus(keyword)}&post_type=product")
        self.find(By.XPATH, f"//*[normalize-space()='{keyword}']")
        self.shot(self.d, "customer-search")
        return self.body_text()

    def open_category(self, slug):
        self.d.get(f"{self.url}/product-category/{slug}/")
        self.find(By.CSS_SELECTOR, ".wp-block-post-title, .woocommerce-loop-product__title")
        self.shot(self.d, f"customer-category-{slug}")
        return [e.text for e in self.d.find_elements(By.CSS_SELECTOR, ".wp-block-post-title, .woocommerce-loop-product__title")]

    def open_product_from_list(self, name):
        self.click(By.XPATH, f"//a[normalize-space()='{name}']")
        self.find(By.NAME, "add-to-cart")

    def open_product(self, url):
        self.d.get(url)
        self.find(By.CSS_SELECTOR, "h1")
        self.shot(self.d, "customer-product")

    def cart_count_label(self):
        return self.find(By.CSS_SELECTOR, ".wc-block-mini-cart__button").get_attribute("aria-label")

    def stock_text(self):
        return self.find(By.CSS_SELECTOR, ".stock").text

    def has_add_to_cart(self):
        return len(self.d.find_elements(By.NAME, "add-to-cart")) > 0

    def try_add_invalid_quantity(self, quantity):
        """Type a quantity the shop should refuse and press Add to cart.

        Returns the browser's validation message (min/max on the quantity box) or,
        if the browser let the form through, the shop's error notice."""
        qty = self.type(By.NAME, "quantity", str(quantity))
        self.click(By.NAME, "add-to-cart")
        message = qty.get_property("validationMessage")
        if not message:
            message = self.find(By.CSS_SELECTOR, ".woocommerce-error, .wc-block-components-notice-banner.is-error").text
        self.shot(self.d, f"customer-qty-{quantity}-refused")
        return message

    def add_to_cart(self, quantity):
        """Set quantity on the product page, press Add to cart and return the notice text."""
        self.type(By.NAME, "quantity", str(quantity))
        self.click(By.NAME, "add-to-cart")
        notice = self.find(By.CSS_SELECTOR, self.NOTICE).text
        self.shot(self.d, f"customer-add-{quantity}")
        return notice

    # ----- cart

    def open_cart(self):
        self.d.get(f"{self.url}/cart/")
        self.find(By.CSS_SELECTOR, ".wc-block-cart-items, .wc-block-cart__empty-cart__title")
        return self.cart_total()

    def cart_total(self):
        return self.find(By.CSS_SELECTOR, self.CART_TOTAL).text

    def wait_cart_total(self, text):
        total = self.wait_text(By.CSS_SELECTOR, self.CART_TOTAL, text)
        self.shot(self.d, "customer-cart")
        return total

    def cart_product_names(self):
        return [e.text for e in self.d.find_elements(By.CSS_SELECTOR, ".wc-block-cart-items .wc-block-components-product-name")]

    def set_cart_quantity(self, name, quantity):
        box = self.type(By.CSS_SELECTOR, f"input[aria-label='Quantity of {name} in your cart.']", str(quantity))
        box.send_keys(Keys.TAB)

    def remove_from_cart(self, name):
        self.click(By.CSS_SELECTOR, f"button[aria-label='Remove {name} from cart']")
        self.wait.until(lambda d: name not in self.cart_product_names())
        self.shot(self.d, "customer-cart-removed")

    def apply_coupon(self, code):
        """Open the coupon panel if needed, apply `code`. Returns nothing; check total or error after."""
        if not self.d.find_elements(By.ID, "wc-block-components-totals-coupon__input-coupon"):
            self.click(By.CSS_SELECTOR, ".wc-block-components-totals-coupon .wc-block-components-panel__button")
        self.type(By.ID, "wc-block-components-totals-coupon__input-coupon", code)
        self.click(By.CSS_SELECTOR, ".wc-block-components-totals-coupon__button")

    def coupon_error(self):
        text = self.find(By.CSS_SELECTOR, ".wc-block-components-totals-coupon .wc-block-components-validation-error").text
        self.shot(self.d, "customer-coupon-error")
        return text

    def discount(self):
        return self.find(By.CSS_SELECTOR, self.DISCOUNT).text

    def proceed_to_checkout(self):
        self.click(By.CSS_SELECTOR, ".wc-block-cart__submit-button")
        self.find(By.ID, "email")

    # ----- checkout

    def checkout_summary_total(self):
        return self.find(By.CSS_SELECTOR, ".wc-block-components-totals-footer-item .wc-block-components-totals-item__value").text

    def place_order_click(self):
        self.click(By.CSS_SELECTOR, ".wc-block-components-checkout-place-order-button")

    def validation_errors(self):
        self.find(By.CSS_SELECTOR, ".wc-block-components-validation-error")
        self.shot(self.d, "customer-checkout-errors")
        return [e.text for e in self.d.find_elements(By.CSS_SELECTOR, ".wc-block-components-validation-error")]

    def fill_billing(self, data):
        """data keys: email, first_name, last_name, address_1, city, state, postcode, phone."""
        self.type(By.ID, "email", data["email"])
        Select(self.find(By.ID, "billing-country")).select_by_value("TH")
        for field in ("first_name", "last_name", "address_1", "city", "postcode", "phone"):
            self.type(By.ID, f"billing-{field}", data.get(field, ""))
        Select(self.find(By.ID, "billing-state")).select_by_value(data["state"])
        self.click(By.ID, "radio-control-wc-payment-method-options-cod")

    def place_order(self):
        """Press Place Order and wait for the order-received page. Returns (order_id, page text)."""
        self.place_order_click()
        self.wait.until(EC.url_contains("order-received"))
        self.find(By.XPATH, "//*[contains(normalize-space(),'Thank you')]")
        self.shot(self.d, "customer-order-received")
        order_id = int(re.search(r"order-received/(\d+)", self.d.current_url).group(1))
        return order_id, self.body_text()
