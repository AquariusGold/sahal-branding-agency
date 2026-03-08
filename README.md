# SAHAL Branding Agency — Flask Backend

A **production-ready Flask web application** with device-aware frontend rendering, MySQL database, and modular Blueprint architecture.

---

## 🏗️ Architecture Overview

| Layer | Technology |
|---|---|
| Backend Framework | Flask 3.x |
| ORM | Flask-SQLAlchemy |
| Migrations | Flask-Migrate (Alembic) |
| Authentication | Flask-Login *(Phase 2)* |
| Email | Flask-Mail *(Phase 3)* |
| Database | MySQL via PyMySQL |
| Forms | Flask-WTF + WTForms |
| Frontend | Bootstrap 5.3 + Jinja2 |
| Device Detection | User-Agent header matching |

---

## 📁 Project Structure

```
sahal_branding_agency/
├── app/
│   ├── __init__.py          # Application factory (create_app)
│   ├── config.py            # Dev / Test / Prod config classes
│   ├── extensions.py        # db, migrate, login_manager, mail
│   ├── models/
│   │   └── __init__.py      # TestConnection model (smoke-test)
│   ├── utils/
│   │   └── device.py        # is_mobile(request) utility
│   ├── auth/                # Blueprint: /auth
│   ├── main/                # Blueprint: / (homepage)
│   ├── services/            # Blueprint: /services
│   ├── admin/               # Blueprint: /admin
│   ├── templates/
│   │   ├── desktop/home.html
│   │   └── mobile/home.html
│   └── static/
├── run.py
├── requirements.txt
└── .env
```

---

## 🚀 Setup & Run

### 1. Create & activate Python virtual environment

**Windows:**
```powershell
python -m venv venv
venv\Scripts\activate
```

**Linux / macOS:**
```bash
python -m venv venv
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Create the MySQL database

```sql
CREATE DATABASE sahal_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 4. Configure environment

Edit `.env` with your MySQL credentials:
```ini
DB_USER=root
DB_PASSWORD=your_password
DB_HOST=localhost
DB_NAME=sahal_db
SECRET_KEY=change-this-in-production
```

### 5. Run database migrations

```bash
flask db init      # Only on first run
flask db migrate -m "Initial schema"
flask db upgrade
```

> ⚡ On first `python run.py`, the app auto-creates tables and inserts a seed row if the DB is empty.

### 6. Start the development server

```bash
python run.py
```

Visit → [http://localhost:5000](http://localhost:5000)

---

## 📱 Device-Aware Frontend

The app serves **completely different UIs** based on device type:

| Visitor | Template | Layout |
|---|---|---|
| Desktop browser | `templates/desktop/home.html` | Multi-column, traditional website |
| Mobile browser | `templates/mobile/home.html` | App-like, single-column, bottom CTA bar |

Detection is done in `app/utils/device.py` via a regex match against the `User-Agent` header. No third-party library needed.

To **test mobile view on desktop**: use Chrome DevTools → Toggle Device Toolbar (F12 → Ctrl+Shift+M).

---

## 📋 Phase Roadmap

| Phase | Module | Status |
|---|---|---|
| ✅ Phase 1 | Stack initialization + device detection | **Complete** |
| Phase 2 | Portfolio module + user authentication | Planned |
| Phase 3 | Service booking + email confirmations | Planned |
| Phase 4 | Order tracking system | Planned |
| Phase 5 | Admin workflow dashboard | Planned |

---

## 🔑 Environment Variables

| Key | Description |
|---|---|
| `SECRET_KEY` | Flask session signing key |
| `DB_USER` | MySQL username |
| `DB_PASSWORD` | MySQL password |
| `DB_HOST` | MySQL host (default: localhost) |
| `DB_NAME` | Database name |
| `MAIL_SERVER` | SMTP server hostname |
| `MAIL_PORT` | SMTP port (default: 587) |
| `MAIL_USE_TLS` | Enable TLS (True/False) |
| `MAIL_USERNAME` | SMTP login username |
| `MAIL_PASSWORD` | SMTP login password |

---

## ⚠️ Production Deployment Notes

- Set `FLASK_ENV=production` and use a **strong random** `SECRET_KEY`.
- Serve with **Gunicorn** behind **Nginx** — do NOT use `python run.py`.
- Use environment variables (not `.env`) for secrets in production.
- Enable MySQL SSL and restrict DB user permissions.
