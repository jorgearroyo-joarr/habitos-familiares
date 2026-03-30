<!-- Version: 3.4.2 | Updated: 2026-03-30 | Author: AI-assisted -->

# Changelog — HábitosFam

All notable changes to this project are documented here.  
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).  
Versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [3.4.2] - 2026-03-30

### Fixed

- **Infraestructura de Despliegue (Render.com)**: Corregidos múltiples puntos de falla en el despliegue:
  - Sincronización de versiones de Python (`3.11.10`) entre `render.yaml` y `runtime.txt`.
  - Robustecimiento de `build.sh` con verificaciones de entorno (Node, Python, Pip) y manejo de errores.
  - Mejora de `backend/main.py`: Ahora usa rutas absolutas para `alembic.ini` y mejores logs de arranque.
  - Optimización de migraciones: `render_as_batch` ahora es condicional al motor de DB (evitando problemas en PostgreSQL).

## [3.4.1] - 2026-03-29

### Fixed

- **CRÍTICO: Crash loop en startup con PostgreSQL (Render)** — El servidor reiniciaba infinitamente porque:
  1. `v330_initial.py`: El `INSERT INTO app_settings` omitía `admin_pin_hash` (columna `NOT NULL`) → violación de constraint en PostgreSQL → ROLLBACK antes de que `seed_default_data` pudiera ejecutarse.
  2. `c929fa34db3d_add_habit_mastery_columns.py`: Intentaba `ADD COLUMN` a columnas (`consecutive_days`, `is_mastered`, `mastered_at`) que `v330_initial` ya incluía en el `CREATE TABLE` → error `column already exists` en PostgreSQL.
  3. `1231155072f6_add_economy_fields_to_profile.py`: Mismo problema para `balance`, `unlocked_themes`, `unlocked_avatars`.
- **Fix colateral:** `crud.py` `get_comparison_charts()` usaba `WeekReward.amount` (columna inexistente) → corregido a `WeekReward.earned_amount`.

### Changed

- Las migraciones `c929fa34db3d` y `1231155072f6` ahora son **idempotentes**: usan `inspector.get_columns()` para verificar si las columnas ya existen antes de intentar crearlas. Esto las hace seguras tanto en DBs nuevas (PostgreSQL en Render) como en DBs con historial previo.

---

## [3.4.0] - 2026-03-18

### Added

- **Gráficos Comparativos (Admin)**: Nueva pestaña en el panel de admin para comparar el desempeño entre perfiles. Incluye:
  - Gráfico de barras: Tasa de completado (%) últimos 7 días por perfil
  - Gráfico de barras: Racha actual de cada perfil
  - Gráfico de barras: Total de recompensas semanales ganadas
  - Gráfico de líneas: Progreso semanal últimas 4 semanas
- `GET /api/admin/comparison/charts` — Endpoint para obtener datos comparativos de todos los perfiles

### Added

- **Sistema Core Loop Sentinel**: Nueva skill (`core-loop-sentinel`) y workflow (`/core-loop-repair`) para monitoreo de salud y auto-reparación del flujo de trabajo de la IA.
- **Integración Proactiva**: El Core Loop ahora incluye un paso de auditoría de salud en su fase inicial.

## [3.3.3] - 2026-03-17

### Changed

- `render.yaml`: Configurada infraestructura nativa con `PYTHON_VERSION` (3.11.10) y `NODE_VERSION` (20.18.0). Agregado `healthCheckPath` para monitoreo de salud.
- `build.sh`: Refactoreado para eliminar la instalación manual de `nvm`/Node.js (ahora nativo) y la ejecución de migraciones (ahora automático en el arranque).

## [3.3.2] - 2026-03-17

### Added

- **Mejoras de UX**:
  - **Spinner de carga**: Indicador visual mientras se cargan datos del API.
  - **Toast de errores**: Mensajes de error visibles cuando falla una llamada al servidor.

### Fixed

- `backend/api/habits.py`: Corregido tipo de `created_at` (ahora usa `datetime.now()` en lugar de string).
- `backend/api/habits.py`: Corregido uso de `DayLogWithMasteryOut` para el atributo `newly_mastered`.
- `backend/crud.py`: Agregadas conversiones explícitas de tipos (`str()`, `float()`, `bool()`) en funciones que retornan schemas Pydantic para evitar errores de serialización.
- `backend/api/admin.py`: Corregida línea muy larga en función `admin_login`.

## [3.3.1] - 2026-03-17

### Added

- **Documentación de Base de Datos**: Nuevo documento `docs/DATABASE.md` con el esquema completo de las 9 tablas, columnas, índices, relaciones y diagramas ER.
- **Migración Inicial de Alembic**: Nueva migración `v330_initial.py` que crea el esquema completo v3.3 desde cero. Permite a sistemas en producción que nunca usaron Alembic migrar fácilmente.

### Changed

- `backend/main.py`: Eliminada la función de migración manual `run_migrations()`. Ahora usa Alembic oficialmente para todas las migraciones de esquema.
- `docs/TECHNICAL.md`: Actualizada la sección de migraciones con referencia a `DATABASE.md` e instrucciones de Alembic.
- `docs/AGENTS.md`: Actualizada la sección de Database Migration Guide y lista de directorios para incluir `DATABASE.md`.

### Fixed

- Corregida la cadena de dependencias de migraciones de Alembic (`v330_initial` -> `c929fa34db3d` -> `1231155072f6`).

## [3.3.0] - 2026-03-18

### Added

- **Mejoras UX Fase 4 (Economía Virtual)**:
  - **Tienda (Store)**: Nueva interfaz modal para comprar Avatars y Temas usando los ahorros acumulados.
  - **Sistema de Saldo (Balance)**: Los perfiles ahora acumulan dinero real ganado por sus hábitos en una cuenta virtual.
  - **Personalización**: Capacidad de desbloquear y aplicar temas visuales y avatares emoji permanentes.
  - **Endpoint de Compra**: API robusta para validación de saldo y transacciones de artículos virtuales.
- `backend/migrations/versions/1231155072f6_add_economy_fields_to_profile.py`: Nueva migración para soporte de economía.

### Changed

- `backend/models.py`: Se agregaron los campos `balance`, `unlocked_themes` y `unlocked_avatars` al modelo `Profile`.
- `backend/crud.py`: La función `mark_reward_paid` ahora suma automáticamente el monto al balance del perfil.
- `frontend/scripts/data.ts`: Definición del catálogo inicial de la tienda (`STORE_ITEMS`).
- `frontend/scripts/app.ts`: Lógica completa de renderizado de tienda y gestión de compras.

## [3.2.0] - 2026-03-17
### Added
- **Mejoras UX Fase 1 (Quick Wins)**:
    - **Retroalimentación Háptica**: Vibración al marcar hábitos y micro-hábitos (Mobile only).
    - **Vista Previa de Perfil**: Botón "Ver" en el panel Admin para entrar como usuario sin cerrar sesión.
- **Mejoras UX Fase 2 (Progreso Visual)**:
    - **Barra de Siguiente Nivel**: Visualización dinámica en el Hero del perfil que muestra cuánto falta para el siguiente Tier (Plata/Oro/Diamante).
    - **Auditoría Visual de Logs**: El panel de datos ahora muestra la hora del último cambio para cada registro diario.
- **Mejoras UX Fase 3 (Eficiencia Admin)**:
    - **Cierre de Semana Masivo**: Nuevo botón "Cerrar Semana para Todos" en Admin y Nueva lógica en `app.ts` para ejecutar el cierre familiar con un clic.
    - **Analíticas de Puntos de Fricción**: Widget en el Dashboard de Admin que identifica automáticamente los 5 hábitos con menor tasa de cumplimiento.
    - **Resumen al pasar el ratón (Hover)**: En la tabla de logs, ahora se puede ver el detalle de qué hábitos se completaron o faltaron al pasar el cursor sobre la fila.

### Changed
- **Optimistic UI**: Reforzada la actualización inmediata del DOM antes de sincronizar con el API para eliminar latencia percibida.
- `backend/schemas.py`: Agregado campo `updated_at` a `DayLogOut`.
- `backend/crud.py`: Implementada función `bulk_close_week` para procesamiento familiar.
- `backend/api/admin.py`: Nuevo endpoint `POST /api/admin/bulk-close-week`.
- `frontend/scripts/admin.ts`: Rediseño de la sección de Logs con Tooltips (resumen de hábitos) y visualización de Friction Points.
- `frontend/scripts/app.ts`: Actualización de la función `resetWeek` para usar el nuevo endpoint familiar.

### Fixed
- Corregida inconsistencia en el cálculo de la fecha de inicio de semana (`getThisMonday`).
### Fixed
- **Lógica de Estrellas y Micro-hábitos (CRÍTICO)**:
    - Corregido acoplamiento erróneo: ahora el estado de micro-hábitos alimenta el progreso del hábito principal, no al revés
    - Eliminado comportamiento que marcaba todos los micro-hábitos al marcar el hábito principal
    - Ahora al completar todos los micro-hábitos, el hábito se marca automáticamente como completado
    - Agregado cálculo dinámico de "estrella ganada" basado en micro-hábitos completados
    - Mejorado feedback visual: estrellas ahora muestran estado pendiente (☆) vs ganado (⭐)

- **Tarjetas Colapsables (Accordion)**:
    - Optimizado rendimiento: ahora las tarjetas no re-renderizan todo el perfil al interactuar
    - Agregadas animaciones CSS suaves para expandir/colapsar mini-tasks
    - El estado de expansión ahora se mantiene correctamente sin parpadeo

- **Panel Admin**:
  - Agregado Error Boundary global para capturar y mostrar errores de forma amigable
  - Mejorado manejo de errores de red y conexiones
  - La sesión ahora muestra mensajes claros cuando expira el PIN

### Added

* **Sistema de Dominio de Hábitos (Habit Mastery)**:
  - Nuevo sistema de "estrellas permanentes" - los hábitos se dominan después de 21 días consecutivos
  - Efectos visuales especiales (corona 👑, borde dorado) para hábitos dominados
  - Confeti dorado y sonido triumphant al dominar un hábito
  - Estrellas bonus semanales para hábitos dominados (+1 por hábito dominado por día completado)
* **Categoría "Tecnología para el Bien"**:
  - Nuevos hábitos para enseñar uso positivo de la tecnología
  - Categoría disponible para todos los perfiles
* **Feedback Dopaminérgico Mejorado**:
  - Celebración especial cuando se domina un hábito
  - Sistema de recompensas visuales y sonoras mejorado
* **Migración de Base de Datos**:
  - Nueva migración Alembic `c929fa34db3d_add_habit_mastery_columns.py` para agregar columnas de mastery
  - Migración automática al iniciar la aplicación

### Fixed

* **Error del Panel Admin (Production)**: Corregido el problema que impedía acceder al admin en producción - ahora admin.html se compila correctamente a dist/ y se sirve desde ahí
* **Error del Panel Admin (Local)**: Corregido el problema que impedía acceder al admin - ahora carga correctamente desde admin.js
* **Error de Columna en Producción**: Corregido error `column habit_templates.consecutive_days does not exist` en PostgreSQL

### Changed

* `backend/models.py` - Agregados campos: `consecutive_days`, `is_mastered`, `mastered_at` a HabitTemplate
* `backend/schemas.py` - Actualizado HabitTemplateOut con nuevos campos de mastery
* `backend/crud.py` - Nueva lógica de mastery y cálculo de estrellas bonus
* `backend/api/habits.py` - Endpoint retorna información de hábitos recién dominados
* `frontend/app.js` - Nuevas funciones: showMasteryCelebration, launchGoldenConfetti, playMasterySound
* `frontend/admin.html` - Corregido src del script de admin
* `frontend/styles.css` - Nuevos estilos para mastery

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
