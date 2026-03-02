# 🗺️ HábitosFam – Roadmap Estratégico

> **Versión actual:** v2.0.0 · **Última actualización:** Marzo 2026

---

## ✅ Estado actual (v2.0.0)

- [x] App web gamificada (HTML/CSS/JS) con diseño premium dark-mode
- [x] Gestión Dinámica de Perfiles (CRUD ilimitado)
- [x] Hábitos y Micro-hábitos configurables por perfil
- [x] Panel Administrativo con PIN y niveles de recompensa personalizables
- [x] Sistema de App Settings (Nombre de App, Moneda, Bonus)
- [x] Dashboard Familiar Unificado (vista Supervisor)
- [x] Dopamine UI: Micro-sparkles, sonidos y confetti burst
- [x] Backend FastAPI robusto con SQLite persistente
- [x] Documentación completa (Técnica, Guía, Agent, Roadmap)


---

## 🚧 v2.1.0 – Pulido y UX (Próximas 4 semanas)

- [ ] **Sincronización API↔Frontend**: reemplazar localStorage por llamadas al backend
- [ ] **Notificaciones de recordatorio**: alerta diaria a hora configurable (Web Notifications API)
- [ ] **Modo oscuro/claro**: toggle opcional
- [ ] **Historial visual**: gráfico de barras mensual estilo GitHub contribution heatmap
- [ ] **Avatar personalizable**: subida de foto de perfil
- [ ] **Favicon y PWA manifest**: instalable en móvil como app

---

## 🔄 v2.2.0 – Migración a PostgreSQL/Supabase (Mes 2)

> **OBJETIVO:** Persistencia en la nube para acceso multi-dispositivo.

- [ ] **Migrar a Supabase** (PostgreSQL): cambiar `DATABASE_URL` en `.env`
- [ ] **Autenticación con Supabase Auth**: reemplazar PIN con login de email
- [ ] **Row-Level Security (RLS)**: cada familia solo ve sus datos
- [ ] **Migraciones con Alembic**: versionado de esquema de base de datos
- [ ] **Deploy en Railway o Render**: servidor siempre activo
- [ ] **Variables de entorno seguras** en plataforma de hosting

### Pasos de migración SQLite → Supabase
```bash
# 1. Crear proyecto en supabase.com
# 2. Copiar connection string a .env
DATABASE_URL="postgresql://postgres:[password]@[host]:5432/postgres"

# 3. Crear tablas en Supabase (via SQLAlchemy)
python -c "from backend.database import create_tables; create_tables()"

# 4. Migrar datos existentes (script incluido en v2.2.0)
python scripts/migrate_sqlite_to_postgres.py
```

---

## 📱 v3.0.0 – App Móvil (Mes 3-4)

- [ ] **Progressive Web App (PWA)**: funciona offline, instalable, push notifications
- [ ] **React Native o Flutter**: app nativa para iOS/Android (evaluación)
- [ ] **QR de acceso rápido**: imprimir código QR en el cuarto para abrir la app
- [ ] **Modo "Hoy"**: pantalla simplificada para uso rápido antes de dormir
- [ ] **Integración con Google Calendar**: eventos de hábitos automáticos

---

## 🤖 v3.1.0 – Inteligencia y Personalización (Mes 5-6)

- [ ] **Sugerencias de hábitos adaptativas**: basadas en racha y tasa de completado
- [ ] **Reportes semanales automáticos por email** (para el padre)
- [ ] **Sistema de logros (badges)**: hitos como "30 días seguidos", "100 estrellas"
- [ ] **Modo desafío**: retos especiales semanales con recompensa extra
- [ ] **Hábitos por temporada**: diferentes hábitos en vacaciones/clases

---

## 👨‍👩‍👧 v4.0.0 – Multi-Familia (Mes 6+)

- [ ] **Cuentas de familia**: múltiples padres, múltiples hijos
- [ ] **Roles**: Admin (padre), Usuario (hija), Observador (abuelos)
- [ ] **Modo compartido familiar**: hábitos que gana toda la familia junta
- [ ] **Marketplace de hábitos**: plantillas predefinidas por edad y objetivo
- [ ] **API pública documentada**: integraciones con otras apps (Google Fit, etc.)

---

## 🔒 Principios de diseño

| Principio | Decisión |
|-----------|----------|
| **Sostenibilidad** | Micro-hábitos progresivos, no todo de golpe |
| **Resiliencia** | Escudo semanal, días parciales cuentan |
| **Dopamina** | Inmediata (check), diaria (completar), semanal ($), mensual (reward) |
| **Progresión** | Niveles, rachas, badges para motivar continuidad |
| **Privacidad** | Datos en casa primero (SQLite), nube opcional |
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
