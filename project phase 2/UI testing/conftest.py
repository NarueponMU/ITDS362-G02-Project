"""Fixtures for the automated UI tests (Selenium WebDriver, Group 02).

- `staff`    : a Chrome window logged in to the shop admin panel as the group account.
- `customer` : a separate Chrome window (own cookies = own guest cart).
- `ts`       : a date-time stamp added to every name the test creates, so every
               run uses new data and the tests also pass on the second run.

Credentials are read from "project phase 2/.env" (see .env.example) or from
environment variables. They are never written in the test code.
"""
import os
from datetime import datetime
from pathlib import Path

import pytest
from selenium import webdriver

from pages import Shop, StaffPanel

HERE = Path(__file__).resolve().parent
RUN_TS = datetime.now().strftime("%Y%m%d-%H%M%S")
SHOT_ROOT = HERE / "results" / "screenshots" / RUN_TS


def load_env_file():
    env_file = HERE.parent / ".env"
    if not env_file.exists():
        return
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_env_file()
SHOP_URL = os.environ.get("SHOP_URL", "http://157.85.104.96/shop").rstrip("/")


def new_driver():
    options = webdriver.ChromeOptions()
    if os.environ.get("HEADLESS", "0") == "1":
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1400,1000")
    options.add_argument("--incognito")
    # The shop runs on plain http. Chrome tries https first, and the failed upgrade
    # can leave a blank page (no <h1>), so switch the automatic upgrade off.
    options.add_argument(
        "--disable-features=HttpsUpgrades,HttpsFirstModeIncognito,"
        "HttpsFirstBalancedModeAutoEnable,HttpsFirstModeV2ForTypicallySecureUsers"
    )
    return webdriver.Chrome(options=options)


class Shots:
    """Saves numbered screenshots as evidence: results/screenshots/<run>/<test>/NN-name.png."""

    def __init__(self, test_name):
        self.folder = SHOT_ROOT / test_name
        self.folder.mkdir(parents=True, exist_ok=True)
        self.count = 0

    def __call__(self, driver, name):
        self.count += 1
        driver.save_screenshot(str(self.folder / f"{self.count:02d}-{name}.png"))


@pytest.fixture
def ts():
    return datetime.now().strftime("%Y%m%d-%H%M%S")


@pytest.fixture
def shot(request):
    return Shots(request.node.name)


@pytest.fixture
def staff(shot):
    user = os.environ.get("WP_USER")
    password = os.environ.get("WP_PASSWORD")
    if not user or not password:
        pytest.skip("Set WP_USER and WP_PASSWORD in 'project phase 2/.env' to run UI tests")
    driver = new_driver()
    panel = StaffPanel(driver, SHOP_URL, shot)
    panel.login(user, password)
    yield panel
    driver.quit()


@pytest.fixture
def customer(shot):
    driver = new_driver()
    yield Shop(driver, SHOP_URL, shot)
    driver.quit()
