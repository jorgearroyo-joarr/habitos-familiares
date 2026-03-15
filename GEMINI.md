<!-- Version: 1.0.0 | Updated: 2026-03-15 -->
# HábitosFam — Gemini CLI Context

> Auto-loaded by Gemini CLI. Provides project-specific instructions.  
> View loaded context: `/memory show` | Reload: `/memory reload`

@AGENTS.md

---

## 🌐 Project at a Glance

- **Stack**: FastAPI + SQLAlchemy + Vanilla JS/HTML  
- **DB**: SQLite (dev) → PostgreSQL/MySQL (prod) via `DATABASE_URL` in `.env`  
- **Dev server**: `uvicorn backend.main:app --reload --port 8765`  
- **Admin**: `http://localhost:8765/admin` (default PIN: 1234)  
- **API docs**: `http://localhost:8765/api/docs`

---

## 🔄 Gated Execution Protocols

<PROTOCOL:PLAN>
Before writing any code (for changes touching more than 1 file OR 10 lines):

1. State in 3 bullet points: WHAT you will change, WHY, and WHICH files you will touch.
2. Wait for explicit user confirmation before proceeding.
3. If the user asks "how" rather than "do it", answer the question — don't start coding.
</PROTOCOL:PLAN>

<PROTOCOL:IMPLEMENT>
When implementing:

- Follow layer order: `config.py → database.py → models.py → schemas.py → crud.py → api/*.py → main.py`
- All user-facing strings in **Spanish (es-MX)**; code, comments, variable names in **English**
- Use `Depends(get_db)` for every DB operation — never share sessions between requests
- Use `crud.py` for all DB operations — never raw SQL in route handlers
- Zero-privilege: endpoints return ONLY data belonging to the slug/user in the URL
- Skill-first: check `.agents/skills/` before implementing a recurring task
</PROTOCOL:IMPLEMENT>

<PROTOCOL:REVIEW>
Before proposing a commit, verify ALL of the following:

- [ ] `ruff check backend/` → 0 errors
- [ ] `mypy backend/ --ignore-missing-imports` → 0 critical errors
- [ ] `pytest backend/ -v` → all tests pass (if tests exist)
- [ ] `CHANGELOG.md` updated with change in correct SemVer section
- [ ] If any API endpoint was added or modified → `docs/TECHNICAL.md` updated
- [ ] Version header updated in any `.md` file touched
</PROTOCOL:REVIEW>

---

## 🔐 Security Reminders

- **NEVER bypass** `verify_admin_pin()` — not even in test routes
- **NEVER create routes** that return another profile's data
- **NEVER use** `os.system()`, `eval()`, `exec()` in generated code
- Full policy: see `SECURITY.md`

---

## 🛠️ Available Skills

Run these tasks using the corresponding skill in `.agents/skills/`:

| Task | Skill |
|------|-------|
| Add a new habit category | `add-habit-category` |
| Add a new API endpoint | `add-api-endpoint` |
| Migrate to PostgreSQL/MySQL | `db-migration` |
| Audit security before a PR | `security-review` |
| Deploy to Render/Fly.io | `deploy` |
| Sync documentation | `update-docs` |
