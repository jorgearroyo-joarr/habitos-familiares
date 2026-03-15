# 🗺️ HábitosFam – Roadmap Estratégico

> **Versión actual:** v2.1.1 · **Última actualización:** Marzo 2026

---

## ✅ Estado actual (v2.1.1)

- [x] App web gamificada (HTML/CSS/JS) con diseño premium dark-mode
- [x] Gestión Dinámica de Perfiles (CRUD ilimitado)
- [x] Hábitos y Micro-hábitos configurables por perfil
- [x] Panel Administrativo con PIN y niveles de recompensa personalizables
- [x] Sistema de App Settings (Nombre de App, Moneda, Bonus)
- [x] Dashboard Familiar Unificado (vista Supervisor)
- [x] Dopamine UI: Micro-sparkles y confetti burst
- [x] Backend FastAPI robusto con SQLite persistente
- [x] Documentación completa (Técnica, Guía, Agent, Roadmap, IMPROVEMENTS)
- [x] Reset de datos integral desde el panel admin
- [x] Localización completa de la API al español (es-MX)
- [x] **[v2.1.1]** Efectos de Micro-Dopamina (confeti + brillos locales)
- [x] **[v2.1.1]** Efectos de Sonido (playCheckSound, playMicroCheckSound)
- [x] **[v2.1.1]** Notificaciones de recordatorio (Web Notifications API)
- [x] **[v2.1.1]** Modo oscuro/claro (toggle con persistencia)
- [x] **[v2.1.1]** Backups Automáticos (antes de operaciones críticas)
- [x] **[v2.1.1]** Favicon y PWA manifest (instalable en móvil)

---

## 🚧 v2.2.0 – Analítica y Plantillas (Próximas 2-4 semanas)

- [ ] **Gráficos de Tendencia**: Integrar `Chart.js` para visualizar el cumplimiento semanal/mensual.
- [ ] **Catálogo de Plantillas**: Hábitos predefinidos por edad (Higiene, Estudio, Deporte).
- [ ] **Editor Drag & Drop**: Reordenar hábitos y categorías arrastrando elementos en admin.
- [ ] **Cierre de Mes Automático**: Consolidación de recompensas sin intervención manual.
- [ ] **Migraciones con Alembic**: Versionado formal del esquema de base de datos.

---

## 📱 v3.0.0 – Migración Cloud y Movilidad (Mes 3-4)

- [ ] **Migrar a Supabase/PostgreSQL**: Persistencia en la nube para acceso multi-dispositivo.
- [ ] **Evolución del Avatar**: El avatar gana accesorios según la racha de días perfectos.
- [ ] **QR de acceso rápido**: Abrir perfiles mediante escaneo de código físico.
- [ ] **Deploy Pro**: Servidor siempre activo en Railway/Render con RLS (Row-Level Security).

---

## 🤖 v3.1.0 – Accesibilidad e IA (Mes 5-6)

- [ ] **Modo de Lectura (TTS)**: El sistema lee los hábitos en voz alta para niños pequeños.
- [ ] **Navegación por Voz**: Comandos simples como "Completar mi día".
- [ ] **Sugerencias Adaptativas**: IA que recomienda retos basados en el desempeño histórico.
- [ ] **Reportes por Email**: Resumen semanal automático para los padres.

---

## 👨‍👩‍👧 v4.0.0 – Multi-Familia (Mes 6+)

- [ ] **Cuentas de familia**: Múltiples padres, múltiples hijos con roles definidos.
- [ ] **Modo compartido familiar**: Hitos globales para toda la casa.
- [ ] **Marketplace AI**: IA que genera planes de hábitos personalizados por temporada.

---

## 🔒 Principios de diseño

| Principio | Decisión |
|-----------|----------|
| **Sostenibilidad** | Micro-hábitos progresivos, no todo de golpe |
| **Resiliencia** | Escudo semanal, días parciales cuentan |
| **Dopamina** | Inmediata (check), diaria (completar), semanal ($), mensual (reward) |
| **Progresión** | Niveles, rachas, badges y evolución de avatar |
| **Privacidad** | Datos en casa primero (SQLite), nube con cifrado opcional |
| **Portabilidad** | DB agnóstico, PWA, export CSV siempre disponible |

---

## 📊 Métricas de éxito

| Métrica | Objetivo Mes 1 | Objetivo Mes 3 |
|---------|----------------|----------------|
| Días activos / mes | ≥ 20/30 | ≥ 25/30 |
| Hábitos diarios completados | ≥ 4/6 | ≥ 5/6 |
| Racha máxima | 7 días | 21 días |
| Recompensa semanal media | $2 (Alana) / $6 (Sofía) | $3 / $8 |
| Recompensa mensual desbloqueada | 1/2 hijas | 2/2 hijas |
