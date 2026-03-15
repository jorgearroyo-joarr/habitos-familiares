<!-- Version: 2.1.0 | Updated: 2026-03-15 | Author: AI-assisted -->
# HábitosFam – Documentación Técnica

> Stack: FastAPI · SQLAlchemy · SQLite (pronto: PostgreSQL/MySQL) · HTML/CSS/JS vanilla

---

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────┐
│                   FRONTEND                          │
│  index.html + styles.css + data.js + app.js         │
│  admin.html + admin.css + admin.js                  │
│  (HTML/CSS/JS vanilla, sin frameworks)              │
└────────────────────┬────────────────────────────────┘
                     │ HTTP REST (fetch API)
┌────────────────────▼────────────────────────────────┐
│                   BACKEND                           │
│  FastAPI (Python 3.14)                              │
│  ├── /api/profiles/*    → habits.py                 │
│  ├── /api/admin/*       → admin.py (PIN auth)       │
│  └── /* (static files)                              │
└────────────────────┬────────────────────────────────┘
                     │ SQLAlchemy ORM
┌────────────────────▼────────────────────────────────┐
│                   DATABASE                          │
│  SQLite (local) ← cambiar DATABASE_URL para:        │
│  PostgreSQL (Supabase) · MySQL                      │
└─────────────────────────────────────────────────────┘
```

---

## 📦 Dependencias principales

| Paquete | Versión | Propósito |
|---------|---------|-----------|
| `fastapi` | 0.115 | Framework REST API |
| `uvicorn` | 0.34 | Servidor ASGI |
| `sqlalchemy` | 2.0 | ORM (abstracción DB) |
| `pydantic` | 2.10 | Validación de datos |
| `python-dotenv` | 1.0 | Variables de entorno |
| `asyncpg` | 0.30 | Driver PostgreSQL (futuro) |
| `pymysql` | 1.1 | Driver MySQL (futuro) |

---

## 🗄️ Esquema de Base de Datos (v3 — 9 tablas)

### `app_settings`
| Columna | Tipo | Descripción |
|---------|------|-------------|
| id | INTEGER PK | Siempre 1 |
| admin_pin_hash | STRING | SHA-256 del PIN admin |
| currency_symbol | STRING | `$`, `€`, `₡`, etc. |
| app_name | STRING | Nombre de la app |
| streak_bonus_days | INTEGER | Días para bonus racha |
| streak_bonus_pct | FLOAT | Multiplicador racha |

### `profiles`
| Columna | Tipo | Descripción |
|---------|------|-------------|
| id | INTEGER PK | |
| slug | STRING UNIQUE | `alana`, `sofia` |
| name | STRING | Nombre display |
| age | INTEGER | Edad |
| avatar | STRING | Emoji |
| theme | STRING | Tema visual |
| pin_hash | STRING | SHA-256 del PIN usuario |
| weekly_reward_base | FLOAT | Base semanal ($) |
| weekly_reward_full | FLOAT | Máximo semanal ($) |
| monthly_reward_desc | STRING | Recompensa mensual |
| monthly_min_pct | FLOAT | % mínimo para desbloquear |
| level_idx | INTEGER | Nivel actual |
| is_active | BOOLEAN | Perfil activo |

### `habit_templates`
| Columna | Tipo | Descripción |
|---------|------|-------------|
| id | INTEGER PK | |
| profile_id | FK | → profiles.id |
| habit_key | STRING | `sport`, `study`, etc. |
| name | STRING | Nombre del hábito |
| icon | STRING | Emoji |
| category | STRING | Categoría |
| stars | INTEGER | Estrellas por completar |
| description | STRING | Descripción corta |
| motivation | STRING | Frase motivacional |
| sort_order | INTEGER | Orden de visualización |

### `micro_habits`
| Columna | Tipo | Descripción |
|---------|------|-------------|
| id | INTEGER PK | |
| habit_template_id | FK | → habit_templates.id |
| description | STRING | Texto del micro-hábito |
| sort_order | INTEGER | Orden |

### `reward_tiers`
| Columna | Tipo | Descripción |
|---------|------|-------------|
| id | INTEGER PK | |
| profile_id | FK | → profiles.id |
| tier_type | STRING | `weekly` o `monthly` |
| min_pct | FLOAT | % mínimo para este nivel |
| multiplier | FLOAT | Multiplicador recompensa |
| label | STRING | Nombre del nivel |
| emoji | STRING | Emoji del nivel |

### `day_logs` / `habit_entries` / `week_rewards` / `month_rewards`
Sin cambios — misma estructura v2.

---

## 🔌 API Reference (v3)

### Autenticación
| Método | URL | Descripción |
|--------|-----|-------------|
| POST | `/api/auth/login` | Login con PIN (user/admin) |

### Configuración
| Método | URL | Descripción |
|--------|-----|-------------|
| GET | `/api/settings` | Configuración global (moneda, bonus) |

### Endpoints de usuario
| Método | URL | Descripción |
|--------|-----|-------------|
| GET | `/api/profiles` | Lista de perfiles activos |
| GET | `/api/profiles/{slug}` | Perfil por slug |
| GET | `/api/profiles/{slug}/habits-config` | Hábitos + micro-hábitos del perfil |
| GET | `/api/profiles/{slug}/reward-tiers` | Niveles de recompensa |
| GET | `/api/profiles/{slug}/today` | Log de hoy |
| POST | `/api/profiles/{slug}/habits` | Guardar estado de hábitos |
| POST | `/api/profiles/{slug}/complete-day` | Marcar día como completado |
| GET | `/api/profiles/{slug}/week` | Stats semanales |
| GET | `/api/profiles/{slug}/month` | Stats mensuales |
| GET | `/api/profiles/{slug}/streak` | Racha actual |
| GET | `/api/profiles/{slug}/dashboard` | Dashboard con data agregada |

### Endpoints admin (requieren header `X-Admin-Pin`)
| Método | URL | Descripción |
|--------|-----|-------------|
| POST | `/api/admin/login` | Validar PIN admin |
| GET/PUT | `/api/admin/settings` | Leer/guardar config global |
| GET/POST | `/api/admin/profiles` | Listar/crear perfiles |
| PATCH/DELETE | `/api/admin/profiles/{slug}` | Editar/desactivar perfil |
| GET/POST | `/api/admin/profiles/{slug}/habits` | Hábitos del perfil |
| GET/PATCH/DELETE | `/api/admin/habits/{id}` | CRUD hábito individual |
| POST | `/api/admin/habits/{id}/micro-habits` | Crear micro-hábito |
| PATCH/DELETE | `/api/admin/micro-habits/{id}` | Editar/borrar micro-hábito |
| GET/PUT | `/api/admin/profiles/{slug}/reward-tiers` | Gestionar niveles recompensa |
| PUT | `/api/admin/profiles/{slug}/pin` | Cambiar PIN del perfil |
| GET | `/api/admin/profiles/{slug}/logs` | Ver registros |
| DELETE | `/api/admin/profiles/{slug}/logs/{date}` | Borrar un registro |
| POST | `/api/admin/profiles/{slug}/close-week` | Cerrar semana |
| GET | `/api/admin/health` | Estado del sistema |
| GET | `/api/admin/export/csv` | Exportar datos CSV |
| POST | `/api/admin/seed` | Datos semilla |
| POST | `/api/admin/reset-all-data` | Borrado de logs y recompensas |

📖 **Documentación interactiva**: `http://localhost:8765/api/docs`

---

## 🔄 Migración de Base de Datos

El único archivo a modificar es `.env`:

```env
# Producción con Supabase
DATABASE_URL="postgresql://postgres:PASSWORD@db.PROJECT.supabase.co:5432/postgres"
```

Con SQLAlchemy, **no se necesita cambiar ningún otro archivo**.

Para crear las tablas en el nuevo servidor:
```bash
python -c "from backend.database import create_tables; create_tables()"
```

Para migraciones de esquema (cuando se añaden columnas), usar Alembic:
```bash
pip install alembic
alembic init alembic
alembic revision --autogenerate -m "descripcion del cambio"
alembic upgrade head
```

---

## 🚀 Arrancar el servidor

```bash
# Instalar dependencias
pip install -r requirements.txt

# Configurar entorno
cp .env.example .env

# Desarrollo (con hot-reload)
uvicorn backend.main:app --reload --port 8765

# Producción
uvicorn backend.main:app --host 0.0.0.0 --port 8765 --workers 2
```

---

## 🧩 Estructura de capas

```
Capa          Archivo              Responsabilidad
──────────────────────────────────────────────────
Configuración config.py            Settings + env vars
Base de datos database.py          Conexión DB, session, tablas
Modelos       models.py            ORM entities
Validación    schemas.py           Pydantic request/response
Operaciones   crud.py              Todas las queries SQL
Rutas API     api/habits.py        Endpoints HTTP públicos
Admin API     api/admin.py         Endpoints HTTP protegidos
Entrada       main.py              FastAPI app, startup, static files
```

---

## ☁️ Hosting Gratuito

| Plataforma | Plan Gratis | Ideal para | Notas |
|------------|-------------|------------|-------|
| **[Render](https://render.com)** | Web Service gratis | Backend Python + SQLite | Auto-deploy desde GitHub, 750h/mes, duerme tras 15min inactividad |
| **[Fly.io](https://fly.io)** | 3 VMs gratis | Backend Python completo | Necesita `fly.toml`, incluye 3GB volumen persistente para SQLite |
| **[Railway](https://railway.com)** | $5 crédito/mes | Backend + PostgreSQL | Ideal si migras a PostgreSQL (incluye DB gratis) |
| **[Vercel](https://vercel.com)** | Frontend gratis | Solo archivos estáticos | No soporta Python; sirve el frontend |
| **[PythonAnywhere](https://pythonanywhere.com)** | 1 app web gratis | Backend Python | Interfaz sencilla, incluye consola Python |
| **[Supabase](https://supabase.com)** | DB PostgreSQL gratis | Solo base de datos | 500MB DB + Auth gratis, ideal como backend DB |

### Opción recomendada: Render.com (⭐ más fácil)

1. Sube tu código a GitHub
2. En [render.com](https://render.com) → New → Web Service
3. Conecta tu repo, configura:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
4. Deploy automático ✅

> ⚠️ En Render gratuito, la instancia duerme tras 15min sin tráfico. El primer acceso tarda ~30s en despertar.  
> Para datos persistentes, usa una URL de PostgreSQL (Supabase gratis) en `DATABASE_URL`.
