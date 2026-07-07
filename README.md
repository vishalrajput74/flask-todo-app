# Flask Todo App

A production-grade, multi-user task management web application built with Flask. Includes full authentication, task management with priorities and filters, email-based password recovery, and a polished responsive UI with dark mode.

**Live Demo:** [https://todo-app-1atv.onrender.com](https://todo-app-1atv.onrender.com)

---

## Features

- **User Authentication**
  - Register, login, logout with hashed passwords (Werkzeug)
  - "Remember Me" session support
  - Change password from profile
  - Forgot/reset password via secure, time-limited email links (SendGrid HTTP API)

- **Task Management**
  - Create, edit, delete tasks with title, description, and due date
  - Auto-calculated priority (High / Medium / Low) based on due date, stored in DB for efficient SQL filtering
  - Status tracking: Pending, Working, Done
  - Bulk actions (update/delete multiple tasks at once)
  - CSV export of tasks

- **Search, Filter & Pagination**
  - Filter by status and priority
  - Search by task title
  - Sortable columns (by due date, priority, id, etc.)
  - Pagination with filter/sort state preserved across page changes (Post-Redirect-Get pattern)

- **Dashboard & Profile**
  - Stats cards (total, pending, working, done, overdue tasks)
  - User profile page with editable username/email

- **UI/UX**
  - Fully responsive design (mobile-friendly)
  - Dark mode toggle with persistence via `localStorage`

- **Backend Architecture**
  - Modular structure using Flask Blueprints (`auth`, `tasks`)
  - Custom session-based `login_required` decorator
  - Form validation via Flask-WTF (CSRF-protected)
  - Database migrations via Flask-Migrate

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| Database | PostgreSQL (production), SQLAlchemy ORM |
| Forms/Validation | Flask-WTF, WTForms |
| Migrations | Flask-Migrate (Alembic) |
| Auth | Session-based, Werkzeug password hashing |
| Email | SendGrid HTTP API (transactional emails on Render) |
| Frontend | Jinja2 templates, HTML, CSS (custom, no framework) |
| Deployment | Render, Gunicorn (WSGI) |

---

## Project Structure

```
app/
├── routes/
│   ├── auth.py          # Login, register, password reset, profile
│   └── tasks.py         # Task CRUD, filters, stats, CSV export
├── templates/            # Jinja2 templates
├── static/css/           # Stylesheets
├── models.py             # User and Task models
├── forms.py              # WTForms form definitions
├── utils.py               # login_required decorator
├── extensions.py          # Flask extension instances (db, csrf, migrate, mail)
└── __init__.py            # App factory
migrations/                # Flask-Migrate migration scripts
run.py                      # App entry point
requirements.txt
```

---

## Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/vishalrajput74/flask-todo-app.git
cd flask-todo-app
```

### 2. Create a virtual environment
```bash
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # macOS/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
Create a `.env` file in the project root:
```
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///todo.db
SENDGRID_API_KEY=your-sendgrid-key       # optional, for password reset emails
MAIL_DEFAULT_SENDER=your-email@example.com
```

### 5. Run database migrations
```bash
flask db upgrade
```

### 6. Start the app
```bash
python run.py
```
App runs at `http://localhost:5001`

---

## Deployment

Deployed on [Render](https://render.com) with auto-deploy from GitHub. Start command:
```bash
flask db upgrade && gunicorn run:app
```

---

## Author

**Vishal Rajput**
[GitHub](https://github.com/vishalrajput74) · [LinkedIn](https://www.linkedin.com/in/vishal-rajput-a5449a280/)
