# 🎁 Metodología y Flujo de Recompensas – HábitosFam

Este documento detalla la estructura lógica, el flujo de datos y la psicología detrás del sistema de gamificación y recompensas de HábitosFam (versión 3+).

---

## 🧠 1. Metodología de Recompensas (Bucle de Dopamina)

El sistema está diseñado bajo un modelo de **Refuerzo Positivo Escalonado**, dividiendo las recompensas en cuatro horizontes temporales para maximizar la retención y formar el hábito:

1. **Micro-Dopamina (Inmediata):** Al marcar un sub-hábito (micro-tarea), el sistema emite un sonido corto (`playMicroCheckSound`) y genera un brillo (sparkle) visual localizado en el cursor.
2. **Dopamina Diaria (Corto Plazo):** Al completar todos los micro-hábitos de una tarjeta, la tarjeta entera se marca como Completada. Se emite un sonido de completación mayor (`playCheckSound`). Si se logra el 100% de los hábitos del día, se dispara una ovación con lluvia de **Confetti** general.
3. **Recompensa Económica (Mediano Plazo - Semanal):** El objetivo transaccional. Ganancias de dinero ficticio o real escalonadas de acuerdo al porcentaje de cumplimiento semanal, impulsadas por un multiplicador de **Racha (Streak)**.
4. **Logro Especial (Largo Plazo - Mensual):** Una recompensa no monetaria (ej. "Salida al cine", "Helado doble") que requiere constancia sostenida (ej. > 75% mensual) para desbloquearse.

### 🛡️ Escudo Protector Semanal
Para evitar la frustración de perder una larga racha por un solo día malo o enfermedad, el cálculo de las Rachas permite que el usuario mantenga su racha viva siempre que haga **al menos el 50% de sus hábitos** cada día.

---

## ⚙️ 2. Flujo de Datos y Modelado en Base de Datos

Las recompensas no están harcodeadas; son dinámicas por perfil y gestionadas desde el panel de administración.

### 2.1 Entidades Clave (SQLAlchemy / SQLite)

- **`AppSettings` (Meta-datos globales):**
  - Define la moneda (`currency_symbol`), los días necesarios para ganar bonus (`streak_bonus_days`, default 7) y el multiplicador de dicho bonus (`streak_bonus_pct`, default 1.5).
- **`Profile` (Definición Base de Usuario):**
  - Contiene montos de contingencia: `weekly_reward_base` y `weekly_reward_full`.
  - Define la meta mensual (`monthly_reward_desc`, `monthly_min_pct`).
- **`RewardTier` (Niveles Flexibles):**
  - Permite configurar tramos (Tiers). 
  - Ejemplo: `min_pct = 0.50` -> `multiplier = 0.5`, `min_pct = 0.85` -> `multiplier = 1.0`. Permite decir "Si cumples el 50%, ganas la mitad de la base, si cumples 85% ganas la base completa".
- **`DayLog` & `HabitEntry`:** Registros de completitud diaria pura.
- **`WeekReward` & `MonthReward`:** Tablas históricas que almacenan "Cierres" definitivos de semana/mes, para auditar qué se pagó y qué no (`reward_paid`).

---

## 🧮 3. Lógica de Cálculo (Backend `crud.py`)

### 3.1. Cálculo Semanal (`compute_week_stats`)
Cuando el sistema consulta o "Cierra" una semana, el backend ejecuta la siguiente lógica estricta:

1. **Conteo Diario:** Itera sobre todos los `DayLog` (Lunes a Domingo). Suma cuántas estrellas tiene el usuario e identifica si alcanzó el 50% (para mantener la racha).
2. **Estrellas Bonus (Maestría):** Si el usuario ha dominado un hábito (21 días consecutivos haciéndolo), recibe **Estrellas Bonus Gratuitas** (+1 por hábito maestro) en días en los que cumpla al menos la mitad de sus tareas, premiando la retención histórica.
3. **Multiplicador de Racha (Streak Bonus):** Si la racha actual iguala o supera el mínimo configurado globalmente (ej. 7 días), se aplica el multiplicador (ej. `x 1.5`).
4. **Proyección en Niveles (`RewardTiers`):** 
   - Evalúa el porcentaje total de éxito de la semana contra los tramos (`RewardTiers`) configurados por el administrador de mayor a menor.
   - Si no hay Tiers o no se llega a ninguno, el pago es 0.
   - Fórmula matemática final: `Pago = Base del Perfil * Multiplicador del Nivel Alcanzado * Multiplicador de Racha`.

### 3.2. Cálculo Mensual (`compute_month_stats`)
Menos estricto financieramente, más binario:
1. Analiza el mes natural (1 al 31).
2. Suma la cantidad de días "Válidos" (días con `>= 50%` de cumplimiento).
3. Obtiene el porcentaje total y lo compara contra `profile.monthly_min_pct` (ej. 75%).
4. Si se iguala o supera, retorna `reward_unlocked = True`.

---

## 🎨 4. Renderizado Frontend e Interacción Parental

### 4.1. Panel Familiar (`index.html` - `app.ts`)
- **Dashboard en Tiempo Real:** En el header de perfil, o en el Tab Familiar, se dibuja un "mini calendario" indicando qué días se cumplió la meta (`✔`), qué días fueron parciales (`+`) y los fallidos (`-`).
- **Vista de Ganancias:** Muestra un pre-cálculo ("Ganados esta semana: $3.50") renderizado directamente a partir del JSON que emite `compute_week_stats`. Múltiples re-creaciones de render ante cada click lo mantienen sincronizado.

### 4.2. Administración Parental (`admin.html` - `admin.ts`)
Los padres operan la aplicación como "Bancos". 
- Tienen un botón destructivo de "Cerrar Semana" o "Cerrar Mes".
- Estas peticiones API insertan en piedra de base de datos la fila dentro de `WeekReward` o `MonthReward`, permitiendo a los padres llevar una cuenta contable de "Lo que le debo a mis hijos". 
- La tabla de Recompensas provee celdas editables que alteran la asignación de `RewardTier` en tiempo real.
