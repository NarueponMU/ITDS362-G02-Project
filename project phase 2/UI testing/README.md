# Automated UI Testing (Group 02)

เครื่องมือ: **Selenium WebDriver 4 (Python) + pytest** ใช้ Google Chrome ส่วน ChromeDriver โหลดให้อัตโนมัติด้วย Selenium Manager

| Automated test | แปลงมาจาก | สิ่งที่ตรวจบนหน้าเว็บ |
|---|---|---|
| `test_tc_sys_01_percent_coupon.py` | TC-SYS-01 | ข้อความ "added to your cart", ยอดรวม ฿500 → ฿450 → ฿675, ส่วนลด ฿50/฿75, error ของคูปองผิด, error ของฟอร์ม checkout, หน้า "Thank you. Your order has been received." ที่มีหมายเลขคำสั่งซื้อและยอด ฿675.00, สถานะ Processing → Completed ฝั่งพนักงาน |
| `test_tc_sys_02_stock_limit.py` | TC-SYS-02 | "3 in stock", จำนวน 5 ถูกปฏิเสธ, error "you already have 3 in your cart", ยอด ฿900.00, "Out of stock" ทั้งฝั่งลูกค้าและพนักงาน, ยกเลิกคำสั่งซื้อแล้วกลับเป็น "In stock (3)" |
| `test_tc_sys_03_minimum_spend_coupon.py` | TC-SYS-03 | ข้อความ "The minimum spend for coupon "g02st03-…" is ฿500.00.", ยอด ฿218 → ฿200 → ฿600 → ฿500, ส่วนลด ฿100 ฝั่งพนักงาน, Usage "1 / ∞" |

แต่ละ test ทำตามขั้นตอนเดียวกับ system test case ต้นฉบับ และมี comment `# Step N:` กำกับทุกขั้น

## หลักการที่ใช้

- **Locator ที่คงที่:** ใช้ `id` / `name` เมื่อหน้าเว็บมีให้ เช่น หน้า login, staff panel (`#title`, `#_regular_price`, `#coupon_amount`, `#order_status`) และฟอร์ม checkout (`#email`, `#billing-city`) ส่วน cart แบบ block ของ WooCommerce ไม่มี id จึงใช้ class ของ block ที่คงที่ร่วมกับ `aria-label` เช่น `input[aria-label='Quantity of … in your cart.']`
- **ไม่มีการรอแบบเวลาคงที่:** ทุกการรอใช้ `WebDriverWait` รอจนกว่า element จะปรากฏหรือข้อความที่ต้องการจะขึ้น (ดู `pages.py`) ไม่มี `time.sleep`
- **ผ่านทุกครั้งที่รัน:** ชื่อสินค้า คูปอง และอีเมลต่อท้ายด้วยวันเวลา `YYYYMMDD-HHMMSS` เช่น `G02 ST01 Mug 20261110-143012` ทุกรอบจึงใช้ข้อมูลใหม่ ลูกค้าเปิดหน้าต่าง Incognito ใหม่ทุก test ตะกร้าจึงว่างเสมอ และสต็อกของ TC-02 เป็นของสินค้าที่ test สร้างขึ้นเอง
- **หลักฐาน:** test เก็บภาพหน้าจอทุกขั้นสำคัญไว้ที่ `results/screenshots/<วันเวลาที่รัน>/<ชื่อ test>/NN-ชื่อขั้น.png`

## วิธีรัน

1. สร้างไฟล์ `project phase 2/.env` โดยคัดลอกจาก `.env.example` แล้วใส่ username และรหัสผ่าน (ที่เปลี่ยนแล้ว) ของกลุ่ม ห้าม commit ไฟล์นี้ เพราะไฟล์อยู่ใน `.gitignore` แล้ว
2. รันคำสั่ง:

```bash
cd "project phase 2"
source .venv/bin/activate          # ถ้ายังไม่มี venv ให้ดู README หลัก
cd "UI testing"
pytest                             # เปิด Chrome ให้เห็นหน้าจอ (ใช้ตอนอัดวิดีโอ)
HEADLESS=1 pytest                  # รันแบบไม่เปิดหน้าต่าง
pytest --html=results/report.html --self-contained-html
```

ถ้าไม่มี `.env` test ทั้ง 3 ข้อจะถูก **skip** พร้อมข้อความบอกวิธีตั้งค่า

> **ข้อควรรู้:** การรัน 1 รอบจะสร้างสินค้า 3 รายการ คูปอง 2 รายการ และคำสั่งซื้อ 3 รายการ (ชื่อขึ้นต้นด้วย G02 ทั้งหมด) บน server ที่ใช้ร่วมกัน จึงควรรันเท่าที่จำเป็น เช่น รอบแรก 1 ครั้ง รอบที่สองอีก 1 ครั้งเพื่อแสดงว่าผ่านซ้ำได้

## ผลการรัน

รันครบ 3 test สองรอบติดกันในวันที่ 5 พ.ย. 2569 ผ่านทั้งสองรอบ

| รอบ | เวลา | ใช้เวลา | TC-SYS-01 | TC-SYS-02 | TC-SYS-03 | ภาพหน้าจอ |
|---|---|---|---|---|---|---|
| 1 | 22:20 | 73 วินาที | Pass | Pass | Pass | `results/screenshots/20261105-222043/` |
| 2 | 22:43 | 75 วินาที | Pass | Pass | Pass | `results/screenshots/20261105-224339/` |

### วิดีโอ https://youtu.be/gC0VQjtZFMs
