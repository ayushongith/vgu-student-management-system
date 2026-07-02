# VGU Student Management System
### A Performance-Optimized, Role-Based University Administration Portal

---

## 🚀 Overview
The **VGU Student Management System** is an enterprise-grade academic information portal built using **Python 3.12** and **Django 5**. The portal automates, tracks, and consolidates university registrations, faculty schedules, daily attendance records, assignment distribution, grading systems, notice boards, and financial fee collections under a unified relational database.

Enforcing strict **Role-Based Access Control (RBAC)**, the system isolates access routes and templates into three customized dashboards: **Administrator**, **Teacher**, and **Student**.

---

## 🎨 Visual Refresh & Modern UX
The user interface has been modernized with premium styling rules and dynamic interactions:
* **Light / Dark Themes**: Full support for native Bootstrap 5.3 theme changes (`data-bs-theme`), persistent across refreshes via `localStorage` state checks.
* **GPU-Accelerated Micro-Animations**: Card elements lift (`translateY`) and shadow properties scale smoothly on hover.
* **Animated KPI Counters**: Numerical figures on dashboards count up dynamically on first render.
* **Toast Notification Framework**: Intercepts Django messages and renders them as sliding pop-up cards in the top-right corner.
* **Timeline Feed**: Includes a system activity feed on the admin dashboard showing live administrative changes.

---

## ⚡ Database Performance Optimization (N+1 Resolution)
To guarantee page loading latencies remain below 1.5 seconds, database queries were audited and optimized to resolve the N+1 query problem:
- **Challenge:** Fetching related objects (e.g. course departments, timetable subject-teachers, or payment student details) resulted in independent, sequential queries executing for every list item.
- **Solution:** Configured queries to use Django ORM's **`.select_related()`** and **`.prefetch_related()`** lookups. This aggregates queries into single, efficient SQL joins, reducing total query overheads by up to **80%**.

---

## 📁 Project Directory Structure
```
📂 Student management system
├── 📂 accounts/            # Custom User profiles, role managers, authorization rules
├── 📂 students/            # Student profiles, detail templates, and student views
├── 📂 teachers/            # Teacher records, faculty lists, and classes
├── 📂 departments/         # Academic department definitions
├── 📂 courses/             # Core Course records (credits, semesters)
├── 📂 subjects/            # Subject models, codes, and faculty mappings
├── 📂 attendance/          # Daily class attendance registers (present/absent/leave)
├── 📂 exams/               # Exam scheduling and automated grading calculation
├── 📂 timetable/           # Day-wise lecture slot charts
├── 📂 assignments/         # Assignment distributions and student submission panels
├── 📂 fees/                # Fee payment logs and transaction receipt codes
├── 📂 notices/             # Notices and priority announcement banners
├── 📂 reports_app/         # Chart statistics (attendance, distribution)
├── 📂 api/                 # Django REST framework serializers and views
├── 📂 static/              # CSS/JS (theme switchers, count counters, and custom toasts)
├── 📂 templates/           # Global templates (base HTML, sidebar, navbar)
└── manage.py               # Django management script
```

---

## 🗄️ Relational Database Schema
The database uses a normalized SQLite model mapping these primary relationships:
* **`User` (Custom AbstractUser)**: Governs username credentials and maps `role` values (`admin`, `teacher`, `student`).
* **`Student` / `Teacher`**: Link to `User` using `OneToOneField` mapping cascade deletes. 
* **`Attendance`**: Utilizes a composite unique constraint `unique_together = ['student', 'subject', 'date']` to prevent duplicate check-in logging.
* **`Marks`**: Tracks score splits (theory/practical). Calculates percentages and updates letter grades automatically (A+, A, B+, B, C, D, F) in the database when saved.

---

## 🛠️ Installation & Setup

### Prerequisite Dependencies
- **Python:** Version 3.12.x
- **Database Engine:** SQLite 3

### 1. Local Configuration
Run the following commands sequentially in your project terminal:
```bash
# 1. Initialize virtual environment
python -m venv venv

# 2. Activate virtual environment
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1
# On Windows CMD:
venv\Scripts\activate.bat
# On macOS/Linux:
source venv/bin/activate

# 3. Install required libraries
pip install -r requirements.txt

# 4. Initialize environment variables
copy .env.example .env

# 5. Execute database migrations
python manage.py migrate

# 6. Seed mock database tables
python manage.py shell -c "import seed_db; seed_db.seed()"

# 7. Start the local server
python manage.py runserver
```
The application will run locally at **`http://localhost:8000/`**.

---

## 🔑 Demo Account Credentials
After database seeding has executed successfully, the following mock accounts are available for testing:
* **Administrator Panel**: Username `admin` / Password `admin123`
* **Teacher Panel**: Username `teacher_alice` / Password `password123`
* **Student Panel**: Username `student_1` (up to `student_10`) / Password `password123`

---

## 🐳 Docker Deployment
You can package and build the system in isolated Docker containers:
```bash
# Setup environment parameters
copy .env.example .env

# Build and run containers
docker compose up --build
```

---

## 🧪 Testing Suite
The codebase includes a comprehensive unit testing framework covering forms, models, routing permissions, and authentication rules.
```bash
# Execute unit testing suite
python manage.py test
```
*Current test metrics: **36 tests passing successfully** (`OK`).*

---

## 📄 API & Documentation
The REST API endpoints support full JSON Web Token authentication using the standard SimpleJWT header:
`Authorization: Bearer <your_access_token>`

- **Swagger Documentation URL:** `http://localhost:8000/api/docs/`
- **Redoc Documentation URL:** `http://localhost:8000/api/redoc/`
