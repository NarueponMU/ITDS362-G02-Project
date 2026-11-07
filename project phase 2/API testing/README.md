# API Testing (Group 02)

ระบบที่ทดสอบ: **WooCommerce Store API** `http://157.85.104.96/shop/wp-json/wc/store/v1`
เครื่องมือ: **pytest + requests** (Python 3)

## Operation ที่เลือก (3 operation, แยก test suite ละไฟล์)

| Suite | ไฟล์ | Operation | สร้างหรือแก้ไขข้อมูลไหม |
|---|---|---|---|
| 1 | `test_products_list.py` | `GET /products` ค้นหา กรอง และเรียงสินค้า | อ่านอย่างเดียว |
| 2 | `test_cart_add_item.py` | `POST /cart/add-item` เพิ่มสินค้าลงตะกร้า | **แก้ไขตะกร้า** |
| 3 | `test_cart_update_item.py` | `POST /cart/update-item` เปลี่ยนจำนวนสินค้าในตะกร้า | **แก้ไขตะกร้า** |

## วิธีรัน (คำสั่งเดียว)

```bash
cd "project phase 2"
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cd "API testing"
pytest
```

บันทึกผลเป็นไฟล์ (แบบที่ใช้สร้างไฟล์ใน `results/`):

```bash
pytest --junitxml=results/junit.xml --html=results/report.html --self-contained-html
```

ถ้าจะรันกับ server อื่น ให้ตั้งค่า `STORE_API_URL` ก่อนรัน Store API ไม่ต้องใช้ login จึงไม่มีรหัสผ่านอยู่ในโค้ด

## ความเป็นอิสระของแต่ละ test

- fixture `cart` ใน `conftest.py` เรียก `GET /cart` เพื่อขอ **Cart-Token ใหม่ทุก test** แต่ละ test จึงมีตะกร้าของตัวเอง กลุ่มอื่นแก้ไขตะกร้านี้ไม่ได้ และผลไม่ขึ้นกับลำดับการรัน
- suite 3 ใช้ fixture `cart_with_item` ซึ่งสร้างตะกร้าใหม่ที่มี Cap 2 ชิ้นก่อนทุก test
- ไม่ hard-code ราคา: test อ่านราคาจาก API ตอนรัน แล้วคำนวณยอดที่คาดหวัง (ราคา × จำนวน)
- test เรื่องการกรองและการเรียงสินค้าใช้รายการสินค้าทั้งร้าน (`all_products`) ที่ดึงตอนรันเป็น oracle ถ้ากลุ่มอื่นเพิ่มสินค้า test ก็ยังถูก
- suite ทั้งหมดไม่มีการ checkout จึงไม่สร้างคำสั่งซื้อค้างไว้บน server

---

## การออกแบบข้อมูลทดสอบด้วย Input Space Partitioning

ใช้แนวทางเดียวกับ Project 1:
(1) ระบุ input ของ operation
(2) กำหนด characteristic ของแต่ละ input
(3) แบ่งแต่ละ characteristic เป็น block ที่ไม่ทับกันและครอบคลุมทุกค่า (disjoint + complete)
(4) เลือกค่าตัวแทนจากแต่ละ block โดยใช้ **Each Choice Coverage (ECC)** และเพิ่ม **boundary value** ที่ขอบของ block ที่เป็นช่วงตัวเลข

ค่าที่ใช้ตั้ง block มาจากเอกสาร Store API และจากค่าที่ API รายงานเอง เช่น `add_to_cart.maximum = 9999`, `per_page` อยู่ในช่วง 1–100 และราคาเป็นหน่วยสตางค์ (`"1800"` = 18.00 บาท)

### Suite 1: `GET /products`

| Characteristic | Block | ค่าที่ใช้ | ผลที่คาดหวัง |
|---|---|---|---|
| C1 `search` | b1 คำที่มีในสินค้า (ตัวพิมพ์เล็ก) | `hoodie` | 200 และทุกรายการมีคำนี้ |
| | b2 คำเดียวกันแต่ตัวพิมพ์ใหญ่ | `HOODIE` | 200 ผลเท่ากับ b1 |
| | b3 คำที่ไม่มีในสินค้าใดเลย | `zzqqxxnotaproduct` | 200 และได้ `[]` |
| | b4 ค่าว่าง | `""` | 200 และได้สินค้าทั้งหมด |
| C2 ช่วงราคา | b1 ช่วงที่ถูกต้อง | min=1000, max=2000 | ได้**ทุก**สินค้าที่ราคาอยู่ในช่วง |
| | b2 min > max | min=2000, max=1000 | 200 และได้ `[]` |
| | b3 min ติดลบ | min=-100 | ได้สินค้าทั้งหมด |
| | b4 ไม่ใช่ตัวเลข | min=`abc` | 400 `rest_invalid_param` |
| C3 `per_page` | ต่ำกว่าขอบล่าง | 0 | 400 |
| | ขอบล่าง | 1 | 200 ได้ 1 รายการ |
| | ขอบบน | 100 | 200 ได้ไม่เกิน 100 รายการ |
| | สูงกว่าขอบบน | 101 | 400 |
| C4 `orderby`/`order` | price asc | `price`,`asc` | ราคาเรียงจากน้อยไปมาก |
| | price desc | `price`,`desc` | ราคาเรียงจากมากไปน้อย |
| | ค่าที่ไม่รองรับ | `colour` | 400 |
| C5 `category` | หมวดที่มีอยู่ | 25 (Accessories) | ได้เฉพาะสินค้าในหมวดนี้ และได้ครบ |
| | หมวดที่ไม่มีอยู่ | 999999 | 200 และได้ `[]` |

### Suite 2: `POST /cart/add-item`

| Characteristic | Block | ค่าที่ใช้ | ผลที่คาดหวัง |
|---|---|---|---|
| C1 ประเภท/การมีอยู่ของ `id` | simple ที่ซื้อได้ | 15 (Belt) | 201 |
| | id ที่ไม่มีอยู่ | 999999 | 400 `woocommerce_rest_cart_invalid_product` |
| | id = 0 (boundary) | 0 | 400 เหมือนข้างบน |
| | ไม่ส่ง id | – | 400 เหมือนข้างบน |
| | variable product | 11 (Hoodie) | 400 `woocommerce_rest_missing_attributes` |
| | external / grouped | 33, 32 | 400 `woocommerce_rest_product_not_purchasable` |
| C2 `quantity` | ไม่ส่ง (ใช้ค่า default) | – | 201 จำนวน = 1 |
| | ขอบล่างของค่าที่ถูกต้อง | 1 | 201 |
| | ค่าทั่วไป | 3 | 201 ยอด = ราคา × 3 |
| | ขอบบนของค่าที่ถูกต้อง | 9999 | 201 |
| | 0 (ต่ำกว่าขอบล่าง) | 0 | 400 `..._invalid_quantity` |
| | ติดลบ | -1 | 400 |
| | สูงกว่าขอบบน | 10000 | 400 (ให้สอดคล้องกับ update-item) |
| | ทศนิยม | 2.5 | 400 |
| | ไม่ใช่ตัวเลข | `"abc"` | 400 `rest_invalid_param` |
| C3 Cart-Token | token ถูกต้อง | fixture | ตามแถวข้างบน |
| | ไม่ส่ง token | – | 401 `woocommerce_rest_missing_nonce` |

มี test เพิ่มอีก 1 ข้อคือเพิ่มสินค้าเดิมซ้ำ (1 แล้วตามด้วย 2) ต้องรวมเป็นบรรทัดเดียว จำนวน 3

### Suite 3: `POST /cart/update-item`

| Characteristic | Block | ค่าที่ใช้ | ผลที่คาดหวัง |
|---|---|---|---|
| C1 `key` | key ของสินค้าในตะกร้านี้ | จาก fixture | ตามแถวของ C2 |
| | key ที่ไม่มีอยู่ | `000…dead` | 409 `woocommerce_rest_cart_invalid_key` |
| | ไม่ส่ง key | – | 409 เหมือนข้างบน |
| | key ของตะกร้าคนอื่น | key จากตะกร้า A ใช้กับตะกร้า B | 409 (ตะกร้าต้องแยกจากกัน) |
| C2 `quantity` | เพิ่มขึ้น | 5 | 200 ยอด = ราคา × 5 |
| | ลดลงถึงขอบล่าง | 1 | 200 |
| | ขอบบน | 9999 | 200 |
| | ไม่ส่ง | – | 200 จำนวนเท่าเดิม (2) |
| | 0 | 0 | 400 `invalid_quantity` |
| | ติดลบ | -3 | 400 `invalid_quantity` |
| | สูงกว่าขอบบน | 10000 | 400 `invalid_quantity` |
| | ทศนิยม | 2.7 | 400 |
| | ไม่ใช่ตัวเลข | `"two"` | 400 `rest_invalid_param` |

ทุก test ตรวจทั้ง **status code** และ **field สำคัญ** ของ response เช่น `items[].id`, `quantity`, `totals.line_total`, `items_count`, `totals.total_price`, `currency_code`, `code` ของ error, `data.params` และ header `X-WP-Total` / `X-WP-TotalPages`

---

## ผลการทดสอบ

รันเมื่อ 2026-11-03 13:59 (เวลาไทย) ไฟล์ผลอยู่ใน `results/`
(`pytest-output-*.txt`, `junit-*.xml`, `report-*.html`)

| Suite | จำนวน test | ผ่าน | ไม่ผ่าน |
|---|---|---|---|
| 1 `GET /products` | 17 | 12 | 5 |
| 2 `POST /cart/add-item` | 17 | 15 | 2 |
| 3 `POST /cart/update-item` | 12 | 11 | 1 |
| **รวม** | **46** | **38** | **8** |

test ที่ไม่ผ่านทั้ง 8 ข้อเกิดจาก **ข้อบกพร่องของระบบ (Defect)** ทุกข้อ ไม่ใช่ความผิดพลาดของ test เพราะ request ถูกต้องตามเอกสาร และรันซ้ำได้ผลเหมือนเดิมทุกครั้ง

### Defect report

**D-API-01: `min_price` ที่ไม่ใช่ตัวเลขทำให้ server error 500**
- Test: `test_products_list.py::test_price_non_numeric_min_is_rejected`
- Request: `GET /products?min_price=abc`
- Expected: `400` และ `code = rest_invalid_param` เหมือน parameter อื่นที่ค่าไม่ถูกต้อง (เช่น `per_page=0`)
- Actual: `500 Internal Server Error` และได้ body เป็นหน้า HTML ไม่ใช่ JSON

**D-API-02: กรองช่วงราคาแล้วได้สินค้าไม่ครบ**
- Test: `test_price_range_returns_every_product_in_range`
- Request: `GET /products?min_price=1000&max_price=2000&per_page=100` (ช่วง 10.00–20.00 บาท)
- Expected: ได้สินค้าทุกชิ้นที่ราคาอยู่ในช่วง เช่น Album 15.00, Cap 16.00, Beanie 18.00, T-Shirt 18.00, Beanie with Logo 18.00, T-Shirt with Logo 18.00, Polo 20.00, V-Neck T-Shirt 15.00
- Actual: `200` แต่ได้มาแค่ `Album (1500)` กับ `Cap (1600)`

**D-API-03: `min_price` ติดลบได้สินค้าแค่ 3 รายการ**
- Test: `test_price_negative_min_returns_all_products`
- Request: `GET /products?min_price=-100&per_page=100`
- Expected: ได้สินค้าทั้งหมด เพราะทุกราคามากกว่า -1.00 บาท
- Actual: `200` แต่ได้แค่ Album, Cap, Belt

**D-API-04 / 05: เรียงตามราคา (`orderby=price`) แล้วลำดับไม่ถูก ทั้ง asc และ desc**
- Test: `test_order_by_price_is_sorted[C4-price-asc]`, `[C4-price-desc]`
- Request: `GET /products?orderby=price&order=asc&per_page=100&type=simple`
- Expected: ราคาเรียงจากน้อยไปมาก `[200, 1500, 1600, 1800, …, 9000]`
- Actual (asc): `[3500, 4500, 4500, 2500, 1800, 2000, 1800, 200, 1800, 9000, 1800, 1500, 1600, 5500]`
- Actual (desc): `[5500, 1600, 1500, 200, 1800, 9000, …]`

> ข้อสังเกตของ D-API-02 ถึง 05: สินค้าที่การกรองและการเรียงตามราคาทำงานถูกมีแค่ 3 ชิ้น (Album, Cap, Belt) จึงน่าจะเกิดจากตาราง price lookup (`wc_product_meta_lookup`) ไม่ตรงกับราคาจริงของสินค้า

**D-API-06: add-item ที่จำนวนเกินขอบบน ระบบลดเหลือ 9999 เงียบๆ แทนที่จะแจ้ง error**
- Test: `test_cart_add_item.py::test_add_with_quantity_above_max_is_rejected`
- Request: `POST /cart/add-item` `{"id": 15, "quantity": 10000}`
- Expected: `400 invalid_quantity` เหมือนที่ `update-item` ตอบเมื่อได้ 10000
- Actual: `201` และตะกร้ามี Belt **9999** ชิ้น ลูกค้าไม่รู้ว่าจำนวนถูกเปลี่ยน และสอง endpoint ทำงานไม่สอดคล้องกัน

**D-API-07: add-item รับจำนวนทศนิยมแล้วปัดลงเงียบๆ**
- Test: `test_add_with_decimal_quantity_is_rejected`
- Request: `POST /cart/add-item` `{"id": 15, "quantity": 2.5}`
- Expected: `400` เพราะจำนวนสินค้าต้องเป็นจำนวนเต็ม
- Actual: `201` และจำนวนในตะกร้า = **2**

**D-API-08: update-item รับจำนวนทศนิยมแล้วปัดลงเงียบๆ**
- Test: `test_cart_update_item.py::test_update_to_decimal_quantity_is_rejected`
- Request: `POST /cart/update-item` `{"key": "<key>", "quantity": 2.7}`
- Expected: `400`
- Actual: `200` และจำนวนในตะกร้า = **2**
