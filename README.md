<div align="center">

# 🍽️ Smart Food Court Management System

**A full-stack web application for managing food court operations in real time**

[![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-black?style=for-the-badge&logo=flask)](https://flask.palletsprojects.com)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-orange?style=for-the-badge&logo=mysql)](https://mysql.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32-red?style=for-the-badge&logo=streamlit)](https://streamlit.io)
[![Railway](https://img.shields.io/badge/Deployed_on-Railway-purple?style=for-the-badge&logo=railway)](https://railway.app)

[🌐 Live Demo](https://food-court-management-production.up.railway.app) • [📊 Features](#-features) • [🚀 Setup](#-local-setup) • [📱 Screenshots](#-portals)

</div>

---

## 📌 About

A **Smart Food Court Management System** that digitizes the entire food ordering workflow — from customer ordering to vendor fulfillment to admin oversight — all in real time.

Built as a complete full-stack project with:
- **3 role-based portals** — Customer, Vendor, Admin
- **Real-time order tracking** with token system
- **Analytics dashboard** with AI-powered food recommendations
- **Cloud deployed** on Railway

---

## ✨ Features

### 👤 Customer Portal
- Browse menu across all vendors with filters (veg, spicy, price)
- Add to cart with quantity controls
- Auto discount (10%) on orders above ₹400
- Place order → get unique token number
- Track order live — Pending → Preparing → Ready → Collected
- View order history and account stats

### 🏪 Vendor Portal
- Live incoming orders dashboard
- Advance order status with one click
- Menu management (add, edit, toggle availability)
- Today's revenue and sales stats
- Queue management view

### 🔐 Admin Portal
- Overview of all vendors and orders
- Revenue charts and weekly trends
- Best-selling items analysis
- Live queue status across all vendors
- System alerts and notifications

### 📊 Analytics Dashboard (Streamlit)
- **Customer Segmentation** — 🐋 Whale, 🔄 Regular, 🆕 New, 😴 Inactive
- **Vendor Scorecard** — Score out of 100 based on revenue, orders, completion
- **Food Recommendations** — Market Basket Analysis (what items are ordered together)
- **Reports** — Download PDF and Excel reports by date range

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | HTML, CSS, JavaScript |
| **Backend** | Python, Flask, Flask-JWT, Flask-Bcrypt |
| **Database** | MySQL, SQLAlchemy ORM |
| **Analytics** | Streamlit, Pandas, Reportlab, Openpyxl |
| **Auth** | JWT Tokens, Bcrypt password hashing |
| **Deployment** | Railway (app + database) |
| **Version Control** | Git, GitHub |

---

## 📱 Portals

### Login Page
Clean login and register interface with role-based redirection

### Customer Portal
Menu browsing → Cart → Token → Live tracking

### Vendor Portal  
Live orders → Status management → Menu control

### Admin Portal
Full oversight → Revenue → Analytics → Alerts

---

## 🏗️ Architecture

```
Browser (HTML/CSS/JS)
        ↕  REST API (JSON)
Flask Backend (Python)
        ↕  SQLAlchemy ORM
   MySQL Database
        
Streamlit Analytics (separate service)
        ↕
   Same MySQL Database
```

---

## 🔄 Order Flow

```
Customer places order
        ↓
Token number generated (#45)
        ↓
Vendor sees → PENDING
        ↓  (clicks Start)
Vendor sees → PREPARING
        ↓  (clicks Ready)
Customer notified → READY
        ↓  (customer collects)
Vendor clicks → COLLECTED ✅
```

---

## 📁 Project Structure

```
food-court-management/
├── app.py                  ← Flask entry point
├── config.py               ← Configuration & DB settings
├── extensions.py           ← SQLAlchemy models
├── analytics.py            ← Streamlit dashboard
├── requirements.txt        ← Python dependencies
├── Procfile                ← Railway deployment
├── api/
│   ├── auth.py             ← Login/Register API
│   ├── menu.py             ← Menu API
│   ├── orders.py           ← Orders API
│   ├── vendor.py           ← Vendor API
│   └── admin.py            ← Admin API
├── static/
│   └── js/
│       └── api.js          ← Frontend API client
├── login.html              ← Login & Register
├── customer.html           ← Customer portal
├── vendor.html             ← Vendor portal
└── admin.html              ← Admin portal
```

---

## 🚀 Local Setup

### Prerequisites
- Python 3.9+
- XAMPP (for local MySQL)
- Git

### Steps

**1. Clone the repository**
```bash
git clone https://github.com/Akshanth07/food-court-management.git
cd food-court-management
```

**2. Create virtual environment**
```bash
python -m venv venv
venv\Scripts\activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
pip install streamlit pandas openpyxl reportlab
```

**4. Start XAMPP MySQL and create database**
- Open XAMPP → Start MySQL
- Open phpMyAdmin → create database `foodcourt_db`
- Run `database.sql` in the SQL tab

**5. Run Flask app**
```bash
python app.py
```
Open → `http://localhost:5000`

**6. Run Analytics dashboard (separate terminal)**
```bash
streamlit run analytics.py
```
Open → `http://localhost:8501`

---

## 🔑 Demo Credentials

| Role | Email | Password |
|------|-------|----------|
| 👑 Admin | admin@foodcourt.com | password123 |
| 🍛 Spice Garden | ravi@spicegarden.com | password123 |
| 🍔 Quick Bites | priya@quickbites.com | password123 |
| 🍔 Burger Barn | burger@barnfood.com | password123 |
| 🍜 Wok and Roll | wok@rollfood.com | password123 |
| 👤 Customer | customer@test.com | password123 |

---

## 🔗 API Endpoints

### Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/auth/login | Login → returns JWT |
| POST | /api/auth/register | Register new user |
| GET | /api/auth/me | Get current user |

### Menu
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/menu/vendors | All vendors |
| GET | /api/menu/items | All menu items |

### Orders
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/orders/place | Place new order |
| GET | /api/orders/my | Order history |
| GET | /api/orders/token/{token} | Track by token |

### Vendor
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/vendor/orders | Live orders |
| POST | /api/vendor/orders/{id}/status | Update status |
| GET | /api/vendor/stats | Revenue & KPIs |

### Admin
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/admin/stats | Overall stats |
| GET | /api/admin/revenue/weekly | Weekly revenue |
| GET | /api/admin/vendors | Vendor performance |

---

## 🌐 Live Deployment

The app is deployed on **Railway** with a cloud MySQL database.

🔗 **Live URL:** https://food-court-management-production.up.railway.app

---

## 👨‍💻 Developer

**Akshanth** — Full Stack Developer

---

<div align="center">
Made with ❤️ using Python, Flask, and MySQL
</div>
