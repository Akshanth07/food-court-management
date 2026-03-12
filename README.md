# 🍽 Smart Food Court Management System
## Setup Guide — Flask + MySQL + XAMPP

---

## 📁 Project Structure

```
foodcourt/
├── app.py                  ← Flask entry point (run this)
├── config.py               ← DB credentials & settings
├── extensions.py           ← SQLAlchemy models
├── requirements.txt        ← Python packages
├── database.sql            ← Run this in phpMyAdmin first
├── api/
│   ├── auth.py             ← /api/auth/*
│   ├── menu.py             ← /api/menu/*
│   ├── orders.py           ← /api/orders/*
│   ├── vendor.py           ← /api/vendor/*
│   └── admin.py            ← /api/admin/*
├── static/
│   └── js/
│       └── api.js          ← Shared API client (include in all pages)
├── login.html              ← Login/Register page
├── customer.html           ← Customer portal
├── vendor.html             ← Vendor dashboard
└── admin.html              ← Admin dashboard
```

---

## ✅ Step 1 — Start XAMPP

1. Open **XAMPP Control Panel**
2. Start **Apache** and **MySQL**
3. Open **phpMyAdmin** at `http://localhost/phpmyadmin`

---

## ✅ Step 2 — Create the Database

1. In phpMyAdmin, click **"New"** in the left sidebar
2. Create a database called `foodcourt_db`
3. Click the **SQL** tab
4. Open `database.sql`, copy ALL contents, paste and click **Go**
5. You should see all tables created with sample data ✓

---

## ✅ Step 3 — Install Python & Dependencies

Make sure Python 3.9+ is installed. Then in your terminal:

```bash
# Navigate into the project folder
cd foodcourt

# (Recommended) create a virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install all required packages
pip install -r requirements.txt
```

---

## ✅ Step 4 — Configure Database Credentials

Open `config.py` and check these lines:

```python
MYSQL_USER     = 'root'      # XAMPP default
MYSQL_PASSWORD = ''          # XAMPP default = empty password
MYSQL_DB       = 'foodcourt_db'
MYSQL_HOST     = 'localhost'
```

> If you set a MySQL password in XAMPP, update `MYSQL_PASSWORD` here.

---

## ✅ Step 5 — Run the Flask Server

```bash
python app.py
```

You should see:
```
 * Running on http://0.0.0.0:5000
 * Debug mode: on
```

Test it: open `http://localhost:5000` in your browser → should show API is running ✓

---

## ✅ Step 6 — Open the Frontend

Open `login.html` directly in your browser, OR serve it via XAMPP:

**Option A (simple — just double-click):**
Open `login.html` in Chrome/Firefox directly.

**Option B (via XAMPP Apache — recommended):**
1. Copy the entire `foodcourt/` folder into `C:\xampp\htdocs\`
2. Open `http://localhost/foodcourt/login.html`

---

## 🔑 Demo Login Credentials

| Role     | Email                        | Password    |
|----------|------------------------------|-------------|
| Admin    | admin@foodcourt.com          | password123 |
| Vendor 1 | ravi@spicegarden.com         | password123 |
| Vendor 2 | priya@burgerbarn.com         | password123 |
| Customer | customer@test.com            | password123 |

---

## 🔗 API Endpoints Summary

### Auth
| Method | Endpoint              | Description         |
|--------|-----------------------|---------------------|
| POST   | /api/auth/login       | Login → returns JWT |
| POST   | /api/auth/register    | Register new user   |
| GET    | /api/auth/me          | Get current user    |

### Menu (Public)
| Method | Endpoint              | Description         |
|--------|-----------------------|---------------------|
| GET    | /api/menu/vendors     | All open vendors    |
| GET    | /api/menu/items       | All menu items      |
| GET    | /api/menu/items?vendor_id=1 | Filter by vendor |

### Orders (Customer)
| Method | Endpoint              | Description         |
|--------|-----------------------|---------------------|
| POST   | /api/orders/place     | Place new order     |
| GET    | /api/orders/my        | My order history    |
| GET    | /api/orders/token/47  | Track by token      |

### Vendor Dashboard
| Method | Endpoint                          | Description          |
|--------|-----------------------------------|----------------------|
| GET    | /api/vendor/orders                | Live incoming orders |
| POST   | /api/vendor/orders/{id}/status    | Update item status   |
| GET    | /api/vendor/stats                 | Revenue & KPIs       |
| POST   | /api/vendor/menu                  | Add menu item        |

### Admin Dashboard
| Method | Endpoint                   | Description          |
|--------|----------------------------|----------------------|
| GET    | /api/admin/stats           | Overall KPIs         |
| GET    | /api/admin/revenue/weekly  | 7-day revenue chart  |
| GET    | /api/admin/vendors         | Vendor performance   |
| GET    | /api/admin/bestsellers     | Top selling items    |
| GET    | /api/admin/queue           | Live queue status    |
| GET    | /api/admin/alerts          | System alerts        |

---

## 🛠 Troubleshooting

**CORS error in browser?**
→ Make sure Flask is running on port 5000 and Flask-CORS is installed.

**MySQL connection refused?**
→ Start MySQL in XAMPP Control Panel.

**ModuleNotFoundError?**
→ Run `pip install -r requirements.txt` again with venv activated.

**Token not working?**
→ Clear localStorage in browser DevTools → Console: `localStorage.clear()`
