<!-- Version: 1.0.0 | Updated: 2026-03-15 | Author: AI-assisted -->

# Changelog — HábitosFam

All notable changes to this project are documented here.  
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).  
Versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

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
