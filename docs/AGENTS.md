<!-- Version: 2.3.0 | Updated: 2026-03-17 | Standard: AGENTS.md 2025 -->

# AGENTS.md – HábitosFam

> **README for AI Agents** — Provides project-specific rules, conventions, and context for AI coding assistants (Antigravity, Gemini CLI, GitHub Copilot, Cursor, OpenAI Codex, Claude Code).  
> Follows the [AGENTS.md 2025 open standard](https://agents.md) adopted by 60,000+ open-source projects.

---

## 🎯 Project Identity

**HábitosFam** is a dynamic family habit tracking system centered around:
- **Dynamic Profiles**: Add unlimited children via the Admin panel.
- **Custom Habits**: Each child has unique habits and reward tiers.
- **Micro-Habits**: Parent habits are broken down into individual sub-tasks for better progress tracking.
- **Dopamine Loops**: Premium visual/audio feedback for persistence.

**Version**: 2.0.0 | **Stack**: FastAPI + SQLAlchemy + Vanilla JS/HTML | **Lang**: Python 3.11+

---

## 🏗️ Architecture Overview

```
habitos-familiares/
├── index.html          # Main daughter-facing app
├── admin.html          # Parent admin panel
├── styles.css          # Shared dark-mode styles
├── admin.css           # Admin-specific styles
├── data.js             # Habit definitions (client-side)
├── app.js              # Frontend logic + localStorage
├── admin.js            # Admin panel logic + API calls
├── AGENTS.md           # ← You are here
├── GEMINI.md           # Gemini CLI context (auto-loaded)
├── CHANGELOG.md        # SemVer changelog (Keep a Changelog format)
├── SECURITY.md         # Threat model + zero-privilege policies
├── backend/
│   ├── __init__.py
│   ├── main.py          # FastAPI entry point + static files
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
│   ├── TECHNICAL.md     # Architecture + API reference
│   ├── DATABASE.md      # Complete database schema documentation
│   ├── DEPLOYMENT.md    # Hosting options (Render, Fly.io, Railway)
│   └── USER_GUIDE.md    # End-user guide (Spanish)
├── .agents/
│   ├── skills/          # Skills 2.0 — reusable AI workflows
│   └── workflows/       # Step-by-step automation scripts
├── .env.example         # All supported env vars (never delete)
├── requirements.txt
└── runtime.txt
```

### Layer Order (always follow this dependency direction)
```
config.py → database.py → models.py → schemas.py → crud.py → api/*.py → main.py
```

---

## 🚦 ALWAYS – ASK FIRST – NEVER

### ALWAYS ✅
- Use the `apiCall` wrapper for all Admin/User frontend actions.
- Load `appSettings` from the API for the currency symbol and app name.
- Use Pydantic schemas for all request/response validation in the backend.
- Run `crud.py` functions for all DB operations — no raw SQL in route handlers.
- Maintain cross-DB compatibility (SQLAlchemy ORM only).
- Use **Spanish** for all user-facing strings; **English** for code, comments, and docs.
- Handle visual feedback (sparkles, confetti) on micro-habit completion.
- Update `CHANGELOG.md` for every functional change (Added/Changed/Fixed/Security).
- Sync `docs/TECHNICAL.md` when any API endpoint is added or modified.
- Add or update version headers in any `.md` doc file you touch.

### ASK FIRST ❓
- Before changing the core DB schema (`models.py`).
- Before adding heavy external JS libraries (>50 KB).
- Before changing the PIN hashing mechanism.
- Before modifying CORS origins.
- Before elevating any privilege or bypassing an auth check — even temporarily.

### NEVER 🚫
- Never put raw SQL in route handlers — use `crud.py`.
- Never bypass the SQLAlchemy session — always use `Depends(get_db)`.
- Never hardcode profile names/ages — always use `HABITS_DATA` / `HABITS_CONFIG`.
- Never store secrets in source code — use `.env`.
- Never delete `.env.example` (tracks all supported env vars).
- Never expose admin endpoints without `X-Admin-Pin` validation.
- Never use `drop_tables()` in production code.
- Never generate code with `os.system()`, `eval()`, `exec()` or shell injection.
- Never access another profile's data from a single-profile endpoint.
- Never commit `.env`, `*.db`, or `*.db-shm` / `*.db-wal` files.

---

## 🧪 Testing

```bash
# Install test dependencies
pip install pytest httpx

# Run all backend tests (from project root)
pytest backend/ -v

# Lint (zero tolerance)
pip install ruff
ruff check backend/

# Type check
pip install mypy
mypy backend/ --ignore-missing-imports

# Full quality gate (must pass before proposing a commit)
ruff check backend/ && mypy backend/ --ignore-missing-imports && pytest backend/ -v
```

> **Agent policy**: Do not propose a commit unless the full quality gate passes.

---

## 🔐 Security Constraints — Zero-Privilege by Design

HábitosFam follows **Zero-Privilege by Design** (OWASP + NIST Zero Trust):  
*"Every user, process, and AI agent starts with zero permissions and receives only the minimum necessary."*

### Privilege model per layer

| Layer | Privilege rule | Enforcement |
|-------|---------------|-------------|
| **Frontend user** | Access only to own profile slug | URL-scoped endpoints |
| **Frontend admin** | Full access only after PIN validation | `X-Admin-Pin` header on every request |
| **API — public** | Read-only profile data (no writes without slug match) | FastAPI route constraints |
| **API — admin** | Full CRUD only after `verify_admin_pin()` | `crud.verify_admin_pin()` dependency |
| **DB session** | One session per HTTP request, closed on exit | `Depends(get_db)` + `finally: db.close()` |
| **AI Agent** | Cannot bypass auth; cannot escalate privilege; cannot access `.env` values | This document |

### Rules for AI agents
- **Never add a bypass** to `verify_admin_pin()`, even in test routes.
- **Never read `.env` values** directly in code — only `config.py` may do so.
- **Never write migrations** that drop existing columns without user confirmation.
- **Never create routes** that return data from a different profile than the one in the URL.
- **Report, don't fix silently** any security-related code you encounter — notify the user.

---

## 🤖 Agent Policies & Workflows

### Plan before implementing
For any change touching more than **3 files** or **10 lines**:
1. Describe what you will change and why (3 bullet points max).
2. List the files you will touch.
3. Wait for user confirmation before writing code.

### Gated execution protocols
| Protocol | When | Action |
|----------|------|--------|
| `PLAN` | Before any multi-file change | State plan, list files, wait |
| `IMPLEMENT` | After plan is approved | Follow layer order, follow conventions |
| `REVIEW` | Before proposing commit | Run quality gate, update CHANGELOG.md |

### Skill-first approach
Before implementing a recurring task, check if a skill exists in `.agents/skills/`:
```
add-habit-category  → for adding new habit categories
add-api-endpoint    → for new FastAPI endpoints
db-migration        → for database schema changes
security-review     → for auditing security before PRs
deploy              → for deploying to Render / Fly.io
update-docs         → for keeping docs in sync
```

---

## 🌿 Branching & GitHub Flow (Zero-Privilege Repo)

To enforce quality and security, direct commits to `main` are strictly forbidden. All agents and developers must use the standard GitHub Flow.

### 1. Branch Naming Convention
Branches must follow the `type/scope` or `type/description` pattern:
- `feature/add-dopamine-stars`
- `fix/admin-pin-bypass`
- `docs/update-technical-guide`
- `chore/update-dependencies`

### 2. Pull Request (PR) Requirements
- All changes must be submitted via PR against the `main` branch.
- PR titles must follow Conventional Commits (e.g., `feat(ui): add dopamine stars`).
- PR descriptions must include what changed, why, and how it was tested.
- If the PR resolves a specific issue, it must include a closing keyword (e.g., `Closes #12`).

### 3. Review & Quality Gates
Before a PR can be merged, it **must** pass the following:
1. `ruff check backend/` (Zero Python linting errors)
2. `mypy backend/ --ignore-missing-imports` (Zero typing issues)
3. `pytest backend/ -v` (All tests pass)
4. For backend changes: `security-review` skill executed and passed.

**Rule for Agents:** When asked to implement a feature, always start by checking out a new branch. Never attempt to push directly to `main`.

---

## 🗄️ Database Migration Guide

> **Important**: Full database schema documentation is available in [DATABASE.md](../docs/DATABASE.md).

### Switch Databases

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

### Alembic Migrations

The project uses Alembic for schema migrations. Migrations run automatically on app startup.

```bash
# Run all pending migrations
alembic upgrade head

# Revert last migration
alembic downgrade -1

# Create new migration (after model changes)
alembic revision --autogenerate -m "description of change"
alembic upgrade head

# View migration history
alembic history
```

For systems in production that never used Alembic before:
```bash
# The initial migration creates the complete v3.3 schema
alembic upgrade head
```

---

## 🧪 Running the Project

```bash
# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env

# Start development server (with hot-reload)
uvicorn backend.main:app --reload --port 8765

# API interactive docs
open http://localhost:8765/api/docs

# App (user-facing)
open http://localhost:8765

# Admin panel (default PIN: 1234)
open http://localhost:8765/admin
```

---

## 💻 Key Patterns

### Adding a new habit category
> Use skill: `.agents/skills/add-habit-category/SKILL.md`

1. Add to `data.js` (under the profile's `habits` object)
2. Add to `backend/data_config.py` (under `HABITS_CONFIG`)
3. Update `docs/TECHNICAL.md`
4. Update `CHANGELOG.md` (Added section)

### Adding a new API endpoint
> Use skill: `.agents/skills/add-api-endpoint/SKILL.md`

1. Add Pydantic schema in `backend/schemas.py`
2. Add CRUD function in `backend/crud.py`
3. Add route handler in `backend/api/habits.py` or `backend/api/admin.py`
4. Document in `docs/TECHNICAL.md`
5. Update `CHANGELOG.md`

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
| `CHANGELOG.md` | Both | Updated by agent on every functional change |
| `SECURITY.md` | Both | Updated only by human or after explicit approval |

---

## 🌍 Localization
- User-facing language: **Spanish (es-MX)**
- Code, comments, variable names: **English**
- Date format: **YYYY-MM-DD** (ISO 8601) everywhere
- Currency: **USD** (configurable via `data_config.py` and admin settings)

---

## 📝 Versioning Policy

This project follows [Semantic Versioning 2.0](https://semver.org) and [Keep a Changelog](https://keepachangelog.com):

| Bump | When |
|------|------|
| **PATCH** `2.0.x` | Bug fixes, typo corrections, doc updates |
| **MINOR** `2.x.0` | New backward-compatible feature (new habit, new endpoint) |
| **MAJOR** `x.0.0` | Breaking DB schema change, major API redesign |

**CHANGELOG.md must be updated in the same commit as the code change.**

---

## 📋 AGENTS.md Change Log

| Version | Date | Change |
|---------|------|--------|
| 2.2.1 | 2026-03-15 | Fixed: Accordion cards, star/micro-habit logic, admin error handling |
| 2.1.0 | 2026-03-15 | Added: Testing, Security, Agent Policies, Versioning, Skills reference |
| 2.0.0 | 2026-03-01 | Initial AGENTS.md (AGENT.md renamed to AGENTS.md 2025 standard) |
