# System Test Cases (Group 02): WooCommerce Shop

- ระบบ: http://157.85.104.96/shop/ (storefront) และ http://157.85.104.96/shop/wp-admin/ (staff)
- บัญชีพนักงาน: `itds362-g02` (Shop manager)
- ลูกค้าเป็น guest เพราะร้านนี้ไม่เปิดให้สมัครสมาชิก ให้เปิดหน้าต่าง Incognito แยกจากหน้าต่างของพนักงาน
- ข้อมูลทั้งหมดที่กลุ่มสร้างขึ้นต้นด้วย `G02` และต่อท้ายด้วยวันเวลาที่ทดสอบ `<ts>` รูปแบบ `YYYYMMDD-HHMM` เช่น `20261110-1030` เพื่อไม่ให้ชนกับข้อมูลของการทดสอบรอบก่อนหรือของกลุ่มอื่น
- ข้อมูลลูกค้าเป็นข้อมูลสมมติทั้งหมด

**วิธีบันทึกผล:** หลังทำแต่ละขั้นตอน ให้กรอกคอลัมน์ *Actual result* และ *Pass or fail* แล้วบันทึกภาพหน้าจอเป็นไฟล์ `screenshots/<TC-ID>/step-XX.png` ถ้าขั้นตอนใดไม่ผ่าน ให้เขียน defect report ลงใน `defect_reports.md`

---

## TC-SYS-01

| | |
|---|---|
| **Test case ID** | TC-SYS-01 |
| **Title** | พนักงานสร้างสินค้าและคูปองลด 10% → ลูกค้าซื้อสินค้าโดยใช้คูปอง → พนักงานเปลี่ยนสถานะคำสั่งซื้อเป็น Completed |
| **Objective** | ตรวจว่าสินค้าและคูปองที่พนักงานสร้างใช้งานได้จริงฝั่งลูกค้า ส่วนลดคำนวณถูกต้องแม้ลูกค้าย้อนกลับไปแก้จำนวนสินค้า และพนักงานปิดคำสั่งซื้อได้ |
| **Preconditions** | 1) พนักงาน login staff panel ได้ 2) ตะกร้าของลูกค้าว่าง (หน้าต่าง Incognito ใหม่) 3) ยังไม่มีสินค้าหรือคูปองชื่อเดียวกันในระบบ |
| **Test data** | สินค้า: `G02 ST01 Mug 20261106-1440` ราคา 250 บาท · คูปอง: `G02ST01-20261106-1440` ส่วนลด 10% (Percentage discount) · คูปองผิด: `G02WRONG` · จำนวนผิดปกติ: `0` · อีเมลผิดรูปแบบ: `g02.buyer@` · ลูกค้า: G02 Tester, `g02.buyer.20261106-1440@example.com`, 99 Test Road, Bangkok, Bangkok (TH-10), 10200, 0800000002 |
| **Tested by and date** | 6787045 นายนฤพล สันติภาพชัย, 2026-11-06 14:40 |

| Step | Action | Input data | Expected result | Actual result | Pass or fail |
|---|---|---|---|---|---|
| 1 | พนักงานเปิด `/shop/wp-admin/` แล้ว login | `itds362-g02` / password ของกลุ่ม | เข้าสู่ Dashboard และเห็นเมนู Products, WooCommerce, Marketing | เข้า Dashboard ได้ เห็นเมนู Products, WooCommerce และ Marketing | Pass |
| 2 | Products → Add New กรอกชื่อและ Regular price แล้วกด Publish | ชื่อ `G02 ST01 Mug <ts>`, ราคา `250` | ขึ้นข้อความ "Product published." | ขึ้น "Product published." สินค้าชื่อ G02 ST01 Mug 20261106-1440 ราคา ฿250 (ครั้งแรกที่กด Publish ขึ้น ERR_CONNECTION_RESET ลองใหม่แล้วผ่าน) | Pass |
| 3 | Marketing → Coupons → Add coupon กรอก code, เลือก Percentage discount, Amount แล้วกด Publish | `G02ST01-<ts>`, `10` | ขึ้นข้อความ "Coupon updated." และคูปองอยู่ในรายการคูปอง | ขึ้น "Coupon updated." คูปอง G02ST01-20261106-1440 แบบ Percentage discount 10 | Pass |
| 4 | ลูกค้าค้นหาสินค้าบน storefront | เปิด `/shop/?s=G02 ST01 Mug <ts>&post_type=product` | เห็นสินค้า `G02 ST01 Mug <ts>` ราคา ฿250.00 (ถ้าผลค้นหามีรายการเดียว ระบบจะพาไปหน้าสินค้าทันที) | หน้าสินค้า G02 ST01 Mug 20261106-1440 ราคา ฿250.00 (ดูในภาพ step-05.png) | Pass |
| 5 | เปิดหน้าสินค้า ใส่จำนวน 0 แล้วกด Add to cart (**ข้อมูลผิดปกติ**) | `0` | สินค้าไม่ถูกเพิ่ม (เบราว์เซอร์แจ้งว่าค่าต้องไม่น้อยกว่า 1) และตะกร้ายังเป็น 0 | เบราว์เซอร์ขึ้น "Value must be greater than or equal to 1." สินค้าไม่ถูกเพิ่ม ไอคอนตะกร้ายังไม่มีตัวเลข | Pass |
| 6 | ใส่จำนวน 2 แล้วกด Add to cart | `2` | ขึ้นข้อความ "2 × “G02 ST01 Mug <ts>” have been added to your cart." | ขึ้น "2 × “G02 ST01 Mug 20261106-1440” have been added to your cart." | Pass |
| 7 | เปิดหน้า Cart | – | มีสินค้า 1 บรรทัด จำนวน 2 และ Estimated total ฿500.00 | มีสินค้า 1 บรรทัด จำนวน 2 Estimated total ฿500.00 | Pass |
| 8 | กด Add coupons ใส่คูปองที่ไม่มีอยู่ แล้วกด Apply (**ข้อมูลผิดปกติ**) | `G02WRONG` | ขึ้นข้อความ `Coupon "g02wrong" cannot be applied because it does not exist.` และยอดรวมยังเป็น ฿500.00 | ขึ้น Coupon "g02wrong" cannot be applied because it does not exist. ยอดยังเป็น ฿500.00 | Pass |
| 9 | ใส่คูปองที่ถูกต้อง แล้วกด Apply | `G02ST01-<ts>` | มีแถว Discount -฿50.00 และ Estimated total ฿450.00 | Discount -฿50.00 Estimated total ฿450.00 | Pass |
| 10 | กด Proceed to Checkout | – | เปิดหน้า Checkout และ Order summary แสดงยอดรวม ฿450.00 | หน้า Checkout ขึ้น Order summary Total ฿450.00 | Pass |
| 11 | **ย้อนกลับ**ไปหน้า Cart (ปุ่ม Back ของเบราว์เซอร์) แล้วเปลี่ยนจำนวนเป็น 3 | `3` | Discount -฿75.00 และ Estimated total ฿675.00 (คูปองยังใช้อยู่) | กลับมาหน้า Cart แล้วเปลี่ยนเป็น 3 ชิ้น Discount -฿75.00 Estimated total ฿675.00 คูปองยังอยู่ | Pass |
| 12 | กด Proceed to Checkout แล้วกด Place Order โดยไม่กรอกข้อมูล (**ข้อมูลผิดปกติ**) | ฟอร์มว่าง | แสดง error ใต้ช่องที่จำเป็น เช่น "Please enter a valid email address" และไม่มีการสร้างคำสั่งซื้อ | ขึ้น error ใต้ทุกช่องที่จำเป็น เช่น "Please enter a valid email address" และ "Please enter a valid first name" ไม่มีคำสั่งซื้อเกิดขึ้น | Pass |
| 13 | กรอกอีเมลผิดรูปแบบ แล้วกด Place Order (**ข้อมูลผิดปกติ**) | `g02.buyer@` | แสดง "Please enter a valid email address" | ขึ้น "Please enter a valid email address" ใต้ช่องอีเมล | Pass |
| 14 | กรอกข้อมูลลูกค้าให้ครบและถูกต้อง เลือก Cash on delivery แล้วกด Place Order | ข้อมูลลูกค้าใน Test data | เปิดหน้า Order received ขึ้นข้อความ "Thank you. Your order has been received." พร้อมหมายเลขคำสั่งซื้อ ยอดรวม ฿675.00 และวิธีชำระ Cash on delivery (จดหมายเลขคำสั่งซื้อไว้) | หน้า Order received ขึ้น "Thank you. Your order has been received." Order #106 Total ฿675.00 Payment: Cash on delivery | Pass |
| 15 | พนักงานไปที่ WooCommerce → Orders แล้วเปิดคำสั่งซื้อตามหมายเลขในขั้นที่ 14 | หมายเลขคำสั่งซื้อ | สถานะ Processing มีสินค้า 3 ชิ้น มีคูปอง `g02st01-<ts>` ส่วนลด ฿75.00 และยอดรวม ฿675.00 | Order #106 สถานะ Processing ลูกค้าเป็น Guest มี 3 ชิ้น คูปอง g02st01-20261106-1440 ส่วนลด ฿75.00 ยอด ฿675.00 | Pass |
| 16 | เปลี่ยน Status เป็น Completed แล้วกด Update | `Completed` | ขึ้นข้อความ "Order updated." และในรายการ Orders คำสั่งซื้อนี้แสดงสถานะ Completed | ขึ้น "Order updated." สถานะเป็น Completed และในหน้า Orders #106 แสดง Completed (ภาพ step-16-order-list.png) | Pass |

**ผล:** ผ่าน 16 จาก 16 ขั้น

---

## TC-SYS-02

| | |
|---|---|
| **Test case ID** | TC-SYS-02 |
| **Title** | พนักงานสร้างสินค้าที่มีสต็อกจำกัด 3 ชิ้น → ลูกค้าพยายามซื้อเกินสต็อกแล้วซื้อจนหมด → พนักงานยกเลิกคำสั่งซื้อและสต็อกกลับคืน |
| **Objective** | ตรวจการจัดการสต็อกตลอดทั้งกระบวนการ: ระบบห้ามซื้อเกินสต็อก สต็อกลดลงเมื่อมีคำสั่งซื้อ ทั้งพนักงานและลูกค้าเห็น Out of stock และสต็อกกลับคืนเมื่อพนักงานยกเลิกคำสั่งซื้อ |
| **Preconditions** | 1) พนักงาน login ได้ 2) ตะกร้าของลูกค้าว่าง 3) สินค้าในขั้นที่ 2 ยังไม่มีใครซื้อ |
| **Test data** | สินค้า: `G02 ST02 Limited Cap 20261107-1450` ราคา 300 บาท, Track stock quantity = เปิด, Stock quantity = 3 · จำนวนเกินสต็อก: `5` · ช่อง Town / City ว่าง · ลูกค้า: G02 Tester, `g02.stock.20261107-1450@example.com`, 99 Test Road, Bangkok, Bangkok (TH-10), 10200, 0800000002 |
| **Tested by and date** | 6787045 นายนฤพล สันติภาพชัย, 2026-11-07 14:50 |

| Step | Action | Input data | Expected result | Actual result | Pass or fail |
|---|---|---|---|---|---|
| 1 | พนักงาน login staff panel | บัญชีกลุ่ม | เข้าสู่ Dashboard | login แล้วเข้า Dashboard ได้ | Pass |
| 2 | Products → Add New กรอกชื่อและราคา แล้วไปแท็บ Inventory ติ๊ก Track stock quantity ใส่ Quantity แล้วกด Publish | `G02 ST02 Limited Cap <ts>`, `300`, stock `3` | ขึ้นข้อความ "Product published." | ขึ้น "Product published." สินค้า G02 ST02 Limited Cap 20261107-1450 ราคา 300 แท็บ Inventory ติ๊ก Track stock quantity และ Quantity 3 (ภาพ step-02-inventory.png) | Pass |
| 3 | ลูกค้าเปิดหน้าสินค้า | URL จากปุ่ม View product | แสดงราคา ฿300.00 และ "3 in stock" | หน้าสินค้าแสดง ฿300.00 และ "3 in stock" | Pass |
| 4 | ใส่จำนวน 5 แล้วกด Add to cart (**ข้อมูลผิดปกติ** เกินสต็อก) | `5` | สินค้าไม่ถูกเพิ่ม (แจ้งว่าค่าต้องไม่เกิน 3 หรือสต็อกไม่พอ) และตะกร้ายังเป็น 0 | เบราว์เซอร์ขึ้น "Value must be less than or equal to 3." สินค้าไม่ถูกเพิ่ม ไอคอนตะกร้ายังไม่มีตัวเลข | Pass |
| 5 | ใส่จำนวน 3 แล้วกด Add to cart | `3` | ขึ้นข้อความว่าเพิ่ม 3 × สินค้าลงตะกร้าแล้ว | ขึ้น "3 × “G02 ST02 Limited Cap 20261107-1450” have been added to your cart." ไอคอนตะกร้าเป็น 3 | Pass |
| 6 | เปิดหน้า Cart | – | จำนวน 3 และ Estimated total ฿900.00 | จำนวน 3 Estimated total ฿900.00 | Pass |
| 7 | **ย้อนกลับ**ไปหน้าสินค้า แล้วเพิ่มอีก 1 ชิ้น (**การกระทำผิดลำดับ**) | `1` | ขึ้น error "You cannot add that amount to the cart — we have 3 in stock and you already have 3 in your cart." และในตะกร้ายังมี 3 ชิ้น | ขึ้น "You cannot add that amount to the cart — we have 3 in stock and you already have 3 in your cart." ไอคอนตะกร้ายังเป็น 3 และหน้า Checkout ในขั้นที่ 8 ก็ยังเป็น 3 ชิ้น | Pass |
| 8 | ไปหน้า Checkout กรอกข้อมูลทุกช่องยกเว้น Town / City แล้วกด Place Order (**ข้อมูลผิดปกติ**) | Town / City ว่าง | แสดง "Please enter a valid town / city" และไม่มีการสร้างคำสั่งซื้อ | ขึ้น "Please enter a valid town / city" ใต้ช่อง Town / City ยังอยู่หน้า Checkout ไม่มีคำสั่งซื้อเกิดขึ้น | Pass |
| 9 | กรอก Town / City แล้วกด Place Order (Cash on delivery) | `Bangkok` | หน้า Order received แสดงยอดรวม ฿900.00 และหมายเลขคำสั่งซื้อ | หน้า Order received ขึ้น "Thank you. Your order has been received." Order #109 Total ฿900.00 Payment: Cash on delivery | Pass |
| 10 | ลูกค้าเปิดหน้าสินค้าเดิมอีกครั้ง | – | แสดง "Out of stock" และไม่มีปุ่ม Add to cart | แสดง "Out of stock" ไม่มีช่องจำนวนและปุ่ม Add to cart | Pass |
| 11 | พนักงานไปที่ Products แล้วค้นหาสินค้านี้ | `G02 ST02 Limited Cap <ts>` | คอลัมน์ Stock แสดง "Out of stock (0)" | คอลัมน์ Stock แสดง "Out of stock (0)" | Pass |
| 12 | พนักงานเปิดคำสั่งซื้อจากขั้นที่ 9 เปลี่ยน Status เป็น Cancelled แล้วกด Update | `Cancelled` | ขึ้นข้อความ "Order updated." และสถานะเป็น Cancelled | ก่อนแก้ order #109 เป็น Processing ลูกค้า Guest 3 ชิ้น ฿900.00 (ภาพ step-12-processing.png) หลังกด Update ขึ้น "Order updated." และสถานะเป็น Cancelled | Pass |
| 13 | พนักงานกลับไปดูสินค้าในรายการ Products | – | คอลัมน์ Stock แสดง "In stock (3)" (สต็อกกลับคืน) | คอลัมน์ Stock แสดง "In stock (3)" | Pass |
| 14 | ลูกค้า reload หน้าสินค้า | – | แสดง "3 in stock" และกด Add to cart ได้อีกครั้ง | แสดง "3 in stock" และมีปุ่ม Add to cart กลับมา (หน้าตาเหมือนขั้นที่ 3 ทุกอย่าง เพราะตะกร้าว่างแล้ว) | Pass |

**ผล:** ผ่าน 14 จาก 14 ขั้น

---

## TC-SYS-03

| | |
|---|---|
| **Test case ID** | TC-SYS-03 |
| **Title** | พนักงานสร้างคูปองลด 100 บาท (ยอดขั้นต่ำ 500 บาท) → ลูกค้าใช้คูปองไม่ได้เพราะยอดไม่ถึง → ลบและแก้สินค้าในตะกร้าจนใช้คูปองได้ → พนักงานตรวจคำสั่งซื้อและจำนวนครั้งที่ใช้คูปอง |
| **Objective** | ตรวจเงื่อนไขยอดขั้นต่ำของคูปองแบบ Fixed cart discount การลบสินค้าออกจากตะกร้า และการบันทึกการใช้คูปองฝั่งพนักงาน |
| **Preconditions** | 1) พนักงาน login ได้ 2) ตะกร้าของลูกค้าว่าง 3) สินค้าตัวอย่าง "Beanie" ขายอยู่ |
| **Test data** | สินค้า: `G02 ST03 Tote 20261107-1610` ราคา 200 บาท · คูปอง: `G02ST03-20261107-1610` แบบ Fixed cart discount 100 บาท, Minimum spend 500 · สินค้าตัวอย่าง: Beanie (฿18.00) · ลูกค้า: G02 Tester, `g02.coupon.20261107-1610@example.com`, 99 Test Road, Bangkok, Bangkok (TH-10), 10200, 0800000002 |
| **Tested by and date** | 6787045 นายนฤพล สันติภาพชัย, 2026-11-07 16:10 |

| Step | Action | Input data | Expected result | Actual result | Pass or fail |
|---|---|---|---|---|---|
| 1 | พนักงาน login staff panel | บัญชีกลุ่ม | เข้าสู่ Dashboard | login แล้วเข้า Dashboard ได้ | Pass |
| 2 | Products → Add New กรอกชื่อและราคา แล้วกด Publish | `G02 ST03 Tote <ts>`, `200` | ขึ้นข้อความ "Product published." | ขึ้น "Product published." สินค้า G02 ST03 Tote 20261107-1610 ราคา 200 | Pass |
| 3 | Marketing → Coupons → Add coupon เลือก Fixed cart discount ใส่ Amount แล้วไปแท็บ Usage restriction ใส่ Minimum spend แล้วกด Publish | `G02ST03-<ts>`, `100`, min `500` | ขึ้นข้อความ "Coupon updated." | ขึ้น "Coupon updated." คูปอง G02ST03-20261107-1610 แบบ Fixed cart discount 100 และ Minimum spend 500 (ภาพ step-03-usage-restriction.png) | Pass |
| 4 | ลูกค้าเปิดหน้าสินค้า Tote แล้วเพิ่ม 1 ชิ้น | `1` | ขึ้นข้อความว่าเพิ่มลงตะกร้าแล้ว | หน้าสินค้าราคา ฿200.00 (ภาพ step-04-product.png) กดแล้วขึ้น "“G02 ST03 Tote 20261107-1610” has been added to your cart." | Pass |
| 5 | เปิดหน้าหมวด Accessories แล้วคลิก Beanie และเพิ่ม 1 ชิ้น | `/shop/product-category/accessories/`, `1` | หน้าหมวดแสดงเฉพาะสินค้าในหมวด Accessories รวมถึง Beanie และขึ้นข้อความว่าเพิ่มลงตะกร้าแล้ว | หน้า Accessories แสดง 5 รายการ มี Beanie ฿18.00 (ภาพ step-05-category.png) กดเพิ่มแล้วขึ้น "“Beanie” has been added to your cart." | Pass |
| 6 | เปิดหน้า Cart | – | มี 2 บรรทัด และ Estimated total ฿218.00 | มี 2 บรรทัด (Tote ฿200.00, Beanie ฿18.00) Estimated total ฿218.00 | Pass |
| 7 | ใช้คูปองตอนยอดรวมยังไม่ถึงขั้นต่ำ (**ข้อมูลผิดปกติ**) | `G02ST03-<ts>` | ขึ้นข้อความ "The minimum spend for coupon "g02st03-&lt;ts&gt;" is ฿500.00." (ระบบแสดงรหัสคูปองเป็นตัวพิมพ์เล็ก) และยอดรวมไม่เปลี่ยน | ขึ้น The minimum spend for coupon "g02st03-20261107-1610" is ฿500.00. ยอดยังเป็น ฿218.00 | Pass |
| 8 | กดลบ Beanie ออกจากตะกร้า (**การกระทำผิดลำดับ**) | – | เหลือ Tote บรรทัดเดียว และยอดรวม ฿200.00 | Beanie หายจากตะกร้า เหลือ Tote บรรทัดเดียว Estimated total ฿200.00 | Pass |
| 9 | เปลี่ยนจำนวน Tote เป็น 3 | `3` | Estimated total ฿600.00 | จำนวนเป็น 3 Estimated total ฿600.00 | Pass |
| 10 | ใช้คูปองอีกครั้ง | `G02ST03-<ts>` | มีแถว Discount -฿100.00 และ Estimated total ฿500.00 | ขึ้น Coupon code "G02ST03-20261107-1610" has been applied มี Subtotal ฿600.00 Discount -฿100.00 Estimated total ฿500.00 | Pass |
| 11 | Proceed to Checkout กรอกข้อมูลลูกค้าแล้วกด Place Order | ข้อมูลลูกค้าใน Test data | หน้า Order received แสดงยอดรวม ฿500.00 และหมายเลขคำสั่งซื้อ | หน้า Checkout ยอด ฿500.00 (ภาพ step-11-checkout.png) กด Place Order แล้วขึ้น "Thank you. Your order has been received." Order #112 Discount -฿100.00 Total ฿500.00 | Pass |
| 12 | พนักงานเปิดคำสั่งซื้อนั้นใน WooCommerce → Orders | หมายเลขคำสั่งซื้อ | สถานะ Processing มีคูปอง `g02st03-<ts>` ส่วนลด ฿100.00 และยอดรวม ฿500.00 | Order #112 สถานะ Processing ลูกค้า Guest คูปอง g02st03-20261107-1610 Discount ฿100.00 Order Total ฿500.00 | Pass |
| 13 | เปลี่ยน Status เป็น Completed แล้วกด Update | `Completed` | ขึ้นข้อความ "Order updated." และสถานะเป็น Completed | ขึ้น "Order updated." สถานะเป็น Completed | Pass |
| 14 | พนักงานไปที่ Marketing → Coupons แล้วค้นหาคูปองนี้ | `G02ST03-<ts>` | คอลัมน์ Usage / Limit แสดง "1 / ∞" | คูปอง g02st03-20261107-1610 คอลัมน์ Usage / Limit แสดง "1 / ∞" | Pass |

**ผล:** ผ่าน 14 จาก 14 ขั้น
