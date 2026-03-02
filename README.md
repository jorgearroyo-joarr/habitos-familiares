# 🏠✨ HábitosFam

> **Pequeños pasos, grandes logros.** | **Small steps, great achievements.**

HábitosFam is a gamified habit tracking system designed to help families (specifically children and teenagers) build resilience through micro-habits and positive reinforcement loops.

[Español](#español) | [English](#english)

---

<a name="español"></a>
## 🇪🇸 Español

### Características Principales
- **Perfiles Dinámicos**: Crea perfiles ilimitados para cada miembro de la familia.
- **Micro-hábitos**: Divide tareas grandes en pasos pequeños (Dopamina inmediata).
- **Gamificación**: Efectos visuales de destellos, sonidos premium y lluvia de confetti.
- **Sistema de Recompensas**: Configura niveles (Bronce, Plata, Oro) y pagos automáticos.
- **Panel Administrativo**: Control total sobre perfiles, hábitos, ajustes y datos.
- **Privacidad**: Tus datos se quedan contigo (SQLite) o en tu propia nube (Supabase).

### Inicio Rápido
1. Clona el repositorio.
2. Instala dependencias: `pip install -r requirements.txt`
3. Inicia el servidor: `python -m uvicorn backend.main:app --reload --port 8765`
4. Abre la app en: `http://localhost:8765`
5. Panel Admin (PIN: `1234`): `http://localhost:8765/admin`

---

<a name="english"></a>
## 🇺🇸 English

### Key Features
- **Dynamic Profiles**: Unlimited profiles for all family members.
- **Micro-habits**: Break down large tasks into small, achievable steps.
- **Gamification**: Visual sparkles, premium audio feedback, and confetti bursts.
- **Reward System**: Set custom tiers (Bronze, Silver, Gold) and automated payouts.
- **Admin Panel**: Full control over profiles, habits, settings, and data logs.
- **Privacy First**: Data stays local (SQLite) or in your private cloud (Supabase).

### Quick Start
1. Clone the repository.
2. Install dependencies: `pip install -r requirements.txt`
3. Run the server: `python -m uvicorn backend.main:app --reload --port 8765`
4. Access the app: `http://localhost:8765`
5. Admin Panel (PIN: `1234`): `http://localhost:8765/admin`

---

## 🚀 Despliegue / Deployment
Para publicar este proyecto de forma gratuita, consulta nuestra guía detallada:
**[Guía de Despliegue (Render, Supabase, Fly.io)](./docs/DEPLOYMENT.md)**

## 🛠️ Tech Stack
- **Backend:** FastAPI (Python 3.14+)
- **Database:** SQLAlchemy (SQLite / PostgreSQL / MySQL)
- **Frontend:** Vanilla HTML5, CSS3 (Glassmorphism), Modern JavaScript
- **Deployment:** Render, Supabase, Fly.io

## 📄 License
MIT License - created with ❤️ for the Arroyo Family and families everywhere.
