# ITDS362 Project Phase 2 (Group 02)

**ระบบที่ทดสอบ:** ร้านค้าออนไลน์ WooCommerce http://157.85.104.96/shop/
**บัญชีของกลุ่ม:** `itds362-g02` (Shop manager)
ข้อมูลทุกอย่างที่กลุ่มสร้างขึ้นต้นด้วย `G02` และใช้ชื่อ อีเมล และเบอร์โทรที่สมมติขึ้นทั้งหมด

| Folder | การทดสอบ | เครื่องมือ | รายละเอียด |
|---|---|---|---|
| [`API testing/`](API%20testing/README.md) | 3 test suite: `GET /products`, `POST /cart/add-item`, `POST /cart/update-item` | pytest + requests | ข้อมูลทดสอบออกแบบด้วย input space partitioning, รวม 46 test |
| [`System testing/`](System%20testing/system_test_cases.md) | 3 manual system test case ที่ผ่านทั้งฝั่งพนักงานและฝั่งลูกค้า + traceability matrix | Chrome (manual) | `system_test_cases.md`, `traceability_matrix.md`, `defect_reports.md`, `screenshots/` |
| [`UI testing/`](UI%20testing/README.md) | แปลง TC-SYS-01..03 เป็น automated UI test | Selenium WebDriver + pytest | เก็บภาพหน้าจอทุกขั้นอัตโนมัติ |
| [`Performance testing/`](Performance%20testing/README.md) | average-load, stress, soak, spike | k6 | threshold ทุก script และตอบคำถาม a–e |

## ติดตั้งครั้งแรก

ต้องมี Python 3.10 ขึ้นไป, Google Chrome และ k6 (`brew install k6`)

```bash
cd "project phase 2"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env      # แล้วใส่รหัสผ่านของกลุ่มใน .env (ใช้เฉพาะ UI testing)
```

## รันแต่ละส่วน

เริ่มจาก folder `project phase 2` และเปิด venv ไว้ (`source .venv/bin/activate`) ทุกครั้ง

```bash
cd "API testing" && pytest                       # API testing (คำสั่งเดียว)
cd "UI testing" && pytest                        # Automated UI testing
cd "Performance testing" && ./run.sh stress_test # Performance testing (ทีละ test)
```

## สรุปผลการทดสอบ

### API Testing (รันเมื่อ 2026-11-03 13:59)

ผ่าน **38/46** test ส่วน test ที่ไม่ผ่านทั้ง 8 ข้อเป็น **defect ของระบบ** (รายละเอียด request, expected และ actual อยู่ใน [`API testing/README.md`](API%20testing/README.md)):

| ID | Defect |
|---|---|
| D-API-01 | `GET /products?min_price=abc` ตอบ **500** (ควรเป็น 400) |
| D-API-02 | กรองช่วงราคา 10–20 บาทได้แค่ 2 รายการ จากที่ควรได้ 8 |
| D-API-03 | `min_price=-100` ได้สินค้าแค่ 3 รายการ (ควรได้ทั้งหมด) |
| D-API-04/05 | `orderby=price` ทั้ง asc และ desc ไม่เรียงตามราคา |
| D-API-06 | add-item ที่จำนวน 10000 ระบบลดเหลือ 9999 เงียบๆ (update-item ตอบ 400 ในกรณีเดียวกัน) |
| D-API-07/08 | add-item และ update-item รับจำนวนทศนิยม (2.5, 2.7) แล้วปัดลงเงียบๆ |

### System Testing

test case ทั้ง 3 ข้อพร้อมผลที่คาดหวังทุกขั้นตอนอยู่ใน `System testing/system_test_cases.md`
traceability matrix ครอบคลุม 16 จาก 18 การทำงานในคู่มือ ส่วนอีก 2 ข้อ (บัญชีลูกค้าและรายชื่อลูกค้า) ทดสอบไม่ได้เพราะร้านปิดการสมัครสมาชิก
**ผลการทดสอบ manual:** ทดสอบเมื่อวันที่ 6–7 พ.ย. 2569 ผ่านครบ 44 จาก 44 ขั้น (TC-SYS-01 16 ขั้น, TC-SYS-02 14 ขั้น, TC-SYS-03 14 ขั้น) ไม่พบข้อบกพร่อง ภาพหน้าจอทุกขั้นอยู่ใน `System testing/screenshots/`

### Automated UI Testing

รัน 3 test สองรอบติดกันเมื่อวันที่ 5 พ.ย. 2569 ผ่านครบทั้งสองรอบ ภาพหน้าจอทุกขั้นอยู่ใน `UI testing/results/screenshots/` ส่วนวิดีโอดูได้ที่ https://youtu.be/gC0VQjtZFMs

### Performance Testing

รันเต็มทั้ง 4 test เมื่อ 2026-11-03 22:58–00:00 ไม่มี request ล้มเหลวเลยในทุก test (0 จาก 35,974) และ check ผ่าน 100% รายละเอียดและคำตอบข้อ a–e อยู่ใน [`Performance testing/README.md`](Performance%20testing/README.md)

| Test | VU สูงสุด | p95 | failed | ผล threshold |
|---|---|---|---|---|
| Average load | 20 | 210 ms | 0% | ✓ ผ่าน |
| Stress | 100 | 5.82 s (20 VU: 226 ms, 40 VU: 1.14 s) | 0% | ✗ เกิน 1 s ตั้งแต่ 40 VU |
| Spike | 100 | 7.48 s (ช่วง spike: 7.53 s) | 0% | ✗ ช่วง spike ช้า กลับมาปกติภายใน 30–60 s |
| Soak (33 นาที) | 15 | 193 ms (ทุกช่วง 187–197 ms) | 0% | ✓ ผ่าน ไม่ช้าลงตามเวลา |

ข้อสรุป: server ตอบได้มากที่สุดประมาณ 18 request ต่อวินาที (ประมาณ 20–40 ผู้ใช้พร้อมกัน) เกินจากนั้นระบบจะช้าลงแต่ไม่ error
