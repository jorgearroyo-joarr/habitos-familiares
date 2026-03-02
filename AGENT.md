# AGENT.md – HábitosFam

> **README for AI Agents** — This file provides project-specific rules, conventions, and context to AI coding assistants working on HábitosFam. It follows the emerging AGENT.md standard (2024).

---

## 🎯 Project Identity

**HábitosFam** is a dynamic family habit tracking system centered around:
- **Dynamic Profiles**: Add unlimited children via the Admin panel.
- **Custom Habits**: Each child has unique habits and reward tiers.
- **Micro-Habits**: Parent habits are broken down into individual sub-tasks for better progress tracking.
- **Dopamine Loops**: Premium visual/audio feedback for persistence.

---

## 🏗️ Architecture Overview

```
good_habits/
├── index.html       # Main daughter-facing app
├── admin.html       # Parent admin panel
├── styles.css       # Shared dark-mode styles
├── admin.css        # Admin-specific styles
├── data.js          # Habit definitions (client-side)
├── app.js           # Frontend logic + localStorage
├── admin.js         # Admin panel logic + API calls
├── backend/
│   ├── main.py          # FastAPI entry point
│   ├── config.py        # Settings via pydantic-settings
│   ├── database.py      # SQLAlchemy abstraction (change URL = change DB)
│   ├── models.py        # ORM models (Profile, DayLog, HabitEntry, WeekReward, MonthReward)
│   ├── schemas.py       # Pydantic v2 request/response schemas
│   ├── crud.py          # All DB operations
│   ├── data_config.py   # Server-side habit/reward config
│   └── api/
│       ├── habits.py    # Public habit API
│       └── admin.py     # Admin API (PIN-protected)
├── docs/
│   ├── TECHNICAL.md
│   └── USER_GUIDE.md
├── ROADMAP.md
└── requirements.txt
```

---

## 🚦 ALWAYS – DO – NEVER

### ALWAYS
- ✅ Use the `apiCall` wrapper for all Admin/User frontend actions.
- ✅ Load `appSettings` from the API for the currency symbol and app name.
- ✅ Use Pydantic schemas for all request/response validation in the backend.
- ✅ Run `crud.py` functions for all DB operations — no raw SQL in route handlers.
- ✅ Maintain cross-DB compatibility (SQLAlchemy ORM).
- ✅ Use Spanish for all user-facing strings; English for code, comments, and docs.
- ✅ Handle visual feedback (sparkles, confetti) on micro-habit completion.

### ASK FIRST
- ❓ Before changing the core DB schema (models.py).
- ❓ Before adding heavy external JS libraries.
- ❓ Before changing the default PIN hashing mechanism.

### NEVER
- 🚫 Never put raw SQL in route handlers — use `crud.py`
- 🚫 Never bypass the SQLAlchemy session — always use `Depends(get_db)`
- 🚫 Never hardcode profile names/ages — always use `HABITS_DATA` / `HABITS_CONFIG`
- 🚫 Never store secrets in source code — use `.env`
- 🚫 Never delete `.env.example` (tracks all supported env vars)
- 🚫 Never expose admin endpoints without PIN validation
- 🚫 Never use `drop_tables()` in production code

---

## 🗄️ Database Migration Guide

To switch databases, **only** change `DATABASE_URL` in `.env`:

```env
# SQLite (default, no setup needed)
DATABASE_URL="sqlite:///./habitosfam.db"

# PostgreSQL / Supabase
DATABASE_URL="postgresql://user:pass@host:5432/habitosfam"

# MySQL
DATABASE_URL="mysql+pymysql://user:pass@host:3306/habitosfam"
```

**No other code changes needed.** SQLAlchemy handles the rest.

---

## 🧪 Running the Project

```bash
# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env

# Start the development server
uvicorn backend.main:app --reload --port 8765

# API docs
open http://localhost:8765/api/docs

# App
open http://localhost:8765

# Admin panel
open http://localhost:8765/admin   # default PIN: 1234
```

---

## 💻 Key Patterns

### Adding a new habit category
1. Add to `data.js` (under `alana.habits` and/or `sofia.habits`)
2. Add to `backend/data_config.py` (under `HABITS_CONFIG`)
3. Increment `total` in `DayLog` if needed

### Adding a new API endpoint
1. Add route handler in `backend/api/habits.py` or `backend/api/admin.py`
2. Add CRUD function in `backend/crud.py`
3. Add Pydantic schema in `backend/schemas.py` if new request/response shape
4. Document in `docs/TECHNICAL.md`

### Profile theme naming convention
- Alana → `alana-theme`, `alana-bar`, `alana-btn`, `alana-card`, `.alana-ring`
- Sofía → `sofia-theme`, `sofia-bar`, `sofia-btn`, `sofia-card`, `.sofia-ring`
- CSS variables: `--alana-primary`, `--sofia-primary`, etc.

---

## 📁 File Ownership

| File | Owner | Notes |
|------|-------|-------|
| `data.js` | Frontend | Must stay in sync with `data_config.py` |
| `backend/database.py` | Backend | Only file to change for DB migration |
| `backend/models.py` | Backend | Schema changes require DB migration |
| `styles.css` | Frontend | Shared between `index.html` and `admin.html` |
| `.env` | Config | Never commit to git |

---

## 🌍 Localization
- User-facing language: **Spanish (es-MX)**
- Code, comments, variable names: **English**
- Date format: **YYYY-MM-DD** (ISO 8601) everywhere
- Currency: **USD** (configurable in `data_config.py`)
