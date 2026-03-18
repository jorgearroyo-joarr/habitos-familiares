# 🚀 Mejoras de Experiencia de Usuario (UX) & Gamificación

Este documento detalla los requerimientos y la guía de implementación para las mejoras de UX propuestas para HábitosFam. Estas características conforman la actualización **v2.3.0**.

---

## 🧒 1. Mejoras para Usuarios (Hijos)

### 1.1 Economía Virtual Dinámica (Tienda)

**Objetivo:** Permitir a los niños gastar sus "estrellas" o "monedas" en personalizar su perfil.
**Requerimientos:**

- **Backend:**
  - Añadir soporte en el modelo `Profile` para campos como `unlocked_themes` (JSON) y `unlocked_avatars` (JSON), o crear una tabla `Purchase`.
  - Endpoint `/api/profiles/{slug}/purchase` para deducir saldo y añadir el item.
- **Frontend (`app.ts` / `index.html`):**
  - Nueva pestaña o modal "Tienda".
  - Lista de temas (ej. "Theme Neón", "Theme Princesa") y avatares con precios.
  - Al comprar, cambiar dinámicamente el `theme` del perfil.

### 1.2 Barra de Progreso a "Siguiente Nivel"

**Objetivo:** Hacer tangibles los `RewardTiers` (Plata, Oro, Diamante) durante el transcurso de la semana.
**Requerimientos:**

- **Backend:** `compute_week_stats` ya calcula el % actual y `get_profile_dashboard` lo entrega.
- **Frontend (`app.ts`):**
  - En el Profile Hero, debajo de las estrellas de la semana, añadir una barra de progreso que muestre visualmente cuánto falta para el siguiente Tier configurado.
  - Mensaje: "¡A 2 estrellas del nivel Oro!".

### 1.3 Mejoras UI Móvil (Gestos y Respuesta Háptica)

**Objetivo:** Interacción más fluida y gratificante en móviles.
**Requerimientos:**

- **Frontend (`app.ts`):**
  - Implementar API de vibración: `if (navigator.vibrate) navigator.vibrate(50)` al hacer check en un micro-hábito, y `navigator.vibrate([100, 50, 100])` al completar todo.
  - (Opcional) Soporte de "Swipe right" en `.habit-card` para marcar todas las micro-tareas como hechas de un solo gesto.

### 1.4 Optimistic UI

**Objetivo:** Eliminar cualquier tiempo de espera en la UI al marcar hábitos.
**Requerimientos:**

- **Frontend (`app.ts`):**
  - La función `toggleHabit` y `toggleMiniTask` ya actualizan el estado local primero. Asegurar que las animaciones, sonidos y renderizado ocurran *antes* o *sin esperar* la resolución del `fetch` al API.
  - Revertir el estado visual y mostrar un "toast" de error si el `fetch` falla.

---

## 👑 2. Mejoras para Administradores (Padres)

### 2.1 Analíticas de Puntos de Fricción

**Objetivo:** Identificar qué hábitos cuestan más trabajo.
**Requerimientos:**

- **Backend:** Endpoint en `/api/admin/insights`.
  - Calcular: Hábito con menos "checks" en los últimos 7 días.
  - Calcular: Horario promedio de cierre diario (`DayLog.timestamp`).
- **Frontend (`admin.ts` / `admin.html`):**
  - Nueva sección "Insights 🧠" en el Dashboard.
  - Mostrar tarjetas con alertas: "El hábito 'Tender la cama' solo se ha hecho 2 veces esta semana."

### 2.2 Modo "Vista Previa" (Impersonate)

**Objetivo:** Entrar como el hijo sin tener que hacer logout/login constantemente.
**Requerimientos:**

- **Frontend (`admin.ts`):**
  - En la lista de perfiles, un botón "Ver como..." que abra `index.html` en una nueva pestaña pasando un token de impersonación o configuración especial en el `localStorage` temporalmente.

### 2.3 Acciones Masivas (Aprobar Semana Múltiple)

**Objetivo:** Cerrar la semana para todos los hijos con un solo clic.
**Requerimientos:**

- **Backend:** Endpoint `/api/admin/bulk-close-week` que itere sobre perfiles activos y llame a `close_week(profile.id)`.
- **Frontend (`app.ts` / `admin.ts`):**
  - En la pestaña "Familia" o Admin Dashboard, botón "Aprobar Semana para Todos".
  - Alert de confirmación y resumen de lo procesado.

### 2.4 Registro de Auditoría Visual (Hora de Checks)

**Objetivo:** Detectar cuando los niños hacen todos los checks en 30 segundos juste antes de dormir.
**Requerimientos:**

- **Backend:** El modelo `HabitEntry` y/o modelo JSON de `mini_tasks` debería almacenar la fecha/hora de la última modificación (timestamp).
- **Frontend (`admin.ts`):**
  - En la sección "Datos", al expandir un día, mostrar la "Hora de guardado" de los hábitos.
  - Si múltiples hábitos se guardaron en la misma ventana de 1 minuto, marcarlos en visualmente sospechosos (amarillo).

---

## 🗺️ Fases de Implementación Sugeridas

1. **Fase 1 (Quick Wins):** Respuesta Háptica, Optimistic UI, y Vista Previa (Admin).
2. **Fase 2 (Visual):** Barra al Siguiente Nivel y Auditoría Visual Básica.
3. **Fase 3 (Lógica):** Acciones Masivas y Analíticas de Puntos de Fricción.
4. **Fase 4 (Major Feature):** Economía Virtual (Tienda de Avatares/Temas).
