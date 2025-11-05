# ระบบ TU REPORT - แผนผังเว็บไซต์และรายละเอียดหน้าเว็บ

> **TU REPORT** - ระบบแจ้งซ่อมและจัดการปัญหาสำหรับมหาวิทยาลัยธรรมศาสตร์
> พัฒนาด้วย Django 5.2.6 + GeoDjango + PostgreSQL/PostGIS

**Last Updated:** 2025-11-02

---

## สารบัญ

- [แผนผังเว็บไซต์ (Sitemap)](#แผนผังเว็บไซต์-sitemap)
- [รายละเอียดหน้าเว็บ (Page Descriptions)](#รายละเอียดหน้าเว็บ-page-descriptions)
- [บทบาทผู้ใช้และสิทธิ์การเข้าถึง](#บทบาทผู้ใช้และสิทธิ์การเข้าถึง)
- [ฟีเจอร์ที่เสร็จสมบูรณ์](#ฟีเจอร์ที่เสร็จสมบูรณ์)
- [เทคโนโลยีที่ใช้](#เทคโนโลยีที่ใช้)

---

## แผนผังเว็บไซต์ (Sitemap)

### โครงสร้างแอปพลิเคชัน

```
ระบบ TU REPORT
│
├── 🗺️ หน้าหลัก (Main Page)
│   └── /dashboard/map/ (แผนที่ Tickets ทั้งหมด + Heat Map) ✅ NEW
│
├── 🔐 ระบบยืนยันตัวตน (Authentication)
│   ├── /login/ (หน้าเข้าสู่ระบบ - TU API + Local)
│   └── /logout/ (ออกจากระบบ + ป้องกันการกดย้อนกลับ) ✅
│
├── 🎫 ระบบผู้ใช้ทั่วไป (User Portal)
│   ├── /tickets/my-tickets/ (รายการแจ้งปัญหาของฉัน)
│   ├── /tickets/create/ (สร้างแจ้งปัญหาใหม่ + GPS + Before Photo) ✅
│   ├── /tickets/<id>/ (รายละเอียดแจ้งปัญหา)
│   ├── /tickets/<id>/edit/ (แก้ไขแจ้งปัญหา) 🚧 TODO
│   ├── /tickets/<id>/cancel/ (ยกเลิกแจ้งปัญหา) 🚧 TODO
│   └── /tickets/<id>/feedback/ (ให้คะแนน/ความคิดเห็น) ✅
│
├── 🔧 ระบบช่างเทคนิค (Technician Portal)
│   ├── /technician/jobs/ (รายการงานที่ได้รับมอบหมาย)
│   ├── /technician/accept/<id>/ (รับงาน)
│   ├── /technician/reject/<id>/ (ปฏิเสธงาน + Auto Reassign) ✅
│   ├── /technician/update-status/<id>/ (อัพเดตสถานะงาน)
│   ├── /technician/complete/<id>/ (ทำงานเสร็จ + After Photo) ✅
│   └── /technician/availability/ (เปลี่ยนสถานะพร้อมทำงาน) 🚧 TODO
│
├── 📊 ระบบผู้ดูแล (Admin Portal)
│   ├── /dashboard/ (แดชบอร์ดผู้ดูแลระบบ) 🚧 TODO
│   ├── /dashboard/reports/ (รายงานและสถิติ) 🚧 TODO
│   └── /dashboard/technicians/ (จัดการช่าง) 🚧 TODO
│
├── 👤 ระบบโปรไฟล์ (User Profile)
│   ├── /profile/ (โปรไฟล์ของฉัน)
│   ├── /profile/edit/ (แก้ไขโปรไฟล์) 🚧 TODO
│   ├── /profile/security/ (ตั้งค่าความปลอดภัย) 🚧 TODO
│   └── /profile/settings/ (ตั้งค่าทั่วไป) 🚧 TODO
│
├── 🔔 ระบบแจ้งเตือน (Notifications)
│   ├── /notifications/ (ศูนย์การแจ้งเตือน) 🚧 TODO
│   └── /notifications/mark-read/<id>/ (ทำเครื่องหมายอ่านแล้ว) 🚧 TODO
│
└── ⚙️ ระบบจัดการ (System Administration)
    └── /admin/ (Django Admin Panel)
```

**สัญลักษณ์:**
- ✅ = เสร็จสมบูรณ์แล้ว
- 🚧 = ยังไม่เสร็จ (TODO)
- ⭐ = ฟีเจอร์ใหม่ที่เพิ่มเข้ามา

---

## รายการหน้าเว็บทั้งหมด (19 หน้า)

| # | ชื่อหน้า | URL | บทบาท | สถานะ | คำอธิบาย |
|---|---------|-----|--------|-------|---------|
| 1 | แผนที่หลัก (Main Page) | `/dashboard/map/` | All | ✅ | แผนที่ Tickets ทั้งหมด + Heat Map |
| 2 | หน้าเข้าสู่ระบบ | `/login/` | Public | ✅ | Login ผ่าน TU API หรือ Local |
| 3 | ออกจากระบบ | `/logout/` | All | ✅ | Logout + ป้องกันกดย้อนกลับ |
| 4 | รายการแจ้งปัญหา | `/tickets/my-tickets/` | User, Tech, Admin | ✅ | ดู Tickets ของตัวเอง |
| 5 | สร้างแจ้งปัญหา | `/tickets/create/` | User, Admin | ✅ | สร้าง Ticket + GPS + Before Photo |
| 6 | รายละเอียด Ticket | `/tickets/<id>/` | Owner, Tech, Admin | ✅ | ดูรายละเอียดและประวัติ |
| 7 | แก้ไข Ticket | `/tickets/<id>/edit/` | Owner | ✅ | แก้ไข Ticket (PENDING เท่านั้น) |
| 8 | ยกเลิก Ticket | `/tickets/<id>/cancel/` | Owner | ✅ | ยกเลิก Ticket + Unassign ช่าง |
| 9 | ให้คะแนน | `/tickets/<id>/feedback/` | Owner | ✅ | ให้คะแนนและความคิดเห็น |
| 10 | รายการงานช่าง | `/technician/jobs/` | Technician | ✅ | ดูงานที่ได้รับมอบหมาย |
| 11 | รับงาน | `/technician/accept/<id>/` | Technician | ✅ | รับงาน (PENDING → IN_PROGRESS) |
| 12 | ปฏิเสธงาน | `/technician/reject/<id>/` | Technician | ✅ | ปฏิเสธ + Auto Reassign |
| 13 | อัพเดตสถานะ | `/technician/update-status/<id>/` | Technician | ✅ | อัพเดตสถานะงาน |
| 14 | ทำงานเสร็จ | `/technician/complete/<id>/` | Technician | ✅ | ทำงานเสร็จ + After Photo |
| 15 | เปลี่ยนสถานะพร้อมทำงาน | `/technician/availability/` | Technician | ✅ | Toggle พร้อมรับงานใหม่ |
| 16 | การแจ้งเตือน | `/notifications/` | All | ✅ | Notification Center |
| 17 | ทำเครื่องหมายอ่าน | `/notifications/mark-read/<id>/` | All | ✅ | Mark notification as read |
| 18 | ทำเครื่องหมายอ่านทั้งหมด | `/notifications/mark-all-read/` | All | ✅ | Mark all as read |
| 19 | แดชบอร์ด Admin | `/dashboard/` | Admin | ✅ | สถิติและรายงานแบบครบวงจร |
| 20 | โปรไฟล์ | `/profile/` | All | ✅ | ดูโปรไฟล์ส่วนตัว |
| 21 | แก้ไขโปรไฟล์ | `/profile/edit/` | All | 🚧 | แก้ไขข้อมูลโปรไฟล์ (TODO) |
| 22 | Django Admin | `/admin/` | Superuser | ✅ | จัดการระบบทั้งหมด |

---

## รายละเอียดหน้าเว็บ (Page Descriptions)

### 1. แผนที่หลัก - Main Page ✅
**URL:** `/dashboard/map/`
**สิทธิ์:** All (ทุก role ที่ล็อกอินแล้ว)
**สถานะ:** ✅ เสร็จสมบูรณ์

**วัตถุประสงค์:**
หน้าหลักแสดง Tickets ทั้งหมดบนแผนที่ พร้อม Heat Map และระบบกรอง (สำหรับทุกคน)

**องค์ประกอบหลัก:**
1. **Summary Statistics Cards:**
   - ทั้งหมด (จำนวน Tickets ทั้งหมด)
   - รอดำเนินการ (PENDING) - สีเหลือง
   - กำลังดำเนินการ (IN_PROGRESS/WORKING) - สีน้ำเงิน
   - เสร็จสิ้น (COMPLETED/CLOSED) - สีเขียว

2. **ระบบกรอง (Filters):**
   - กรองตามสถานะ (ทั้งหมด/รอดำเนินการ/กำลังดำเนินการ/เสร็จสิ้น)
   - กรองตามหมวดหมู่ (dropdown แสดงหมวดหมู่ทั้งหมด)
   - ปุ่ม Toggle Heat Map (แสดง/ซ่อน)

3. **แผนที่ Interactive (Leaflet.js + OpenStreetMap):**
   - Markers สีต่างๆ ตามสถานะ:
     - 🟡 เหลือง = PENDING
     - 🔵 น้ำเงิน = IN_PROGRESS/WORKING
     - 🟢 เขียว = COMPLETED/CLOSED
   - Markers ขนาดใหญ่ + ขอบแดงสำหรับ CRITICAL tickets
   - คลิกที่ marker → แสดง popup + เปิด details panel
   - Popup แสดงข้อมูลสรุป + ปุ่ม "ดูรายละเอียด"

4. **⭐ Details Panel (ด้านล่างแผนที่):**
   - แสดงเมื่อคลิกที่ marker
   - **ข้อมูล Ticket:**
     - หัวข้อและรายละเอียดปัญหา
     - สถานะ (badge สี)
     - หมวดหมู่
     - ความเร่งด่วน
     - วันที่แจ้ง
   - **รูปภาพ:**
     - รูปก่อนดำเนินการ (Before Photo)
     - รูปหลังดำเนินการ (After Photo) - ถ้ามี
     - แสดง "ไม่มีรูปภาพ" ถ้าไม่มี
   - **ไม่แสดง:** ชื่อผู้แจ้ง, ชื่อช่าง (privacy)
   - ปุ่มปิด panel (×)

5. **⭐ Heat Map Overlay (Category-Aware Density):**
   - แสดงความหนาแน่นของ Tickets แบบอัจฉริยะ
   - **Algorithm:** คำนวณปัญหาหมวดหมู่เดียวกันที่อยู่ใกล้กัน (ภายใน ~100m)
   - **Intensity:** ยิ่งมีปัญหาหมวดหมู่เดียวกันใกล้กัน → สีเข้มขึ้น
   - **Gradient สี (ตามความหนาแน่น):**
     - โปร่งใส (ไม่มีปัญหา)
     - ฟ้า-เขียว (ความหนาแน่นต่ำ)
     - เหลือง (ความหนาแน่นปานกลาง)
     - ส้ม (ความหนาแน่นสูง)
     - แดงเข้ม (ความหนาแน่นสูงมาก)
   - กดปุ่ม Toggle เพื่อแสดง/ซ่อน
   - Overlay ทับบนแผนที่จริง

6. **Legend (คำอธิบายสี):**
   - แสดงความหมายของสี markers
   - อธิบายสัญลักษณ์ต่างๆ

**ฟีเจอร์:**
- ✅ แผนที่แสดง Tickets ทั้งหมดที่มี GPS location
- ✅ Heat Map overlay (Leaflet.heat plugin) with category-aware density
- ✅ กรองตามสถานะ (auto-submit form)
- ✅ กรองตามหมวดหมู่
- ✅ Markers สีตามสถานะ
- ✅ Markers ขนาดและขอบแดงสำหรับ CRITICAL
- ✅ Popup แสดงข้อมูล Ticket + ปุ่มดูรายละเอียด
- ✅ **Details Panel** ด้านล่างแผนที่เมื่อคลิก marker
- ✅ แสดง Before/After Photos ใน details panel
- ✅ ไม่แสดงชื่อผู้แจ้ง/ช่าง ใน details panel (privacy)
- ✅ Heat map แบบอัจฉริยะ: สีเข้มตามความหนาแน่นของปัญหาหมวดหมู่เดียวกัน
- ✅ Auto-fit map bounds เพื่อแสดง markers ทั้งหมด
- ✅ Statistics cards แสดงจำนวนแต่ละสถานะ
- ✅ Responsive design
- ✅ เชื่อมกับโลโก้ TU REPORT (คลิกโลโก้ → กลับ Main Page)

**Navigation:**
- คลิกโลโก้ "TU REPORT" ใน navbar → Main Page
- เมนู "แผนที่หลัก" ใน navbar → Main Page

**ไฟล์:**
- `dashboard/views.py` (map_view)
- `templates/dashboard/main_page.html`
- `dashboard/urls.py`

---

### 2. หน้าเข้าสู่ระบบ (Login Page) ✅
**URL:** `/login/`
**สิทธิ์:** Public (ทุกคน)
**สถานะ:** ✅ เสร็จสมบูรณ์

**วัตถุประสงค์:**
ยืนยันตัวตนผ่าน TU API (Mock) หรือ Local Authentication พร้อมระบบรักษาความปลอดภัย

**องค์ประกอบหลัก:**
1. **โลโก้และชื่อแอป** - "TU REPORT ระบบแจ้งซ่อม มธ."
2. **ช่อง Username/Password**
3. **ปุ่มเลือกประเภท Login:**
   - TU API (เชื่อมต่อกับ Mock TU API)
   - Local (ระบบภายใน)
4. **ปุ่มเข้าสู่ระบบ**
5. **แสดงข้อผิดพลาด** (ถ้ามี)

**ฟีเจอร์:**
- ✅ Session-based authentication
- ✅ Auto redirect ตามบทบาท (User → tickets, Technician → jobs, Admin → dashboard)
- ✅ Login logging (บันทึกประวัติการเข้าสู่ระบบ)
- ✅ IP address tracking
- ✅ Session security (HttpOnly, SameSite=Lax, 24hr timeout)

**ระบบรักษาความปลอดภัย:**
- ✅ CSRF Protection
- ✅ Session timeout (24 ชั่วโมง)
- ✅ Secure cookies (HttpOnly, SameSite)

---

### 2. ออกจากระบบ (Logout) ✅
**URL:** `/logout/`
**สิทธิ์:** ผู้ที่ล็อกอินแล้ว
**สถานะ:** ✅ เสร็จสมบูรณ์

**วัตถุประสงค์:**
ออกจากระบบและป้องกันการกดย้อนกลับเข้าหน้าที่ต้อง login

**ฟีเจอร์:**
- ✅ Flush session สมบูรณ์
- ✅ ตั้ง Cache-Control headers (no-cache, no-store, must-revalidate)
- ✅ ป้องกันการกดปุ่มย้อนกลับ (Back button)
- ✅ Middleware validation (SessionSecurityMiddleware)
- ✅ Redirect กลับ login page

**ระบบรักษาความปลอดภัย:**
- ✅ Session flush
- ✅ Cache headers
- ✅ Middleware checks

---

### 3. สร้างแจ้งปัญหา (Create Ticket) ✅
**URL:** `/tickets/create/`
**สิทธิ์:** User, Admin
**สถานะ:** ✅ เสร็จสมบูรณ์

**วัตถุประสงค์:**
สร้าง Ticket ใหม่พร้อม GPS Auto-Capture และ Before Photo

**องค์ประกอบหลัก:**
1. **หัวข้อหน้า** - "แจ้งปัญหา"
2. **ช่องกรอกหัวเรื่อง** (required)
3. **เลือกหมวดหมู่** (required):
   - ⚡ ไฟฟ้า (Electrical)
   - 💧 ประปา (Plumbing)
   - 🏗️ อาคาร (Building)
   - ❄️ แอร์ (Air Conditioning)
   - 🌐 เครือข่าย (Network)
   - 🔧 อื่นๆ (Others)
4. **ระดับความเร่งด่วน** (required):
   - ⚪ ปกติ (NORMAL)
   - 🟡 เร่งด่วน (URGENT)
   - 🔴 วิกฤต (CRITICAL)
5. **รายละเอียด** - textarea (required)
6. **สถานที่ (อาคาร/ห้อง)** - text input (optional)
7. **⭐ GPS Auto-Capture** (required):
   - 🎯 ปุ่ม "ใช้ตำแหน่งปัจจุบัน (GPS)"
   - แผนที่ Leaflet + OpenStreetMap
   - คลิกบนแผนที่เพื่อเลือกตำแหน่ง
   - แสดงสถานะ GPS (กำลังค้นหา/สำเร็จ/ล้มเหลว)
   - Hidden fields: latitude, longitude (required)
8. **⭐ Before Photo Upload** (required):
   - Input file (accept image/*)
   - แสดง preview รูปภาพ
   - Max size: 5MB
9. **ปุ่มส่งรายงาน/ยกเลิก**

**ฟีเจอร์:**
- ✅ GPS Auto-Capture ด้วย Geolocation API
- ✅ แผนที่แบบ Interactive (Leaflet.js)
- ✅ Before Photo Upload (required)
- ✅ Photo Preview ด้วย FileReader API
- ✅ Form validation (client-side + server-side)
- ✅ บันทึกตำแหน่ง GPS เป็น PostGIS Point (SRID 4326)
- ✅ Auto-dispatch หาช่างอัตโนมัติ
- ✅ บันทึก Before Photo ใน BeforeAfterPhoto model
- ✅ สร้าง TicketStatusHistory (สถานะ PENDING)
- ✅ แสดงข้อความว่าได้มอบหมายให้ช่างคนไหนแล้ว

**ไฟล์:**
- `templates/user/create_ticket.html`
- `tickets/views.py` (create_ticket)

---

### 4. รายละเอียด Ticket ✅
**URL:** `/tickets/<id>/`
**สิทธิ์:** Owner, Assigned Technician, Admin
**สถานะ:** ✅ เสร็จสมบูรณ์

**วัตถุประสงค์:**
แสดงรายละเอียด Ticket พร้อมประวัติการเปลี่ยนสถานะและไฟล์แนบ

**องค์ประกอบหลัก:**
1. **Ticket Header** - #ID + Title + Status Badge
2. **Ticket Info Card:**
   - Category
   - Urgency Level
   - Description
   - Address
   - Created By
   - Assigned To
   - Created/Updated timestamps
3. **GPS Location Map:**
   - แผนที่แสดงตำแหน่ง
   - พิกัด Lat/Lng
4. **Before/After Photos:**
   - แสดงรูป Before Photo
   - แสดงรูป After Photo (ถ้ามี)
5. **Status History Timeline:**
   - แสดงประวัติการเปลี่ยนสถานะ
   - เรียงตามเวลา (ใหม่ → เก่า)
   - แสดงผู้เปลี่ยน + เวลา + comment
6. **Action Buttons:**
   - User: ปุ่มให้คะแนน (ถ้า COMPLETED/CLOSED)
   - Technician: ปุ่มอัพเดตสถานะ
   - Admin: ปุ่มมอบหมายใหม่

**ฟีเจอร์:**
- ✅ แสดง Before/After Photos จาก BeforeAfterPhoto model
- ✅ แสดง Status History แบบ timeline
- ✅ แสดง GPS location บนแผนที่
- ✅ Permission check (เฉพาะเจ้าของ/ช่างที่รับผิดชอบ/Admin)
- ✅ ปุ่ม action ตามสิทธิ์และสถานะ

---

### 5. ให้คะแนนและความคิดเห็น (Feedback Form) ✅
**URL:** `/tickets/<id>/feedback/`
**สิทธิ์:** Ticket Owner
**สถานะ:** ✅ เสร็จสมบูรณ์

**วัตถุประสงค์:**
ให้ผู้ใช้ให้คะแนนและความคิดเห็นสำหรับงานที่เสร็จแล้ว

**องค์ประกอบหลัก:**
1. **Ticket Info** (read-only):
   - Ticket #ID + Title
   - Technician name
   - Completed date
2. **⭐ Overall Rating** (required):
   - Star rating 1-5 (⭐⭐⭐⭐⭐)
   - Interactive JavaScript (คลิกดาว)
   - แสดงสีเหลืองเมื่อเลือก
3. **Detailed Ratings** (optional):
   - ความเร็วในการตอบสนอง (Response Speed) - dropdown 1-5
   - คุณภาพการทำงาน (Work Quality) - dropdown 1-5
   - ความสุภาพเรียบร้อย (Politeness) - dropdown 1-5
   - ความสะอาด (Cleanliness) - dropdown 1-5
4. **Comment** (optional):
   - Textarea
   - Max 500 ตัวอักษร
   - Placeholder: "แชร์ประสบการณ์ของคุณ..."
5. **ปุ่มส่งความคิดเห็น/ยกเลิก**

**ฟีเจอร์:**
- ✅ Star rating แบบ interactive (JavaScript)
- ✅ Overall rating required (1-5 stars)
- ✅ Detailed ratings optional (4 categories)
- ✅ Comment field (max 500 chars)
- ✅ Validation: เฉพาะ COMPLETED/CLOSED tickets
- ✅ Validation: ป้องกัน duplicate feedback (OneToOneField)
- ✅ บันทึกใน TicketFeedback model
- ✅ เชื่อมโยง technician, ticket, created_by

**ไฟล์:**
- `templates/tickets/feedback_form.html`
- `tickets/views.py` (submit_feedback)

---

### 5.1 แก้ไข Ticket (Edit Ticket) ✅
**URL:** `/tickets/<id>/edit/`
**สิทธิ์:** Ticket Owner (created_by)
**สถานะ:** ✅ เสร็จสมบูรณ์

**วัตถุประสงค์:**
ให้ผู้ใช้แก้ไขข้อมูล Ticket ของตัวเองที่ยังอยู่ในสถานะ PENDING

**องค์ประกอบหลัก:**
1. **Editable Fields:**
   - หัวข้อปัญหา (Title)
   - หมวดหมู่ (Category)
   - รายละเอียด (Description)
   - ระดับความเร่งด่วน (Urgency Level)
   - สถานที่ (Address Description)

2. **Non-Editable Fields:**
   - GPS Location (แสดงเป็น read-only)
   - Before Photo (ไม่สามารถเปลี่ยนได้)
   - Created date
   - Status

3. **Validation:**
   - เฉพาะสถานะ PENDING เท่านั้น
   - เฉพาะเจ้าของ ticket
   - Form validation (client + server)

**ฟีเจอร์:**
- ✅ แก้ไข ticket เฉพาะสถานะ PENDING
- ✅ แก้ไขได้เฉพาะ: title, category, description, urgency, address
- ✅ ไม่สามารถแก้ไข GPS และรูปภาพ
- ✅ บันทึกประวัติการแก้ไขใน TicketStatusHistory
- ✅ Form validation
- ✅ Permission check (owner only)
- ✅ แสดง info message สำหรับ non-editable fields

**ไฟล์:**
- `templates/user/edit_ticket.html`
- `tickets/views.py` (edit_ticket)

---

### 5.2 ยกเลิก Ticket (Cancel Ticket) ✅
**URL:** `/tickets/<id>/cancel/`
**สิทธิ์:** Ticket Owner (created_by)
**สถานะ:** ✅ เสร็จสมบูรณ์

**วัตถุประสงค์:**
ให้ผู้ใช้ยกเลิก Ticket ของตัวเอง (สถานะ PENDING, IN_PROGRESS, INSPECTING, WORKING)

**องค์ประกอบหลัก:**
1. **Ticket Information (read-only):**
   - Ticket #ID + Title
   - สถานะปัจจุบัน
   - หมวดหมู่
   - ช่างที่รับผิดชอบ (ถ้ามี)

2. **Warning Messages:**
   - แจ้งเตือนว่าไม่สามารถย้อนกลับได้
   - แจ้งว่าจะแจ้งเตือนช่าง (ถ้ามี)

3. **Cancel Form:**
   - เหตุผลในการยกเลิก (optional textarea)
   - ปุ่มยืนยัน/กลับ

**ฟีเจอร์:**
- ✅ ยกเลิกได้เฉพาะสถานะ: PENDING, IN_PROGRESS, INSPECTING, WORKING
- ✅ เปลี่ยนสถานะเป็น REJECTED
- ✅ Unassign technician (assigned_to = None)
- ✅ บันทึกเหตุผลใน reject_reason
- ✅ สร้าง TicketStatusHistory พร้อม comment
- ✅ หน้า confirmation พร้อม warning
- ✅ ช่องเหตุผล (optional)
- ✅ แสดง success message พร้อมแจ้งว่าได้แจ้งช่างแล้ว
- ✅ Redirect ไปหน้า my_tickets

**ไฟล์:**
- `templates/user/cancel_ticket.html`
- `tickets/views.py` (cancel_ticket)

---

### 5.3 ค้นหาและกรอง Tickets (Search & Filter) ✅
**URLs:**
- `/tickets/my-tickets/` (User view)
- `/technician/jobs/` (Technician view)
**สิทธิ์:** User (own tickets) / Technician (assigned tickets)
**สถานะ:** ✅ เสร็จสมบูรณ์

**วัตถุประสงค์:**
ให้ผู้ใช้และช่างสามารถค้นหาและกรองรายการ tickets ได้อย่างสะดวก

**องค์ประกอบหลัก:**

1. **Search Bar:**
   - ค้นหาจากชื่อหัวข้อ (title) หรือรายละเอียด (description)
   - ใช้ case-insensitive search
   - แสดงค่าที่ค้นหาใน input field

2. **Filter Options (4 dropdown menus):**
   - **สถานะ (Status):**
     - ทั้งหมด / รอดำเนินการ / รับงานแล้ว / กำลังตรวจสอบ / กำลังดำเนินการ / เสร็จสิ้น / ปิดงาน / ปฏิเสธ
   - **หมวดหมู่ (Category):**
     - ทั้งหมด / (รายการ categories ที่ active)
   - **ความเร่งด่วน (Urgency):**
     - ทั้งหมด / ต่ำ / ปานกลาง / สูง / เร่งด่วนมาก
   - **เรียงตาม (Sort):**
     - ล่าสุด / เก่าสุด / เร่งด่วนมากสุด / เร่งด่วนน้อยสุด

3. **Date Range Filter:**
   - วันที่เริ่มต้น (date_from)
   - วันที่สิ้นสุด (date_to)
   - ใช้ input type="date"

4. **Action Buttons:**
   - 🔍 ค้นหา (submit button)
   - 🔄 ล้างตัวกรอง (clear all filters)
   - แสดงผลลัพธ์จำนวนรายการที่กรอง (เมื่อมีการกรอง)

**ฟีเจอร์:**
- ✅ Search by title OR description (Q objects)
- ✅ Filter by status, category, urgency
- ✅ Filter by date range (created_at)
- ✅ Sort by created_at, urgency_level
- ✅ Maintain filter state in URL parameters
- ✅ Show filtered result count
- ✅ Clear all filters button
- ✅ Responsive UI with Tailwind CSS
- ✅ Works for both user and technician views

**Implementation Details:**
- **Backend:**
  - Uses Django Q objects for OR search
  - Filters applied progressively (chainable)
  - Date parsing with datetime.strptime()
  - Validation of sort_by values
  - Pass all filter values to template for state maintenance

- **Frontend:**
  - GET form with query parameters
  - Selected values shown in dropdowns
  - Result counter displayed when filters active
  - Clear button redirects to base URL

**ไฟล์:**
- `tickets/views.py` (my_tickets, lines 74-155)
- `technician/views.py` (job_list, lines 10-101)
- `templates/user/my_tickets.html` (lines 31-120)
- `templates/technician/job_list.html` (lines 36-123)

---

### 6. รายการงานช่าง (Technician Jobs) ✅
**URL:** `/technician/jobs/`
**สิทธิ์:** Technician
**สถานะ:** ✅ เสร็จสมบูรณ์

**วัตถุประสงค์:**
แสดงงานที่ได้รับมอบหมายให้ช่าง

**องค์ประกอบหลัก:**
1. **หัวข้อ** - "งานของฉัน"
2. **Summary Cards:**
   - Pending count
   - In Progress count
3. **Job List:**
   - แสดง Tickets ที่ assigned_to = current technician
   - ยกเว้น CLOSED, REJECTED
   - เรียงตาม -created_at
4. **Each Job Card:**
   - Ticket #ID + Title
   - Status badge
   - Category
   - Created by
   - Created date
   - Action buttons (Accept/Reject/Update/Complete)

**ฟีเจอร์:**
- ✅ แสดงงานที่ได้รับมอบหมาย
- ✅ Summary statistics
- ✅ Permission check (technician role only)
- ✅ Links to accept, reject, update, complete

---

### 7. รับงาน (Accept Job) ✅
**URL:** `/technician/accept/<id>/`
**สิทธิ์:** Assigned Technician
**สถานะ:** ✅ เสร็จสมบูรณ์

**วัตถุประสงค์:**
ช่างรับงาน (PENDING → IN_PROGRESS)

**ฟีเจอร์:**
- ✅ เปลี่ยนสถานะจาก PENDING → IN_PROGRESS
- ✅ สร้าง TicketStatusHistory
- ✅ Validation: เฉพาะ PENDING tickets
- ✅ แสดง success message
- ✅ Redirect กลับ job list

---

### 8. ปฏิเสธงาน + Auto Reassign ✅
**URL:** `/technician/reject/<id>/`
**สิทธิ์:** Assigned Technician
**สถานะ:** ✅ เสร็จสมบูรณ์

**วัตถุประสงค์:**
ช่างปฏิเสธงาน → ระบบหาช่างใหม่อัตโนมัติ

**ฟีเจอร์:**
- ✅ Unassign current technician
- ✅ สร้าง TicketStatusHistory (บันทึกการปฏิเสธ)
- ✅ เรียก auto_dispatch_ticket() หาช่างใหม่
- ✅ แสดง success message ถ้าหาช่างใหม่ได้
- ✅ แสดง warning ถ้าไม่พบช่าง
- ✅ Validation: เฉพาะ PENDING tickets

**ไฟล์:**
- `technician/views.py` (reject_job)

---

### 9. ทำงานเสร็จ + After Photo ✅
**URL:** `/technician/complete/<id>/`
**สิทธิ์:** Assigned Technician
**สถานะ:** ✅ เสร็จสมบูรณ์

**วัตถุประสงค์:**
ช่างทำงานเสร็จ พร้อมอัพโหลดรูป After Photo

**องค์ประกอบหลัก:**
1. **Ticket Info** (read-only):
   - Ticket #ID + Title
   - Category
   - Created by
2. **⭐ After Photo Upload** (required):
   - Input file (accept image/*)
   - Preview รูปภาพ
   - Required field
3. **Comment** (optional):
   - Textarea
   - หมายเหตุเพิ่มเติม
4. **ปุ่มยืนยันทำงานเสร็จ/ยกเลิก**

**ฟีเจอร์:**
- ✅ After Photo upload (required)
- ✅ Photo preview ด้วย FileReader API
- ✅ บันทึกใน BeforeAfterPhoto model (photo_type='AFTER')
- ✅ เปลี่ยนสถานะเป็น COMPLETED
- ✅ บันทึก completed_at timestamp
- ✅ สร้าง TicketStatusHistory
- ✅ Validation: เฉพาะ IN_PROGRESS/INSPECTING/WORKING tickets
- ✅ แสดง error ถ้าไม่แนบรูป

**ไฟล์:**
- `templates/technician/complete_job.html`
- `technician/views.py` (complete_job)

---

### 9.1 เปลี่ยนสถานะพร้อมทำงาน (Availability Toggle) ✅
**URL:** `/technician/availability/`
**สิทธิ์:** Technician
**สถานะ:** ✅ เสร็จสมบูรณ์

**วัตถุประสงค์:**
ให้ช่างสามารถ toggle สถานะพร้อมรับงานใหม่ได้ด้วยตัวเอง

**องค์ประกอบหลัก:**
1. **Toggle Button** (ใน Job List page):
   - ✅ พร้อมรับงาน (สีเขียว)
   - ⏸️ หยุดรับงาน (สีเทา)
   - One-click toggle
   - แสดงด้านบนของหน้า job list

2. **Functionality:**
   - Toggle TechnicianPresence.is_available
   - Auto-create presence record if not exists
   - Default to available (True)

3. **Feedback Messages:**
   - Success: "✅ คุณพร้อมรับงานใหม่แล้ว"
   - Warning: "⏸️ คุณหยุดรับงานใหม่ชั่วคราว (งานที่มีอยู่แล้วยังคงดำเนินการต่อ)"

**ฟีเจอร์:**
- ✅ One-click toggle availability
- ✅ Visual feedback (green/gray button)
- ✅ Auto-create TechnicianPresence record
- ✅ Auto-dispatcher respects availability
- ✅ Unavailable technicians skipped in assignment
- ✅ Existing assigned tickets continue normally
- ✅ Clear success/warning messages
- ✅ Integrated into job list page

**Impact on Auto-Dispatcher:**
- Auto-dispatcher checks `is_available` before assigning
- Unavailable technicians are completely skipped
- Helps technicians control their workload
- Prevents over-assignment

**ไฟล์:**
- `technician/views.py` (update_availability, job_list)
- `tickets/dispatcher.py` (find_best_technician)
- `templates/technician/job_list.html`

---

### 9.2 การแจ้งเตือน (Notification Center) ✅
**URL:** `/notifications/`
**สิทธิ์:** All logged-in users
**สถานะ:** ✅ เสร็จสมบูรณ์

**วัตถุประสงค์:**
ศูนย์รวมการแจ้งเตือนทั้งหมด แสดงการอัปเดตของ tickets และการมอบหมายงาน

**องค์ประกอบหลัก:**
1. **Summary Stats:**
   - จำนวนการแจ้งเตือนที่ยังไม่ได้อ่าน
   - ปุ่ม "ทำเครื่องหมายอ่านทั้งหมด"

2. **Filters:**
   - Filter by Read Status (ทั้งหมด/ยังไม่ได้อ่าน/อ่านแล้ว)
   - Filter by Type:
     - 🎫 Ticket ใหม่ (NEW_TICKET)
     - 👷 มอบหมายงาน (ASSIGNED)
     - 🔄 มอบหมายใหม่ (REASSIGNED)
     - 🔔 เปลี่ยนสถานะ (STATUS_CHANGE)
     - ✅ ปิดงาน (COMPLETED)
     - 🚨 เร่งด่วน (URGENT)
     - 💬 ข้อความ (COMMENT)
     - ⭐ ความคิดเห็น (FEEDBACK)

3. **Notification List:**
   - แต่ละการแจ้งเตือนแสดง:
     - Icon และ badge ตามประเภท
     - Badge "ใหม่" สำหรับยังไม่อ่าน
     - หัวข้อและข้อความ
     - Link ไปยัง ticket ที่เกี่ยวข้อง
     - Timestamp (วันที่/เวลา)
     - ปุ่มทำเครื่องหมายว่าอ่านแล้ว

4. **Navbar Notification Badge:**
   - ไอคอนกระดิ่งใน navbar
   - แสดงจำนวนการแจ้งเตือนที่ยังไม่ได้อ่าน (red badge)
   - คลิกเพื่อไปยัง notification center

**ฟีเจอร์:**
- ✅ Notification list view with pagination (50 items)
- ✅ Filter by read status (all/unread/read)
- ✅ Filter by notification type
- ✅ Icon and color coding by type
- ✅ Badge "ใหม่" for unread notifications
- ✅ Link to related ticket
- ✅ Mark single notification as read
- ✅ Mark all notifications as read
- ✅ Navbar notification bell with red badge counter
- ✅ Context processor for unread count
- ✅ Empty state when no notifications
- ✅ Timestamp display (created_at, read_at)

**Backend Integration:**
- ✅ Automatically create notifications for:
  - Ticket assigned to technician
  - Ticket accepted by technician
  - Ticket rejected by technician (reassignment)
  - Ticket completed by technician
  - Status changes

**ไฟล์:**
- `notify/views.py` - notification_list, mark_as_read, mark_all_as_read
- `notify/utils.py` - Notification helper functions
- `notify/context_processors.py` - Unread count for navbar
- `templates/notify/notification_list.html` - UI
- `templates/components/navbar.html` - Notification bell badge
- `tu_report/settings.py` - Context processor registration

---

### 9.3 แดชบอร์ด Admin (Admin Dashboard) ✅
**URL:** `/dashboard/`
**สิทธิ์:** Admin only
**สถานะ:** ✅ เสร็จสมบูรณ์

**วัตถุประสงค์:**
แดชบอร์ดสำหรับผู้ดูแลระบบ แสดงสถิติและรายงานแบบครบวงจร

**องค์ประกอบหลัก:**

**1. Overview Statistics Cards:**
- 📊 Total Tickets (ทั้งหมด)
- ⏳ Pending Tickets (รอดำเนินการ) - สีเหลือง
- 🔧 In Progress (กำลังดำเนินการ) - สีฟ้า
- ✅ Completed (เสร็จสิ้น) - สีเขียว

**2. Performance Metrics:**
- ⏱️ Average Response Time (เวลาตอบสนองเฉลี่ย)
  - คำนวณจากเวลาที่สร้าง ticket ถึงเวลาที่มอบหมายช่าง
  - แสดงเป็นชั่วโมง
- ⏲️ Average Completion Time (เวลาทำงานเสร็จเฉลี่ย)
  - คำนวณจากเวลาที่สร้างถึงเวลาที่เสร็จสิ้น
  - แสดงเป็นชั่วโมง
- ⭐ Average Overall Rating
  - คะแนนเฉลี่ยจาก feedback ทั้งหมด
  - จำนวน feedback ทั้งหมด

**3. Charts (Chart.js):**
- 📈 Tickets by Status (Pie Chart)
  - แสดงสัดส่วน PENDING/IN_PROGRESS/COMPLETED/REJECTED
  - Color-coded (เหลือง/ฟ้า/เขียว/แดง)
- 📊 Tickets by Category (Bar Chart)
  - แสดงจำนวน tickets แต่ละหมวดหมู่
  - เรียงจากมากไปน้อย

**4. Technician Performance Table:**
แสดงผลงานช่างแต่ละคนพร้อม:
- ชื่อช่าง (display name + username)
- งานที่รับ (assigned count)
- งานเสร็จ (completed count)
- อัตราสำเร็จ (completion rate %)
  - Progress bar visualization
  - เรียงจากมากไปน้อย
- คะแนนเฉลี่ย (average rating)
- สถานะพร้อมทำงาน (available/unavailable)
  - ✅ พร้อมรับงาน (สีเขียว)
  - ⏸️ หยุดรับงาน (สีเทา)

**5. Recent Activity (2 columns):**

**Column 1 - Recent Tickets:**
- แสดง 10 tickets ล่าสุด
- แต่ละ ticket แสดง:
  - Ticket #ID + Title (clickable)
  - Category | Created datetime
  - Status badge (color-coded)

**Column 2 - Recent Feedback:**
- แสดง 5 feedbacks ล่าสุด
- แต่ละ feedback แสดง:
  - Ticket #ID (clickable)
  - ชื่อช่างที่รับผิดชอบ
  - Overall rating (⭐ X/5)
  - Created date
  - Comment snippet (truncated 15 words)

**6. User Statistics:**
- 👥 Total Users (ผู้ใช้ทั้งหมด)
- 👷 Total Technicians (ช่างเทคนิค)
- 👤 Total Regular Users (ผู้ใช้ทั่วไป)

**ฟีเจอร์:**
- ✅ Comprehensive overview statistics
- ✅ Real-time performance metrics calculation
- ✅ Interactive charts (Chart.js v4.4.0)
- ✅ Technician performance comparison table
- ✅ Recent activity monitoring
- ✅ User statistics breakdown
- ✅ Responsive design (grid layout)
- ✅ Color-coded status indicators
- ✅ Clickable links to ticket details
- ✅ Permission-based access (admin only)

**การคำนวณ:**
- Response Time: ใช้ `updated_at - created_at` (sample 100 tickets)
- Completion Time: ใช้ `completed_at - created_at` (sample 100 tickets)
- Completion Rate: `(completed / assigned) * 100`
- Average Rating: `AVG(overall_rating)` per technician

**ไฟล์:**
- `dashboard/views.py` (dashboard_home) - Backend logic with statistics
- `templates/dashboard/admin_dashboard.html` - Complete UI with charts

---

### 10. Real-time Notifications ⚡ ✅
**URL:** WebSocket: `ws://host/ws/notifications/`
**สิทธิ์:** All logged-in users
**สถานะ:** ✅ เสร็จสมบูรณ์

**วัตถุประสงค์:**
แจ้งเตือนแบบ real-time ผ่าน WebSocket โดยไม่ต้อง refresh หน้า

**องค์ประกอบหลัก:**

**1. WebSocket Connection:**
- Auto-connect เมื่อโหลดหน้า
- Reconnect logic (max 5 attempts, delay 3s)
- Ping/pong keep-alive (ทุก 30 วินาที)
- Reconnect เมื่อ tab กลับมา visible

**2. Notification Display Methods:**

**A. Toast Notification (In-app):**
- แสดงมุมขวาบน (top-right)
- ใช้ animation slide-in/slide-out
- แสดง icon ตาม notification type
- แสดงหัวข้อ + ข้อความ
- ปุ่มปิด (X)
- Auto-dismiss หลัง 5 วินาที

**B. Browser Notification:**
- ขอ permission ครั้งแรก
- แสดงนอก browser window
- คลิกเพื่อ focus + ไปหน้า ticket
- รองรับ icon และ badge

**C. Badge Update:**
- อัปเดตจำนวน unread real-time
- อัปเดตที่ notification bell ใน navbar
- แสดง "99+" ถ้ามากกว่า 99

**3. Notification Types:**
แต่ละ type มี icon และสีต่างกัน:
- 🎫 NEW_TICKET - Ticket ใหม่
- 👷 ASSIGNED - มอบหมายงาน
- 🔄 REASSIGNED - มอบหมายใหม่
- 🔔 STATUS_CHANGE - เปลี่ยนสถานะ
- ✅ COMPLETED - เสร็จสิ้น
- 🚨 URGENT - เร่งด่วน
- 💬 COMMENT - ความคิดเห็น
- ⭐ FEEDBACK - คะแนน

**4. Connection Features:**
- Connection status logging (console)
- Error handling และ retry logic
- Graceful degradation (ถ้า WebSocket ไม่ทำงาน)
- Support both ws:// และ wss://

**Implementation Details:**

**Backend (Django Channels):**
- `notify/consumers.py` - NotificationConsumer
- `notify/routing.py` - WebSocket URL routing
- `tu_report/asgi.py` - ASGI application config
- `notify/utils.py` - ส่ง WebSocket message เมื่อสร้าง notification
- Channel layer: InMemoryChannelLayer (dev) / Redis (production)

**Frontend (JavaScript):**
- WebSocket client ใน `templates/base.html`
- Auto-connect และ reconnect logic
- Multiple display methods (toast, browser, badge)
- CSS animations (slide-in/out)
- Event handlers (onopen, onmessage, onclose, onerror)

**ฟีเจอร์:**
- ✅ Real-time notification delivery
- ✅ Multiple display methods
- ✅ Auto-reconnect on disconnect
- ✅ Ping/pong keep-alive
- ✅ Badge counter update
- ✅ Browser notification support
- ✅ Toast notification with animations
- ✅ Connection status monitoring
- ✅ Error handling

**Production Deployment:**
- ต้องใช้ Daphne แทน Gunicorn: `daphne tu_report.asgi:application`
- แนะนำใช้ Redis สำหรับ channel layer
- Configure Nginx สำหรับ WebSocket proxy
- ตั้งค่า `CHANNEL_LAYERS` ใน settings.py

**ไฟล์:**
- `notify/consumers.py` - WebSocket consumer
- `notify/routing.py` - WebSocket routing
- `tu_report/asgi.py` - ASGI configuration
- `tu_report/settings.py` - Channels configuration
- `notify/utils.py` - Send WebSocket messages
- `templates/base.html` - WebSocket client JavaScript
- `requirements.txt` - channels, channels-redis, daphne

---

### 11. โปรไฟล์ (User Profile) ✅
**URL:** `/profile/`
**สิทธิ์:** All logged-in users
**สถานะ:** ✅ เสร็จบางส่วน (View only)

**วัตถุประสงค์:**
แสดงข้อมูลโปรไฟล์ผู้ใช้

**องค์ประกอบหลัก:**
1. **Avatar** - แสดงตัวอักษรแรกของ username
2. **User Info:**
   - Display Name (TH/EN)
   - Username
   - Email
   - Role badge (User/Technician/Admin)
   - Auth provider
3. **Personal Info:**
   - Faculty/Department/Organization
4. **Account Info:**
   - Created at
   - Updated at
   - Last login
5. **Statistics:**
   - สำหรับ User: tickets created, pending, completed
   - สำหรับ Technician: jobs assigned, in progress, completed
6. **Action Buttons:**
   - แก้ไขโปรไฟล์ (TODO)
   - ตั้งค่าความปลอดภัย (TODO)
   - ตั้งค่าทั่วไป (TODO)

**ฟีเจอร์:**
- ✅ แสดงข้อมูลโปรไฟล์
- ✅ แสดง role badge
- ✅ แสดงสถิติ (ยังไม่ทำงาน)
- 🚧 แก้ไขโปรไฟล์ (TODO)
- 🚧 Upload avatar (TODO)
- 🚧 Security settings (TODO)

**ไฟล์:**
- `templates/profile/view.html`

---

### 11. Django Admin Panel ✅
**URL:** `/admin/`
**สิทธิ์:** Superuser
**สถานะ:** ✅ เสร็จสมบูรณ์

**วัตถุประสงค์:**
จัดการระบบทั้งหมดผ่าน Django Admin

**Models ที่ Register แล้ว:**
- ✅ User
- ✅ LoginLog
- ✅ Category
- ✅ Department
- ✅ Ticket (GISModelAdmin)
- ✅ TicketStatusHistory
- ✅ Attachment
- ✅ TechnicianPresence
- ✅ AssignmentRule
- ✅ TicketFeedback (with detailed fieldsets)
- ✅ BeforeAfterPhoto (with file size tracking)

**ฟีเจอร์:**
- ✅ CRUD operations สำหรับทุก models
- ✅ List display with important fields
- ✅ List filters
- ✅ Search fields
- ✅ Custom fieldsets (Feedback, BeforeAfterPhoto)
- ✅ GIS widget สำหรับ Ticket location
- ✅ Readonly fields (timestamps, file sizes)

---

## บทบาทผู้ใช้และสิทธิ์การเข้าถึง

### ตารางสิทธิ์การเข้าถึง

| หน้า/ฟีเจอร์ | Public | User | Technician | Admin | Superuser |
|-------------|:------:|:----:|:----------:|:-----:|:---------:|
| **Authentication** |
| Login | ✅ | ✅ | ✅ | ✅ | ✅ |
| Logout | ❌ | ✅ | ✅ | ✅ | ✅ |
| **Tickets** |
| My Tickets List | ❌ | ✅ | ✅ | ✅ | ✅ |
| Create Ticket + GPS + Photo | ❌ | ✅ | ❌ | ✅ | ✅ |
| View Ticket Detail | ❌ | ✅* | ✅** | ✅ | ✅ |
| Edit Ticket | ❌ | ✅* | ❌ | ✅ | ✅ |
| Cancel Ticket | ❌ | ✅* | ❌ | ✅ | ✅ |
| Submit Feedback | ❌ | ✅* | ❌ | ❌ | ✅ |
| **Technician** |
| Job List | ❌ | ❌ | ✅ | ❌ | ✅ |
| Accept Job | ❌ | ❌ | ✅** | ❌ | ✅ |
| Reject Job + Reassign | ❌ | ❌ | ✅** | ❌ | ✅ |
| Update Status | ❌ | ❌ | ✅** | ❌ | ✅ |
| Complete + After Photo | ❌ | ❌ | ✅** | ❌ | ✅ |
| Toggle Availability | ❌ | ❌ | ✅ | ❌ | ✅ |
| **Notifications** |
| View Notifications | ❌ | ✅ | ✅ | ✅ | ✅ |
| Mark as Read | ❌ | ✅ | ✅ | ✅ | ✅ |
| Mark All as Read | ❌ | ✅ | ✅ | ✅ | ✅ |
| **Admin** |
| Dashboard | ❌ | ❌ | ❌ | ✅ | ✅ |
| Reports | ❌ | ❌ | ❌ | 🚧 | ✅ |
| **Profile** |
| View Profile | ❌ | ✅ | ✅ | ✅ | ✅ |
| Edit Profile | ❌ | 🚧 | 🚧 | 🚧 | ✅ |
| **System** |
| Django Admin | ❌ | ❌ | ❌ | ❌ | ✅ |

**สัญลักษณ์:**
- ✅ = เข้าถึงได้เต็มที่
- ✅* = เฉพาะของตัวเอง (own tickets)
- ✅** = เฉพาะที่ได้รับมอบหมาย (assigned tickets)
- 🚧 = ยังไม่เสร็จ (TODO)
- ❌ = ไม่สามารถเข้าถึง

---

## ฟีเจอร์ที่เสร็จสมบูรณ์

### ✅ Priority 1 - Critical Features (100%)

#### 1. GPS Auto-Capture + Before Photo ✅
**Files:**
- `templates/user/create_ticket.html`
- `tickets/views.py` (create_ticket)

**Features:**
- GPS button with Geolocation API
- Auto-capture current location
- Click map to select location
- Before photo upload (required)
- Photo preview with FileReader
- Saves to BeforeAfterPhoto model (photo_type='BEFORE')

#### 2. After Photo + Complete Job ✅
**Files:**
- `templates/technician/complete_job.html`
- `technician/views.py` (complete_job)

**Features:**
- After photo upload (required)
- Photo preview
- Comment field
- Updates status to COMPLETED
- Records completion timestamp
- Creates TicketStatusHistory

#### 3. Feedback/Rating Form ✅
**Files:**
- `templates/tickets/feedback_form.html`
- `tickets/views.py` (submit_feedback)

**Features:**
- Interactive star rating (1-5)
- Overall rating (required)
- Detailed ratings (optional): response speed, work quality, politeness, cleanliness
- Comment field (max 500 chars)
- Validation: only COMPLETED/CLOSED tickets
- Prevents duplicate feedback (OneToOneField)

#### 4. Reject Job + Auto Reassign ✅
**Files:**
- `technician/views.py` (reject_job)

**Features:**
- Unassigns current technician
- Records rejection in TicketStatusHistory
- Calls auto_dispatch_ticket() for reassignment
- Shows success if reassigned
- Shows warning if no available technician

---

### ✅ Priority 4 - Security Features (100%)

#### 1. Session Security ✅
**Files:**
- `tu_report/settings.py`

**Settings:**
- SESSION_COOKIE_AGE = 86400 (24 hours)
- SESSION_SAVE_EVERY_REQUEST = True
- SESSION_COOKIE_HTTPONLY = True
- SESSION_COOKIE_SAMESITE = 'Lax'
- SESSION_COOKIE_NAME = 'tu_report_sessionid'

#### 2. Prevent Back Button After Logout ✅
**Files:**
- `authentication/middleware.py` (NoCacheAfterLogoutMiddleware, SessionSecurityMiddleware)
- `authentication/views.py` (logout_view)
- `tu_report/settings.py` (MIDDLEWARE)

**Features:**
- Sets Cache-Control headers (no-cache, no-store, must-revalidate)
- Flushes session on logout
- Middleware validates session
- Prevents back button navigation

#### 3. CSRF Protection ✅
**Files:**
- `tu_report/settings.py`

**Settings:**
- CSRF_COOKIE_HTTPONLY = True
- CSRF_COOKIE_SAMESITE = 'Lax'
- CSRF_COOKIE_NAME = 'tu_report_csrftoken'

#### 4. Security Headers ✅
**Files:**
- `tu_report/settings.py`

**Production Settings:**
- SECURE_SSL_REDIRECT = True
- SESSION_COOKIE_SECURE = True
- CSRF_COOKIE_SECURE = True
- SECURE_BROWSER_XSS_FILTER = True
- SECURE_CONTENT_TYPE_NOSNIFF = True
- X_FRAME_OPTIONS = 'DENY'
- SECURE_HSTS_SECONDS = 31536000 (1 year)
- SECURE_HSTS_INCLUDE_SUBDOMAINS = True
- SECURE_HSTS_PRELOAD = True

#### 5. Login Required Middleware ✅
**Files:**
- `authentication/middleware.py` (LoginRequiredMiddleware)

**Features:**
- Forces login before accessing any page
- Exempt URLs: /login/, /logout/, /static/, /media/, /admin/

---

## 🚧 ฟีเจอร์ที่ยังไม่เสร็จ

### Priority 2 - Important Features

#### 1. Notification System 🚧
- In-app notifications
- Notify on ticket assign, status change, accept/reject
- Notification badge/counter
- Mark as read

#### 2. Admin Dashboard 🚧
- Overall statistics
- Technician performance metrics
- Feedback reports
- Before/After photo gallery
- Charts/graphs

#### 3. Technician Availability Toggle 🚧
- Toggle button in technician UI
- Update TechnicianPresence.is_available
- Auto-dispatch respects availability

#### 4. Edit/Cancel Ticket 🚧
- Edit ticket (PENDING only)
- Cancel ticket (PENDING/IN_PROGRESS)
- Record changes in history

### Priority 3 - Nice to Have

#### 5. Search & Filter 🚧
- Search tickets
- Filter by status, category, date
- Sort options

#### 6. Export Reports 🚧
- Export to PDF/Excel
- Monthly reports
- Download photos as ZIP

#### 7. Profile Features 🚧
- Upload avatar
- Edit profile info
- Change password
- Two-Factor Authentication

#### 8. Real-time Updates 🚧
- WebSocket support (Django Channels)
- Live notifications
- Live status updates

---

## เทคโนโลยีที่ใช้

### Backend
- **Framework:** Django 5.2.6
- **GIS Extension:** GeoDjango (django.contrib.gis)
- **Database:** PostgreSQL 15 + PostGIS 3.3
- **GIS Libraries:** GDAL 3.11+, GEOS
- **Authentication:** Session-based (Django Sessions)
- **API:** TU REST API (Mock + Real)
- **File Storage:** Local media files (configurable to S3)

### Frontend
- **HTML5:** Semantic markup
- **CSS:** Tailwind CSS 3.x
- **JavaScript:** Vanilla JS + Alpine.js (if needed)
- **Maps:** Leaflet.js 1.9+ with OpenStreetMap
- **Charts:** Chart.js (for dashboard)
- **Icons:** Emoji + Font Awesome (optional)

### Database Features
- **Spatial Index:** PostGIS GIST index on location fields
- **SRID:** 4326 (WGS84 - GPS standard)
- **Point Fields:** Geography type for accurate distance calculation
- **Distance Calculation:** PostGIS ST_Distance (Geodesic Haversine)

### Auto-Dispatch Algorithm
```python
# Priority Score
priority_score = urgency_weight (40%) + category_weight (30%) + density (30%)

# Technician Score
tech_score = distance_weight (60%) + workload_weight (40%)

# Find best technician
best_tech = min(available_technicians, key=lambda t: tech_score(t))
```

### Security Features
- Session timeout: 24 hours
- CSRF protection enabled
- XSS protection enabled
- Clickjacking protection (X-Frame-Options: DENY)
- HTTPS enforced (production)
- HSTS configured (production)
- HttpOnly cookies
- SameSite cookies (Lax)
- Back button prevention after logout

---

## ข้อมูลเวอร์ชัน

- **Project Version:** 1.0.0
- **Django Version:** 5.2.6
- **Database:** PostgreSQL 15 + PostGIS 3.3
- **Python:** 3.10+
- **Last Updated:** 2025-11-02
- **Institution:** Thammasat University

---

## เอกสารที่เกี่ยวข้อง

- **Implementation Status:** [IMPLEMENTATION_STATUS.md](../IMPLEMENTATION_STATUS.md)
- **Render Deployment:** [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md)
- **GDAL Installation:** [INSTALL_GDAL_WINDOWS.md](INSTALL_GDAL_WINDOWS.md)
- **Project README:** [README.md](../README.md)

---

> 🎓 **TU REPORT** - ระบบแจ้งซ่อมอัจฉริยะ
> พัฒนาสำหรับมหาวิทยาลัยธรรมศาสตร์
> พร้อมระบบมอบหมายอัตโนมัติและฟีเจอร์ GIS เต็มรูปแบบ
