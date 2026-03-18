# 🎨 Definición Arquitectónica de Frontend e Interfaz de Usuario (UI) – HábitosFam

Este documento establece los estándares, arquitectura y principios visuales para el frontend de la plataforma **HábitosFam**. El objetivo es mantener una experiencia de usuario (UX) unificada, fluida, fuertemente gamificada y con acabados visuales "premium".

---

## 🏗️ 1. Stack Tecnológico Frontend

El frontend está diseñado para ser ultraligero, rápido y libre de pesados frameworks JS, manteniendo tipado fuerte para la lógica de negocio.

- **Estructura y Core:** Vanilla HTML5, CSS3, JavaScript.
- **Lógica e Integración:** TypeScript (compilado vía Vite).
- **Procesamiento y Build:** Vite (`vite.config.ts`).
- **Gráficos y Visualización:** Chart.js (para tendencias semanales/mensuales/anuales).
- **Capacidades PWA:** Archivo de manifiesto (`manifest.json`), Favicon SVG, instalable en dispositivos móviles.

---

## 🧠 2. Principios de Experiencia de Usuario (UX) e Interfaz (UI)

La interfaz se basa en un sistema de recompensas psicológicas (**Dopamine UI**) orientado a mantener el _engagement_ diario de la familia.

### 2.1. Diseño Base y "Look & Feel"
- **Glassmorphism y Efectos Translucidos:** Uso nativo de `backdrop-filter: blur(20px)` y `background: rgba(...)` para emular cristal o superficies esmeriladas.
- **Bordes y Sombras Suaves:** Radios de borde exagerados y amigables (`--radius: 20px` para contenedores grandes, `--radius-sm: 12px` para tarjetas interactuables).
- **Modo Oscuro (Por Defecto):** Fondo profundo (`#0f0a1e`) con elementos de superficie (`#1a1230`) e iluminaciones radiales.
- **Tipografía Moderna:** 
  - Títulos y números destacados: **Baloo 2** (para un toque amigable y lúdico).
  - Cuerpo del texto y lectura: **Nunito** (para claridad y legibilidad).

### 2.2. Gamificación e Interacción
- **Micro-interacciones:** Retroalimentación inmediata al completar acciones.
  - Generación local de *brillos* al marcar micro-hábitos.
  - Lluvia de **Confetti** al completar un hábito principal en su totalidad o al cerrar el día perfecto.
- **Retroalimentación Auditiva:** Efectos de sonido reproducidos dinámicamente (`playMicroCheckSound`, `playCheckSound`).
- **Estados de "Maestría":** Una vez que un hábito es dominado (21+ días), su UI cambia (brillo dorado, animación *pulse-crown*).

### 2.3. Psicología de Color por Entidad (Temas)
Cada miembro de la familia (o el dashboard grupal) cuenta con su propia paleta inyectada globalmente vía variables CSS (`styles.css`):
- **Alana (`--alana-primary: #a855f7`):** Tonos Purpuras/Lilas. Gradientes de `#c084fc` a `#818cf8`.
- **Sofía (`--alana-primary: #ec4899`):** Tonos Rosas/Naranjas. Gradientes de `#f472b6` a `#fb923c`.
- **Familia (`--family-primary: #f59e0b`):** Tonos Ámbar/Rojos.

---

## 🏛️ 3. Arquitectura de Interfaces (Pantallas)

El sistema emplea un esquema de aplicaciones estáticas múltiples, dividiendo claramente los contextos operativos:

### 3.1. Aplicación Principal (`index.html`)
La aplicación de uso diario para toda la familia.
- **Overlays:** Pantalla de Log in basada en PIN (`login-overlay`), Canvas de Confetti (`confetti-canvas`).
- **Header:** Nombre de la aplicación, toggle de modo Claro/Oscuro, badge del usuario actual y botón para cerrar sesión.
- **Pestañas (Tabs):** Navegación inyectada dinámicamente en `<nav class="tab-nav">` dependiendo de los perfiles activos e incluyendo un Tab de "Famila".
- **Área Principal (`main`):** El contenedor principal donde se inyectan dinámicamente las Secciones de Perfil. Incluye la Tarjeta de Hero (con avatar, edad y racha), las estadísticas de ganancias, las Barras de Progreso Diario y el Grid de Hábitos.

### 3.2. Panel Administrativo (`admin.html`)
Diseñado para la configuración por parte de los padres (requiere PIN global de administrador).
- **Estética:** Retiene el look limpio, pero más sobrio.
- **Navegación Vertical/Pestañas:** Separación clara en: Perfiles (👥), Hábitos (📋), Recompensas (💰), Ajustes (⚙️) y Datos (📊).
- **Gestión Avanzada:** Uso de componentes modales (`#habit-modal`, `#profile-modal`) para CRUD completo. Drag & Drop nativo para reordenamiento de hábitos. Formularios embebidos para variables de sistema.

---

## 🧩 4. Componentes de UI Core

### 4.1. Tarjeta de Hábito (`.habit-card`)
- **Estructura Interna:** Icono base, Títulos, Subtítulos/Motivación, Contador de Estrellas, Botón/Checkbox de estado.
- **Expansión Modular:** Soporte para acordeones ocultos (`.mini-tasks`) que alojan los micro-hábitos.
- **Estados Dinámicos:** Asignación de clases nativas (`.completed`, `.mastered`) que desencadenan alteraciones estructurales de CSS (e.g., bordes dorados e iconos interactivos).

### 4.2. Gráficos y Dashboard (`Chart.js`)
- Embebidos en el dashboard Familiar o en las vistas de "Tendencias" individuales.
- Diseño minimalista, omitiendo grillas de fondo invasivas, preservando los gradientes de color del usuario pertinente.

### 4.3. Modales y Overlays
- Fondos de oscurecimiento (`.modal-overlay` o `backdrop-filter`).
- Contenedores centralizados con animación al invocar (e.g., el modal principal de "¡Increíble!" tras realizar todos los retos diarios).

---

## 🖥️ 5. Flujos Lógicos Frontend (Scripts)

La mecánica principal reside en los "Smart Scripts" ubicados bajo el folder `/scripts/`:
- **Inyección DOM (`app.ts` / `admin.ts`):** Dado que la aplicación usa HTML estático nativo, los scripts hacen `.innerHTML` y manipulan el DOM de manera eficiente escuchando la API en Axios/Fetch. No existe un Virtual DOM; en su lugar, se limpian y repintan contenedores específicos.
- **Manejo de Estados:** El estado de visualización actual (e.g., Tab Activo, PIN en uso, Dark Mode estatus) se almacena vía `localStorage` o en memoria local temporal.
- **Integración API REST:** Las llamadas a `api/habits.py` actualizan directamente la persistencia en base de datos; la UI espera confirmación de protocolo `200 OK` antes de realizar las animaciones complejas (como sumar estrellas en pantalla).
