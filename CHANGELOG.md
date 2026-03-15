<!-- Version: 2.3.1 | Updated: 2026-03-15 | Author: AI-assisted -->

# Changelog — HábitosFam

All notable changes to this project are documented here.  
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).  
Versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

## [3.0.0] - 2026-03-15
### Added
*   **Vite + TypeScript Stack**: El frontend completo (`app.js`, `admin.js`, `data.js`) fue migrado a TypeScript (`.ts`) con tipado estricto e interfaces compartidas (`Profile`, `Habit`, `MicroHabit`).
*   **Render Infrastructure as Code**: Nuevo archivo `render.yaml` para despliegue automático "Full Stack" en Render combinando la compilación de Vite (`npm run build`) y FastAPI.

### Changed
*   **Asset Serving**: Configuración de `backend/main.py` revertida para servir archivos estáticos compilados y ultra-bajos desde la carpeta `dist/` cuando se compila para producción.

### Fixed
*   **PIN Auto-advance (UX)**: Mejorada la fluidez del input de PIN. Ahora avanza de casilla automáticamente, permite borrar fluidamente y soporta pegar (Paste) el PIN completo.
*   **Tests de IU Automatizados**: Creación de perfiles desde el panel de admin estabilizada.

## [2.3.1] - 2026-03-15
### Fixed
- **CSS Loading** — Fixed CSS not loading by serving from `frontend/` source directory instead of `dist/`
- **Tests** — Fixed `TestMonthClose` tests that were failing due to PIN hash mock issues

## [2.3.0] - 2026-03-15
### Added
- Comprehensive Architectural Justification document (`docs/ARCHITECTURE.md`).
- Core Use Cases documentation (`docs/USE_CASES.md`).
- Backend Testing Suite (Unit and Functional tests using `pytest`).
- Quality Gate enforcement with `ruff` and `mypy`.
- Automated testing design document (`docs/TESTING_DESIGN.md`).

## [2.2.0] - 2026-03-15

### Added
- **Gráficos de Tendencia** — `GET /api/profiles/{slug}/trends` con Chart.js para visualizar cumplimiento semanal/mensual/anual
- **Catálogo de Plantillas** — `GET /api/admin/templates/catalog` con hábitos predefinidos por edad (Higiene, Estudio, Deporte)
- **Editor Drag & Drop** — Reordenar hábitos arrastrando en el panel admin con `POST /api/admin/profiles/{slug}/habits/reorder`
- **Cierre de Mes Automático** — `POST /api/admin/profiles/{slug}/close-month` y `close-current-month` para consolidar recompensas mensuales
- **Migraciones Alembic** — Configuración en `migrations/` para versionado formal del esquema de DB
- **Pruebas Unitarias** — `backend/test_api.py` con tests para tendencias, templates, month-close, reorder y endpoints existentes

### Changed
- `backend/schemas.py` — Nuevos esquemas: `TrendResponse`, `MonthCloseResult`, `HabitTemplatesCatalog`
- `backend/crud.py` — Nuevas funciones: `get_trend_data()`, `close_month()`, `get_habit_templates_catalog()`
- `backend/api/habits.py` — Endpoint `GET /profiles/{slug}/trends`
- `backend/api/admin.py` — Endpoints: `GET /templates/catalog`, `POST /close-month`, `POST /close-current-month`, `POST /habits/reorder`
- `app.js` — Gráficos Chart.js con selector de periodo y estadísticas de tendencia
- `admin.js` — Drag & drop para reorder de hábitos
- `styles.css` — Estilos para trends charts, drag & drop, templates catalog

---

## [2.1.1] - 2026-03-15

### Added
- **Web Notifications** — Recordatorio diario configurable via Web Notifications API
- **Light/Dark Theme Toggle** — Botón en header para cambiar entre modo oscuro y claro (persistente via localStorage)
- **Automatic Database Backups** — Backups automáticos antes de operaciones críticas (reset, delete profile)
- **PWA Support** — manifest.json y favicon.svg para instalación como app móvil
- `backend/backup.py` — Nuevo módulo de backup con retención de 5 backups máximos

### Changed
- `styles.css` — Variables CSS adicionales para theme light
- `index.html` — Meta tags para PWA y theme-color
- `app.js` — Funciones para notificaciones, toggle de tema e inicialización

---

## [2.1.0] - 2026-03-15

### Added
- `AGENTS.md` — AI agent context file following the AGENTS.md 2025 open standard (renamed from `AGENT.md`)
- `GEMINI.md` — Gemini CLI project context with hierarchical loading and PLAN/IMPLEMENT/REVIEW protocols
- `backend/GEMINI.md` — Backend-specific context for Gemini CLI sub-directory loading
- `CHANGELOG.md` — This file, following Keep a Changelog + SemVer
- `SECURITY.md` — Threat model + Zero-Privilege by Design policy (OWASP + NIST Zero Trust)
- `.agents/skills/add-habit-category/SKILL.md` — Reusable skill for adding habit categories
- `.agents/skills/add-api-endpoint/SKILL.md` — Reusable skill for new FastAPI endpoints
- `.agents/skills/db-migration/SKILL.md` — Reusable skill for DB migration (SQLite → PostgreSQL/MySQL)
- `.agents/skills/security-review/SKILL.md` — OWASP security audit skill
- `.agents/skills/deploy/SKILL.md` — Deployment guide skill (Render, Fly.io, Railway)
- `.agents/skills/update-docs/SKILL.md` — Documentation sync skill
- `.agents/workflows/dev-run.md` — Workflow to start the development server
- `.agents/workflows/add-feature.md` — Standard feature addition workflow
- `[FIXED]` Integrated "Propuestas de Mejora" into official `ROADMAP.md`
- `[FIXED]` Added `reset-all-data` functional endpoint to Admin API
- `[FIXED]` Fixed 15+ linting and type errors across the backend
- `[FIXED]` Fully localized API responses and error messages to es-MX

### Changed
- `AGENTS.md` — Upgraded from 2024 to 2025 standard: added Testing section, Security Constraints (Zero-Privilege), Agent Policies, Gated Protocols, Versioning Policy, Skill references

---

## [2.0.0] - 2026-03-01

### Added
- Dynamic profile system — unlimited children via admin panel
- Admin panel (`admin.html`, `admin.js`, `admin.css`) with full CRUD
- Micro-habits — parent habits broken into individual sub-tasks
- Reward tier system — weekly/monthly rewards with configurable multipliers
- Streak bonus system — configurable bonus for consecutive days
- FastAPI backend with SQLAlchemy ORM (9-table schema)
- Multi-DB support: SQLite (default), PostgreSQL, MySQL — change only `DATABASE_URL`
- `docs/TECHNICAL.md` — Full API reference (30+ endpoints)
- `docs/DEPLOYMENT.md` — Hosting guide (Render, Fly.io, Railway, PythonAnywhere)
- `docs/USER_GUIDE.md` — End-user guide in Spanish

### Changed
- Architecture migrated from static files to FastAPI + SQLAlchemy
- Profile data moved from hardcoded JS to DB-driven configuration
- Admin authentication upgraded to PIN + SHA-256 hash

---

## [1.0.0] - 2025-12-01

### Added
- Initial version: static HTML/CSS/JS app for Alana and Sofía
- Local storage-based habit tracking
- Sparkle + confetti visual feedback on habit completion
- Dark mode design with profile themes
