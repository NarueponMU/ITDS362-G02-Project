# Defect Reports: System Testing (Group 02)

เขียน 1 รายการต่อ 1 ขั้นตอนที่ไม่ผ่าน ถ้าทุกขั้นตอนผ่าน ให้เขียนว่า "ไม่พบข้อบกพร่อง" พร้อมวันที่ทดสอบ

## แบบฟอร์ม

| | |
|---|---|
| **Defect ID** | D-SYS-01 |
| **Test case / Step** | TC-SYS-0X, step N |
| **Title** | (สรุปสั้นๆ ว่าอะไรผิด) |
| **Severity** | Critical / Major / Minor |
| **Environment** | http://157.85.104.96/shop/, Chrome (เวอร์ชัน), วันที่และเวลา |
| **Steps to reproduce** | 1. … 2. … 3. … |
| **Test data** | … |
| **Expected result** | … |
| **Actual result** | … |
| **Evidence** | `screenshots/TC-SYS-0X/step-NN.png` |

---

## ผลการทดสอบ

**ไม่พบข้อบกพร่อง** ทุกขั้นตอนของ test case ทั้ง 3 ข้อได้ผลตรงกับ Expected result

| Test case | วันที่ทดสอบ | ผล | คำสั่งซื้อที่ใช้ทดสอบ |
|---|---|---|---|
| TC-SYS-01 | 2026-11-06 | ผ่าน 16 จาก 16 ขั้น | #106 (Completed) |
| TC-SYS-02 | 2026-11-07 | ผ่าน 14 จาก 14 ขั้น | #109 (Cancelled) |
| TC-SYS-03 | 2026-11-07 | ผ่าน 14 จาก 14 ขั้น | #112 (Completed) |

ทดสอบบน http://157.85.104.96/shop/ ด้วย Google Chrome 157 บน macOS โดยฝั่งลูกค้าใช้หน้าต่าง Incognito
