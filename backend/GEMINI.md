<!-- Version: 1.0.0 | Updated: 2026-03-15 -->
# HábitosFam — Backend Context (Gemini CLI)

> Sub-directory context loaded by Gemini CLI when working inside `backend/`.  
> Supplements the root `GEMINI.md`.

---

## 🏗️ Backend Layer Architecture

```
config.py       → Pydantic Settings — reads .env, exposes typed `settings` object
database.py     → SQLAlchemy engine, SessionLocal, create_tables()
models.py       → ORM models (Profile, DayLog, HabitEntry, HabitTemplate, ...)
schemas.py      → Pydantic v2 request/response DTOs
crud.py         → ALL database operations — no raw SQL anywhere else
api/habits.py   → Public endpoints (/api/profiles/*)
api/admin.py    → Admin endpoints (/api/admin/*) — PIN-gated
main.py         → FastAPI app, startup, CORS, static files mounting
```

**Dependency direction (never reverse this):**
```
config → database → models → schemas → crud → api/* → main
```

---

## 📐 Conventions for Backend Code

### Typing
- All function signatures must have full Python type hints
- Return types must be explicit: `Optional[Model]`, `List[Schema]`, etc.
- Use `from __future__ import annotations` for forward references

### SQLAlchemy Session Pattern
```python
# CORRECT — always use Depends(get_db)
@router.get("/profiles/{slug}")
def get_profile(slug: str, db: Session = Depends(get_db)):
    return crud.get_profile(db, slug)

# NEVER — direct session creation in route handlers
db = SessionLocal()  # ← FORBIDDEN in route handlers
```

### CRUD Pattern
```python
# All DB operations live in crud.py
# Signature: function_name(db: Session, *args) -> ReturnType

def get_profile(db: Session, slug: str) -> Optional[Profile]:
    return db.query(Profile).filter(Profile.slug == slug).first()
```

### Admin Endpoint Pattern
```python
# Every admin route must call verify_admin_pin() first
@router.get("/admin/something")
def admin_something(
    x_admin_pin: str = Header(alias="X-Admin-Pin"),
    db: Session = Depends(get_db)
):
    crud.verify_admin_pin(db, x_admin_pin)  # raises HTTPException if invalid
    # ... rest of logic
```

### Pydantic v2 Schema Pattern
```python
class ProfileCreate(BaseModel):
    name: str
    slug: str = Field(..., pattern=r"^[a-z0-9-]+$")

    model_config = ConfigDict(from_attributes=True)
```

---

## 🔐 Security Rules (Backend)

1. `verify_admin_pin()` must be called at the START of every admin route handler — no exceptions.
2. Profile endpoints must filter by `slug` from the URL — never return all profiles from a user-facing endpoint.
3. Never access `os.environ` directly — only `settings.*` from `config.py`.
4. Session must be closed even on exception — `Depends(get_db)` handles this with `finally: db.close()`.

---

## 🧪 Quality Gate (run before any commit)

```bash
# From project root
ruff check backend/
mypy backend/ --ignore-missing-imports
pytest backend/ -v
```
