<!-- Version: 1.0.0 | Updated: 2026-03-17 | Author: AI-assisted -->

# 📊 HábitosFam – Documentación de Base de Datos

> Este documento describe el esquema de base de datos completo de HábitosFam v3.3.  
> Stack: SQLAlchemy 2.0 + SQLite (PostgreSQL/MySQL compatible)

---

## Visión General

HábitosFam utiliza **9 tablas** para gestionar el sistema de hábitos familiares:

```
┌─────────────────────────────────────────────────────────────────────┐
│                          ESQUEMA DE DATOS                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐       │
│  │ app_settings │     │   profiles   │     │habit_templates│      │
│  └──────────────┘     └──────────────┘     └──────────────┘       │
│         │                      │                    │                 │
│         │                      │           ┌───────┴───────┐         │
│         │                      │           │               │         │
│         │                      │     ┌─────▼─────┐  ┌────▼────┐    │
│         │                      │     │micro_habits│  │reward_tiers│   │
│         │                      │     └───────────┘  └───────────┘    │
│         │                      │                                    │
│         │            ┌────────┴────────┐                          │
│         │            │                 │                          │
│    ┌────▼────┐ ┌────▼────┐     ┌────▼────┐                      │
│    │ day_logs │ │habit_entries│ │ week_rewards│                   │
│    └──────────┘ └──────────┘     └───────────┘                   │
│         │                                                    ┌────▼────┐
│         │                                                    │month_rewards│
│         └────────────────────────────────────────────────────┘─────────┘
└─────────────────────────────────────────────────────────────────────┘
```

---

## Tablas

### 1. app_settings

Configuración global de la aplicación (singleton, siempre `id=1`).

| Columna | Tipo | Nullable | Default | Descripción |
|---------|------|----------|---------|-------------|
| `id` | INTEGER | No | 1 | Clave primaria (siempre 1) |
| `admin_pin_hash` | VARCHAR(128) | No | - | Hash SHA-256 del PIN de admin |
| `currency_symbol` | VARCHAR(10) | Sí | "$" | Símbolo de moneda |
| `app_name` | VARCHAR(100) | Sí | "HábitosFam" | Nombre de la aplicación |
| `streak_bonus_days` | INTEGER | Sí | 7 | Días necesarios para bonus de racha |
| `streak_bonus_pct` | FLOAT | Sí | 1.5 | Multiplicador de bonus de racha (1.5 = +50%) |
| `updated_at` | DATETIME | Sí |.utcnow() | Última modificación |

**Índices**: PK (`id`)

---

### 2. profiles

Perfiles de los miembros de la familia (niños/adolescentes).

| Columna | Tipo | Nullable | Default | Descripción |
|---------|------|----------|---------|-------------|
| `id` | INTEGER | No | AUTO | Clave primaria |
| `slug` | VARCHAR(50) | No | - | Identificador único (ej: "alana", "sofia") |
| `name` | VARCHAR(100) | No | - | Nombre para mostrar |
| `age` | INTEGER | No | - | Edad del perfil |
| `avatar` | VARCHAR(10) | Sí | "⭐" | Emoji de avatar |
| `theme` | VARCHAR(50) | Sí | "default" | Tema visual |
| `level_idx` | INTEGER | Sí | 0 | Índice de nivel actual |
| `is_active` | BOOLEAN | Sí | True | Perfil activo |
| `pin_hash` | VARCHAR(128) | Sí | NULL | Hash SHA-256 del PIN del usuario |
| `weekly_reward_base` | FLOAT | Sí | 2.0 | Recompensa semanal base |
| `weekly_reward_full` | FLOAT | Sí | 4.0 | Recompensa semanal máxima (100%) |
| `monthly_reward_desc` | VARCHAR(255) | Sí | "Actividad especial" | Descripción de recompensa mensual |
| `monthly_min_pct` | FLOAT |Sí | 0.75 | Porcentaje mínimo para recompensa mensual |
| `balance` | FLOAT | Sí | 0.0 | Saldo acumulado virtual (economía) |
| `unlocked_themes` | TEXT | Sí | '["default"]' | JSON array de temas desbloqueados |
| `unlocked_avatars` | TEXT | Sí | '[]' | JSON array de avatares desbloqueados |
| `created_at` | DATETIME | Sí | .utcnow() | Fecha de creación |
| `updated_at` | DATETIME | Sí | .utcnow() | Última modificación |

**Índices**:
- PK (`id`)
- UNIQUE (`slug`)

**Relaciones**:
- `day_logs`: 1:N con DayLog
- `rewards`: 1:N con WeekReward
- `month_rewards`: 1:N con MonthReward
- `habit_templates`: 1:N con HabitTemplate
- `reward_tiers`: 1:N con RewardTier

---

### 3. habit_templates

Definiciones de hábitos asignados a cada perfil.

| Columna | Tipo | Nullable | Default | Descripción |
|---------|------|----------|---------|-------------|
| `id` | INTEGER | No | AUTO | Clave primaria |
| `profile_id` | INTEGER | No | - | FK → profiles.id |
| `habit_key` | VARCHAR(50) | No | - | Clave única del hábito (ej: "sport", "study") |
| `name` | VARCHAR(150) | No | - | Nombre del hábito |
| `icon` | VARCHAR(10) | Sí | "⭐" | Emoji del hábito |
| `category` | VARCHAR(50) | Sí | "general" | Categoría (deporte, estudio, hogar, etc.) |
| `stars` | INTEGER | Sí | 1 | Estrellas por completar |
| `description` | VARCHAR(255) | Sí | "" | Descripción corta |
| `details` | TEXT | Sí | "" | Detalles adicionales |
| `motivation` | VARCHAR(255) | Sí | "" | Frase motivacional |
| `sort_order` | INTEGER | Sí | 0 | Orden de visualización |
| `is_active` | BOOLEAN | Sí | True | Hábito activo |
| `consecutive_days` | INTEGER | Sí | 0 | Días consecutivos completados |
| `is_mastered` | BOOLEAN | Sí | False | Hábito dominado (21+ días) |
| `mastered_at` | DATETIME | Sí | NULL | Fecha cuando se alcanzó el dominio |
| `created_at` | DATETIME | Sí | .utcnow() | Fecha de creación |

**Índices**:
- PK (`id`)
- UNIQUE (`profile_id`, `habit_key`)

**Relaciones**:
- `profile`: N:1 con Profile
- `micro_habits`: 1:N con MicroHabit

---

### 4. micro_habits

Sub-tareas individuales dentro de un hábito.

| Columna | Tipo | Nullable | Default | Descripción |
|---------|------|----------|---------|-------------|
| `id` | INTEGER | No | AUTO | Clave primaria |
| `habit_template_id` | INTEGER | No | - | FK → habit_templates.id |
| `description` | VARCHAR(255) | No | - | Texto de la micro-tarea |
| `sort_order` | INTEGER | Sí | 0 | Orden de visualización |
| `is_active` | BOOLEAN | Sí | True | Micro-hábito activo |
| `created_at` | DATETIME | Sí | .utcnow() | Fecha de creación |

**Índices**:
- PK (`id`)

**Relaciones**:
- `habit_template`: N:1 con HabitTemplate

---

### 5. reward_tiers

Niveles de recompensa configurables por perfil.

| Columna | Tipo | Nullable | Default | Descripción |
|---------|------|----------|---------|-------------|
| `id` | INTEGER | No | AUTO | Clave primaria |
| `profile_id` | INTEGER | No | - | FK → profiles.id |
| `tier_type` | VARCHAR(20) | Sí | "weekly" | Tipo: "weekly" o "monthly" |
| `min_pct` | FLOAT | No | - | Porcentaje mínimo (0.0 - 1.0) |
| `multiplier` | FLOAT | No | - | Multiplicador de recompensa |
| `label` | VARCHAR(100) | Sí | "" | Nombre del nivel (ej: "Bronce", "Plata", "Oro") |
| `emoji` | VARCHAR(10) | Sí | "" | Emoji del nivel |
| `sort_order` | INTEGER | Sí | 0 | Orden de visualización |

**Índices**:
- PK (`id`)

**Relaciones**:
- `profile`: N:1 con Profile

---

### 6. day_logs

Registro diario de cumplimiento de hábitos.

| Columna | Tipo | Nullable | Default | Descripción |
|---------|------|----------|---------|-------------|
| `id` | INTEGER | No | AUTO | Clave primaria |
| `profile_id` | INTEGER | No | - | FK → profiles.id |
| `date` | VARCHAR(10) | No | - | Fecha (ISO: "YYYY-MM-DD") |
| `completed_count` | INTEGER | Sí | 0 | Hábitos completados |
| `total` | INTEGER | Sí | 6 | Total de hábitos |
| `pct` | FLOAT | Sí | 0.0 | Porcentaje completado (0.0 - 1.0) |
| `day_done` | BOOLEAN | Sí | False | Día completado (≥50%) |
| `bonus_star` | BOOLEAN | Sí | False | Estrella bonus por día perfecto |
| `created_at` | DATETIME | Sí | .utcnow() | Fecha de creación |
| `updated_at` | DATETIME | Sí | .utcnow() | Última modificación |

**Índices**:
- PK (`id`)
- UNIQUE (`profile_id`, `date`)
- INDEX (`date`)

**Relaciones**:
- `profile`: N:1 con Profile
- `habit_entries`: 1:N con HabitEntry

---

### 7. habit_entries

Estado individual de cada hábito dentro de un DayLog.

| Columna | Tipo | Nullable | Default | Descripción |
|---------|------|----------|---------|-------------|
| `id` | INTEGER | No | AUTO | Clave primaria |
| `day_log_id` | INTEGER | No | - | FK → day_logs.id |
| `habit_id` | VARCHAR(50) | No | - | ID del hábito (habit_key) |
| `done` | BOOLEAN | Sí | False | Hábito completado |
| `mini_tasks_json` | TEXT | Sí | "{}" | JSON con estado de micro-hábitos |
| `toggled_at` | DATETIME | Sí | NULL | Última vez que se marcó |

**Índices**:
- PK (`id`)
- UNIQUE (`day_log_id`, `habit_id`)

**Relaciones**:
- `day_log`: N:1 con DayLog

---

### 8. week_rewards

Resumen de recompensa semanal por perfil.

| Columna | Tipo | Nullable | Default | Descripción |
|---------|------|----------|---------|-------------|
| `id` | INTEGER | No | AUTO | Clave primaria |
| `profile_id` | INTEGER | No | - | FK → profiles.id |
| `week_start` | VARCHAR(10) | No | - | Fecha inicio semana (lunes) |
| `week_end` | VARCHAR(10) | No | - | Fecha fin semana (domingo) |
| `days_completed` | INTEGER | Sí | 0 | Días completados en la semana |
| `total_pct` | FLOAT | Sí | 0.0 | Porcentaje total de la semana |
| `streak_at_close` | INTEGER | Sí | 0 | Racha al cerrar la semana |
| `shield_used` | BOOLEAN | Sí | False | Si se usó el escudo protector |
| `earned_amount` | FLOAT | Sí | 0.0 | Monto ganado |
| `reward_paid` | BOOLEAN | Sí | False | Si la recompensa fue pagada |
| `notes` | TEXT | Sí | NULL | Notas adicionales |
| `created_at` | DATETIME | Sí | .utcnow() | Fecha de creación |

**Índices**:
- PK (`id`)
- UNIQUE (`profile_id`, `week_start`)

**Relaciones**:
- `profile`: N:1 con Profile

---

### 9. month_rewards

Resumen de recompensa mensual por perfil.

| Columna | Tipo | Nullable | Default | Descripción |
|---------|------|----------|---------|-------------|
| `id` | INTEGER | No | AUTO | Clave primaria |
| `profile_id` | INTEGER | No | - | FK → profiles.id |
| `month_key` | VARCHAR(7) | No | - | Mes (formato: "YYYY-MM") |
| `days_completed` | INTEGER | Sí | 0 | Días completados en el mes |
| `total_days` | INTEGER | Sí | 0 | Total de días del mes |
| `pct` | FLOAT | Sí | 0.0 | Porcentaje del mes |
| `reward_unlocked` | BOOLEAN | Sí | False | Recompensa mensual desbloqueada |
| `reward_paid` | BOOLEAN | Sí | False | Recompensa pagada |
| `reward_desc` | VARCHAR(255) | Sí | NULL | Descripción de la recompensa |
| `notes` | TEXT | Sí | NULL | Notas adicionales |
| `created_at` | DATETIME | Sí | .utcnow() | Fecha de creación |

**Índices**:
- PK (`id`)
- UNIQUE (`profile_id`, `month_key`)

**Relaciones**:
- `profile`: N:1 con Profile

---

## Migraciones

### Historia de Migraciones

| Fecha | Versión | Descripción |
|-------|---------|-------------|
| 2026-03-15 | c929fa34db3d | Agregar columnas de dominio de hábitos (consecutive_days, is_mastered, mastered_at) |
| 2026-03-17 | 1231155072f6 | Agregar campos de economía virtual (balance, unlocked_themes, unlocked_avatars) |

### Ejecutar Migraciones

```bash
# Instalar Alembic si no está instalado
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

### Migración para Sistemas en Producción

Si tienes una base de datos existente que nunca usó Alembic (solo `create_all()`), ejecuta:

```bash
# Crear la migración inicial desde el estado actual
alembic revision --autogenerate -m "initial from existing database"
```

Esto creará una migración que representa el estado actual del esquema.

---

## Cambios de Esquema entre Versiones

### v3.0 → v3.1
- Sin cambios en el esquema

### v3.1 → v3.2
- Sin cambios en el esquema

### v3.2 → v3.3
- Agregadas columnas a `habit_templates`:
  - `consecutive_days` (INTEGER, default 0)
  - `is_mastered` (BOOLEAN, default False)
  - `mastered_at` (DATETIME, nullable)
- Agregadas columnas a `profiles`:
  - `balance` (FLOAT, default 0.0)
  - `unlocked_themes` (TEXT, default '["default"]')
  - `unlocked_avatars` (TEXT, default '[]')

---

## Notas Técnicas

### Compatibilidad Multi-DB

SQLAlchemy 2.0 garantiza compatibilidad con:
- **SQLite**: Desarrollo local (por defecto)
- **PostgreSQL**: Producción recomendada (Supabase, Railway)
- **MySQL**: Alternativa de producción

Para cambiar de base de datos, solo modificar `DATABASE_URL` en `.env`:

```env
# SQLite (desarrollo)
DATABASE_URL="sqlite:///./habitosfam.db"

# PostgreSQL / Supabase
DATABASE_URL="postgresql://postgres:PASSWORD@db.PROJECT.supabase.co:5432/postgres"

# MySQL
DATABASE_URL="mysql+pymysql://user:pass@host:3306/habitosfam"
```

### Índices y Rendimiento

- `profiles.slug`: Búsqueda por slug (login)
- `day_logs.date + profile_id`: Consulta de logs por rango de fechas
- `habit_templates.profile_id`: Carga de hábitos por perfil

### Foreign Keys

Todas las tablas usan `ON DELETE CASCADE` para eliminación automática de registros relacionados.

---

## Diagramas ER (simplificado)

```
app_settings (1) ─────────┐
                          │
profiles (M) ◄────────────┤
     │                   │
     ├─► habit_templates (M)
     │         │
     │         ├─► micro_habits (M)
     │
     ├─► reward_tiers (M)
     │
     └─► day_logs (M)
               │
               └─► habit_entries (M)
               │
               └─► week_rewards (M)
               │
               └─► month_rewards (M)
```

---

## Seeds (Datos Iniciales)

Los datos iniciales se insertan automáticamente en `crud.seed_default_data()`:

- **AppSettings**: Configuración global por defecto
- **Profiles**: Alana (7 años) y Sofía (16 años)
- **HabitTemplates**: 7 hábitos por perfil
- **MicroHabits**: 3 micro-hábitos por hábito
- **RewardTiers**: 5 niveles de recompensa semanal
