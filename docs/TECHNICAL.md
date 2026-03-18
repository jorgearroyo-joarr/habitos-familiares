<!-- Version: 3.4.0 | Updated: 2026-03-18 | Author: AI-assisted -->
# HábitosFam – Documentación Técnica

> Stack: FastAPI · SQLAlchemy · SQLite (PostgreSQL/MySQL ready) · HTML5/CSS3 · TypeScript v5

---

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────┐
│                   FRONTEND (Vite + TypeScript)      │
│  /frontend:                                         │
│  ├── index.html        (Root)                       │
│  ├── admin.html        (Admin UI)                   │
│  ├── /scripts/*.ts     (Lógica TypeScript tipada)   │
│  ├── /styles/*.css     (Estilos base)               │
│  ├── /public/          (PWA assets)                 │
│  └── /dist/            (Build de producción Vite)   │
└────────────────────┬────────────────────────────────┘
                     │ HTTP REST (fetch API)
┌────────────────────▼────────────────────────────────┐
│                   BACKEND                           │
│  FastAPI (Python 3.14 + Type Hints)                 │
│  ├── /api/habits.py (Public REST)                   │
│  ├── /api/admin.py  (Admin CRUD)                    │
│  ├── /tests/        (Unit & Functional)             │
│  └── /main.py       (Startup & Static Serving)       │
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

> **Nota**: El esquema completo con todas las columnas, índices y relaciones está documentado en [DATABASE.md](./DATABASE.md).

### Tablas Principales

| Tabla | Propósito |
|-------|-----------|
| `app_settings` | Configuración global (moneda, PIN admin, bonus racha) |
| `profiles` | Perfiles de familiares (nombre, avatar, PIN, saldo) |
| `habit_templates` | Hábitos asignados a cada perfil |
| `micro_habits` | Sub-tareas dentro de cada hábito |
| `reward_tiers` | Niveles de recompensa configurables |
| `day_logs` | Registro diario de completado |
| `habit_entries` | Estado de cada hábito por día |
| `week_rewards` | Recompensas semanales |
| `month_rewards` | Recompensas mensuales |

Para detalles completos (columnas, tipos, defaults, foreign keys), consulta [DATABASE.md](./DATABASE.md).

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
| GET | `/api/profiles/{slug}/trends?period=weekly|monthly|yearly` | Gráficos de tendencia (Chart.js) |
| POST | `/api/profiles/{slug}/purchase` | **Comprar artículo virtual (avatar/tema)** |

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
| POST | `/api/admin/bulk-close-week` | **Cerrar semana masivamente** |
| GET | `/api/admin/health` | Estado del sistema |
| GET | `/api/admin/export/csv` | Exportar datos CSV |
| POST | `/api/admin/seed` | Datos semilla |
| POST | `/api/admin/reset-all-data` | Borrado de logs y recompensas |
| GET | `/api/admin/templates/catalog` | Catálogo de plantillas de hábitos |
| POST | `/api/admin/profiles/{slug}/close-month` | Cerrar mes específico |
| POST | `/api/admin/profiles/{slug}/close-current-month` | Cerrar mes actual |
| POST | `/api/admin/profiles/{slug}/habits/reorder` | Reordenar hábitos (drag & drop) |
| GET | `/api/admin/comparison/charts` | **Gráficos comparativos entre perfiles** |

📖 **Documentación interactiva**: `http://localhost:8765/api/docs`

---

## 🔄 Migración de Base de Datos

> **Nota**: El esquema completo de la base de datos está documentado en [DATABASE.md](./DATABASE.md).

### Cambio de Motor de Base de Datos

El único archivo a modificar es `.env`:

```env
# Producción con Supabase
DATABASE_URL="postgresql://postgres:PASSWORD@db.PROJECT.supabase.co:5432/postgres"
```

Con SQLAlchemy, **no se necesita cambiar ningún otro archivo**.

### Alembic Migraciones (Producción)

HábitosFam usa **Alembic** para migraciones de esquema. Las migraciones se ejecutan automáticamente al iniciar la aplicación.

#### Comandos常用:

```bash
# Instalar Alembic (ya incluido en requirements.txt)
pip install alembic

# Ejecutar todas las migraciones pendientes
alembic upgrade head

# Revertir la última migración
alembic downgrade -1

# Crear una nueva migración (después de cambios en modelos)
alembic revision --autogenerate -m "descripcion del cambio"

# Ver historial de migraciones
alembic history
```

#### Para sistemas en producción que nunca usaron Alembic:

Si tienes una base de datos existente (solo con `create_tables()`), ejecuta:

```bash
# La migración inicial crea el esquema completo v3.3
alembic upgrade head
```

Esto detectará automáticamente el estado actual y aplicará las migraciones necesarias.

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

### Opción recomendada: Render.com (⭐ más fácil con `render.yaml`)

El proyecto incluye un archivo `render.yaml` (Infrastructure as Code) que configura automáticamente el entorno "Full Stack" (Node.js + Python):

1. Sube tu código a GitHub.
2. En [render.com](https://render.com) → New → **Blueprint** (Infrastructure as Code).
3. Conecta tu repositorio. Render leerá el esquema y configurará los comandos solitos:
   - **Build**: Compilará el frontend con `npm run build` e instalará dependencias de Python con `pip`.
   - **Start**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
4. Deploy automático configurado ✅

> ⚠️ En Render gratuito, la instancia duerme tras 15min sin tráfico. El primer acceso tarda ~30s en despertar.  
> Para datos persistentes, usa una URL de PostgreSQL (Supabase gratis) en `DATABASE_URL`.
