# TU REPORT - Ticket & Auto Dispatcher System

ระบบแจ้งปัญหาและจัดการซ่อมบำรุงภายในมหาวิทยาลัยธรรมศาสตร์

## 🚀 Quick Start

### 1. Clone และ Setup

```bash
# Clone repository
cd C:\Users\PC\Documents\331\PROJECT

# สร้าง virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt
```

### 2. Setup Database (PostgreSQL + PostGIS)

```bash
# ติดตั้ง PostgreSQL และ PostGIS extension
# Windows: Download จาก https://www.postgresql.org/download/windows/
# PostGIS: https://postgis.net/install/

# สร้าง database
createdb tu_report

# เปิด psql และเพิ่ม PostGIS extension
psql -d tu_report
CREATE EXTENSION postgis;
\q
```

### 3. Configure Environment

```bash
# Copy .env.example เป็น .env
copy .env.example .env  # Windows
# cp .env.example .env  # Mac/Linux

# แก้ไข .env file:
# DATABASE_URL=postgresql://postgres:your_password@localhost:5432/tu_report
```

### 4. Run Migrations

```bash
# สร้าง migrations
python manage.py makemigrations authentication
python manage.py makemigrations tickets

# รัน migrations
python manage.py migrate

# Load initial data (Categories, Assignment Rules)
python manage.py loaddata fixtures/initial_data.json
```

### 5. Create Superuser

```bash
python manage.py createsuperuser
# Username: admin
# Email: admin@tu.ac.th
# Password: (your secure password)
```

### 6. Run Development Server

```bash
python manage.py runserver

# เปิดเบราว์เซอร์: http://localhost:8000
# Admin panel: http://localhost:8000/admin
```

---

## 📁 Project Structure

```
tu_report/
├── authentication/         # User authentication & TU API integration
│   ├── models.py          # User, LoginLog models
│   ├── utils/
│   │   └── mock_tu_api.py # Mock TU API functions
│   └── views.py           # Login/Logout views
├── tickets/               # Ticket management
│   ├── models.py          # Ticket, Category, Attachment models
│   ├── dispatcher.py      # Auto Dispatcher logic (Part 3)
│   └── views.py           # Ticket CRUD views
├── dashboard/             # Admin dashboard
│   └── views.py
├── technician/            # Technician job management
│   └── views.py
├── tu_report/             # Main project settings
│   ├── settings.py
│   └── urls.py
├── templates/             # HTML templates (Part 2)
├── static/               # CSS, JS, images
├── media/                # Uploaded files
├── fixtures/             # Initial data
└── manage.py
```

---

## 🔧 Part 1 Checklist (COMPLETED ✅)

```
✅ Django project structure
✅ settings.py configured
✅ User model (authentication/models.py)
✅ Ticket models (tickets/models.py)
✅ Category, Department, LoginLog models
✅ TechnicianPresence & AssignmentRule models
✅ Admin interfaces
✅ Initial data fixtures
✅ requirements.txt
✅ .env.example
✅ .gitignore
✅ Procfile & render.yaml
```

---

## 📝 Next Steps

### Part 2: Views + Templates
```bash
# จะสร้าง:
- Login page (TU API + Local)
- User page (Create ticket, My tickets)
- Technician page (Job list, Update status)
- Admin Dashboard
- Base templates + Components
```

### Part 3: Auto Dispatcher + Testing
```bash
# จะสร้าง:
- Auto Dispatcher logic (tickets/dispatcher.py)
- Test suite (≥80% coverage)
- Demo data command
```

---

## 🗄️ Database Models

### User (authentication/models.py)
- Custom user model รองรับ TU API และ Local authentication
- Fields: username, role, auth_provider, displayname_th, faculty, department, etc.

### Ticket (tickets/models.py)
- Ticket แจ้งปัญหา พร้อม PostGIS location
- Status workflow: PENDING → IN_PROGRESS → WORKING → COMPLETED → CLOSED
- Priority scoring system

### Category
- หมวดหมู่: ไฟฟ้า, ประปา, IT, แอร์, อาคาร

### AssignmentRule
- กฎการมอบหมายงานอัตโนมัติ
- max_open_tickets, weight_distance, weight_workload

---

## 🔑 Mock Users (TU API)

สามารถใช้ mock users เหล่านี้สำหรับทดสอบ:

**Students:**
- Username: `student001` | Password: `student123`
- Username: `6501234567` | Password: `demo123`

**Employees:**
- Username: `staff001` | Password: `staff123`
- Username: `tech_admin` | Password: `admin123`

---

## 🐛 Troubleshooting

### PostGIS ไม่ทำงาน
```bash
# ตรวจสอบว่า PostGIS extension ถูกติดตั้ง
psql -d tu_report -c "SELECT PostGIS_version();"

# ถ้ายังไม่มี ให้ติดตั้ง:
psql -d tu_report -c "CREATE EXTENSION postgis;"
```

### Migration Errors
```bash
# ลบ migrations และสร้างใหม่
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete

python manage.py makemigrations
python manage.py migrate
```

### Static Files ไม่แสดง
```bash
python manage.py collectstatic --noinput
```

---

## 📞 Support

- Documentation: [detail.txt](detail.txt)
- API Documentation: [APIdetail.txt](APIdetail.txt)
- UI Components: [UI_COMPONENTS_GUIDE.md](UI_COMPONENTS_GUIDE.md)

---

**Version:** 1.0.0 (Part 1 Complete)
**Author:** TestTer
**Framework:** Django 5.0 + PostGIS + TailwindCSS
