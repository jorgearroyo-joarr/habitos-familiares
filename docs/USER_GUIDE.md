<!-- Version: 2.1.0 | Updated: 2026-03-15 | Author: AI-assisted -->
# 📖 HábitosFam – Guía de Usuario

> Para papás y mamás — sin tecnicismos

---

## ¿Qué es HábitosFam?

HábitosFam es una app para el celular o computadora que ayuda a tus hijas a construir buenos hábitos de forma divertida, con:

- ✅ Una lista de verificación diaria personalizada para cada hija
- 🌟 Estrellas y recompensas económicas para motivarlas
- 🔥 Un contador de racha para mantener el momentum
- 📊 Un panel de control para que veas el progreso como papá/mamá

---

## 👩‍👧 Gestión de Perfiles (Dinámico)

HábitosFam v3 es totalmente flexible. A través del panel administrativo puedes:
- **Agregar nuevos perfiles**: No solo Alana y Sofía, puedes añadir más hijos/as.
- **Personalizar temas**: Cada perfil tiene su propio color, avatar y edad.
- **Seguridad individual**: Cada usuario tiene su propio **PIN de 4 dígitos** para evitar que se marquen hábitos de otros.

### 📋 Los Hábitos y Micro-hábitos
Cada perfil tiene su propia lista de hábitos. Lo más importante son los **micro-hábitos**:
1. Toca la flecha ▼ en cualquier tarjeta para ver el detalle.
2. Marca cada micro-hábito individualmente.
3. Al completar todos los micro-hábitos, el hábito principal se marca automáticamente con una celebración de **confetti**!

---

## ⚙️ Configuración del Sistema
En la pestaña **Ajustes** del panel Admin, puedes cambiar:
- **Nombre de la App**: Personaliza el título que aparece en el header (ej: "Familia Arroyo").
- **Símbolo de Moneda**: Cambia de `$` a `₡`, `€`, `RD$`, etc.
- **Bonus de Racha**: Define cuántos días seguidos se necesitan para el bonus y el porcentaje extra.

---

## 💰 Sistema de Recompensas
Las recompensas ya no son fijas. En la pestaña **Recompensas** de Admin puedes configurar "Niveles" por cada perfil:
- **Base Semanal**: El monto mínimo garantizado.
- **Full Semanal**: El monto máximo al llegar al 100%.
- **Niveles Escalados**: Define etiquetas (ej: "Bronce", "Plata", "Oro") y qué porcentaje de cumplimiento requieren para ganar el multiplicador de dinero.
- **Recompensa Mensual**: Define un premio especial (ej: "Salida al cine") y el porcentaje mínimo para desbloquearlo.

---

## 💰 ¿Cómo se ganan las recompensas?

### Recompensa del día (Dopamina ✨)
Cada micro-hábito da un destello visual. Completar el hábito principal activa **Confetti** y sonidos premium.

### Recompensa semanal (Económica)
El sistema calcula automáticamente el pago basado en el porcentaje de cumplimiento y los niveles configurados.
> 🔥 **Bonus de racha**: Al mantener la constancia, el sistema aplica el multiplicador configurado automáticamente.

### Recompensa mensual (Logro Especial)
Se desbloquea al final del mes si se alcanza el objetivo configurado. Aparece un botón de "¡Recompensa desbloqueada!" en el panel familiar.

---

## 🔥 ¿Qué es la racha?

Es el número de días consecutivos donde completaron al menos 3 de 6 hábitos (≥50%).

- La racha se ve en el encabezado de cada perfil
- Si llegan a 7 días = bonus en la recompensa semanal
- Niveles que se desbloquean con la racha:
  - **Alana:** Exploradora → Aventurera → Heroína → Leyenda
  - **Sofía:** Campeona → Guerrera → Maestra → Élite

**Escudo protector** 🛡️: una vez por semana pueden tener 1 día libre sin perder la racha.

---

## ⚙️ Panel de Administración (para padres)

Abre **http://localhost:8765/admin** (o el enlace en el panel Familia de la app).

**PIN por defecto:** `1234` (cámbialo en el archivo `.env`)

### ¿Qué puedes hacer?

1. **Perfiles** → Crear/Editar hijos, cambiar sus PINs y sus montos base de dinero.
2. **Hábitos** → Definir qué hábitos y micro-hábitos tiene cada perfil.
3. **Recompensas** → Configurar niveles de pago (Bronce, Plata, Oro).
4. **Ajustes** → Cambiar nombre de la app, moneda y parámetros de racha.
5. **Datos** → Ver logs detallados, borrar días erróneos y exportar a Excel/CSV.

### Seguridad
- **PIN Admin**: Por defecto es `1234`. Se puede cambiar en la pestaña "Ajustes".
- **PIN Usuario**: Cada hijo tiene el suyo. El "Supervisor" (Admin) puede marcar hábitos en cualquier perfil sin necesidad del PIN del hijo.

---

## 🚀 Cómo abrir la app

### Opción 1: Doble clic (sin internet, sin servidor)
- Doble clic en `index.html` o `admin.html`
- Funciona sin servidor, datos guardados en el navegador

### Opción 2: Con servidor (recomendado para persistencia)
```
1. Abre una terminal/PowerShell en la carpeta good_habits/
2. Ejecuta: uvicorn backend.main:app --reload --port 8765
3. Abre: http://localhost:8765
4. Admin: http://localhost:8765/admin
```

---

## ❓ Preguntas frecuentes

**¿Qué pasa si se olvidad un día?**
El escudo protector (1 por semana) puede cubrir ese día sin romper la racha.

**¿Se pueden cambiar los hábitos?**
Sí, editando el archivo `data.js`. Seguir las instrucciones en `AGENTS.md`.

**¿Los datos se pierden si cierro la app?**
No. Los datos se guardan en la base de datos `habitosfam.db` de forma permanente.

**¿Puedo usar esto en el teléfono?**
Sí. (Ver guía en `TECHNICAL.md`).

**¿Cómo lo pongo en internet (gratis)?**
Sigue la guía de "Cloud Hosting" en `TECHNICAL.md` para usar Render o Fly.io sin costo.
