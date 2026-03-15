"""
HábitosFam – backend/data_config.py  (v3)
Seed templates for initial DB population.
Called once on first startup to populate profiles, habits, micro-habits, and reward tiers.
"""

import hashlib


def _hash_pin(pin: str) -> str:
    return hashlib.sha256(pin.encode()).hexdigest()


# ── Default PINs ──────────────────────────────────────────────
DEFAULT_ADMIN_PIN = "1234"


# ── Profile templates ─────────────────────────────────────────
PROFILE_TEMPLATES = [
    {
        "slug": "alana",
        "name": "Alana",
        "age": 7,
        "avatar": "🦄",
        "theme": "alana",
        "pin": "1111",
        "weekly_reward_base": 2.0,
        "weekly_reward_full": 4.0,
        "monthly_reward_desc": "Actividad especial elegida por Alana 🎪",
        "monthly_min_pct": 0.75,
    },
    {
        "slug": "sofia",
        "name": "Sofía",
        "age": 16,
        "avatar": "🌸",
        "theme": "sofia",
        "pin": "2222",
        "weekly_reward_base": 5.0,
        "weekly_reward_full": 10.0,
        "monthly_reward_desc": "Actividad especial o cash bonus elegido por Sofía 🎯",
        "monthly_min_pct": 0.75,
    },
]


# ── Habit templates with micro-habits ─────────────────────────

HABIT_TEMPLATES = {
    "alana": [
        {
            "habit_key": "sport",
            "name": "Actividad Física 🏃‍♀️",
            "icon": "⚽",
            "category": "deporte",
            "stars": 1,
            "description": "Mover el cuerpo y ser fuerte",
            "details": "Al menos 20 minutos de movimiento activo",
            "motivation": "¡Los cuerpos fuertes necesitan moverse cada día!",
            "micro_habits": [
                "🏃 20 min de juego activo o deporte",
                "🧘 5 min de estiramiento antes de dormir",
                "🚶 Caminata o andar en bici hoy",
            ],
        },
        {
            "habit_key": "study",
            "name": "Estudio 📚",
            "icon": "✏️",
            "category": "estudio",
            "stars": 1,
            "description": "Aprender algo nuevo hoy",
            "details": "Lectura de 15 min + tarea + repaso",
            "motivation": "¡Cada página leída es un superpoder nuevo!",
            "micro_habits": [
                "📖 Leer 15 minutos (libro o cuentos)",
                "✏️ Completar la tarea del colegio",
                "🔢 Practicar 1 mini-juego de matemáticas",
            ],
        },
        {
            "habit_key": "home",
            "name": "Ayudo en Casa 🏠",
            "icon": "🧹",
            "category": "hogar",
            "stars": 1,
            "description": "Ser parte del equipo familiar",
            "details": "Una tarea del hogar completada con amor",
            "motivation": "¡Cuando todos ayudan, la casa es más feliz!",
            "micro_habits": [
                "🍽️ Poner o recoger la mesa",
                "🧹 Barrer o limpiar una habitación",
                "🧺 Guardar la ropa limpia",
            ],
        },
        {
            "habit_key": "room",
            "name": "Cuarto Ordenado 🌈",
            "icon": "🌸",
            "category": "orden",
            "stars": 1,
            "description": "Mi espacio, mi responsabilidad",
            "details": "Cuarto recogido antes de las 8pm",
            "motivation": "¡Un cuarto ordenado da superpoderes para estudiar!",
            "micro_habits": [
                "🛏️ Hacer la cama al despertar",
                "🧸 Juguetes en su lugar",
                "👕 Ropa sucia en el cesto",
            ],
        },
        {
            "habit_key": "food",
            "name": "Como Sano 🥦",
            "icon": "🥗",
            "category": "nutricion",
            "stars": 1,
            "description": "Comida que me hace fuerte y feliz",
            "details": "Verduras y agua durante el día",
            "motivation": "¡La comida sana te da energía para jugar y crecer!",
            "micro_habits": [
                "🥦 Comer vegetales en el almuerzo o cena",
                "💧 Tomar 4 vasos de agua",
                "🍎 Una fruta como snack (en vez de dulces)",
            ],
        },
        {
            "habit_key": "money",
            "name": "Hábito de Dinero 💰",
            "icon": "🪙",
            "category": "finanzas",
            "stars": 1,
            "description": "Aprender el valor del dinero",
            "details": "Alcancía y decisiones inteligentes",
            "motivation": "¡Quien ahorra desde pequeña, tiene grandes sueños!",
            "micro_habits": [
                "🪙 Guardar una moneda en mi alcancía",
                "🤔 Antes de pedir algo: ¿lo necesito o lo quiero?",
                "📊 Contar cuánto tengo ahorrado esta semana",
            ],
        },
        {
            "habit_key": "tech_good",
            "name": "Tecnología para el Bien 🌐",
            "icon": "💻",
            "category": "tecnologia",
            "stars": 2,
            "description": "Usar la tecnología para crear y ayudar",
            "details": "Aprender, crear y compartir algo positivo",
            "motivation": "¡La tecnología puede hacer el mundo mejor!",
            "micro_habits": [
                "🎨 Crear algo digital (dibujo, historia, juego)",
                "🌍 Investigar un tema que me interese en internet",
                "📱 Compartir algo positivo con mi familia o amigos",
            ],
        },
    ],
    "sofia": [
        {
            "habit_key": "sport",
            "name": "Ejercicio & Deporte 💪",
            "icon": "🏋️‍♀️",
            "category": "deporte",
            "stars": 1,
            "description": "Cuerpo fuerte, mente clara",
            "details": "30+ minutos de actividad física",
            "motivation": "¡Tu cuerpo es tu mejor herramienta!",
            "micro_habits": [
                "🏃‍♀️ 30 min de cardio, pesas o deporte",
                "🧘‍♀️ 10 min de meditación o yoga",
                "💤 Dormir mínimo 8 horas esta noche",
            ],
        },
        {
            "habit_key": "study",
            "name": "Estudio Profundo 🎓",
            "icon": "📚",
            "category": "estudio",
            "stars": 1,
            "description": "Aprender con intención y método",
            "details": "90 min enfocados + repaso sin teléfono",
            "motivation": "¡Cada hora de estudio es una inversión en tu futuro!",
            "micro_habits": [
                "📵 90 min de estudio sin teléfono (modo avión)",
                "📝 Completar todas las tareas del día",
                "🔄 Repasar lo aprendido con resúmenes propios",
            ],
        },
        {
            "habit_key": "home",
            "name": "Colaboro en Casa 🏡",
            "icon": "🫶",
            "category": "hogar",
            "stars": 1,
            "description": "Responsabilidad compartida",
            "details": "Una tarea significativa del hogar",
            "motivation": "¡La colaboración es una habilidad que te abrirá puertas!",
            "micro_habits": [
                "🍳 Cocinar o ayudar en la preparación de una comida",
                "🧹 Limpiar o aspirar una zona de la casa",
                "🛒 Apoyar con lista de compras o mandados",
            ],
        },
        {
            "habit_key": "room",
            "name": "Espacio Organizado 🗂️",
            "icon": "✨",
            "category": "orden",
            "stars": 1,
            "description": "Orden externo = orden mental",
            "details": "Cuarto y escritorio organizados",
            "motivation": "¡El orden es el primer hábito de las personas exitosas!",
            "micro_habits": [
                "🛏️ Cama hecha cada mañana",
                "📂 Escritorio despejado y organizado",
                "📱 Apps y archivos digitales en orden (1 vez/semana)",
            ],
        },
        {
            "habit_key": "food",
            "name": "Nutrición Inteligente 🥑",
            "icon": "🥣",
            "category": "nutricion",
            "stars": 1,
            "description": "Combustible para rendir al máximo",
            "details": "Comidas balanceadas + hidratación",
            "motivation": "¡Come para rendir, no solo por placer!",
            "micro_habits": [
                "🥑 Incluir proteína y vegetales en comidas principales",
                "💧 Beber 6-8 vasos de agua",
                "🚫 Sin snacks ultraprocesados hoy",
            ],
        },
        {
            "habit_key": "money",
            "name": "Finanzas Personales 📈",
            "icon": "💹",
            "category": "finanzas",
            "stars": 1,
            "description": "Construir inteligencia financiera",
            "details": "Ahorro, registro y aprendizaje financiero",
            "motivation": "¡La independencia financiera empieza con tus hábitos de HOY!",
            "micro_habits": [
                "💰 Registrar un ingreso o gasto del día",
                "📚 Leer/escuchar 10 min sobre finanzas o emprendimiento",
                "🎯 Revisar o actualizar mi meta de ahorro personal",
            ],
        },
        {
            "habit_key": "tech_good",
            "name": "Tecnología para el Bien 🌐",
            "icon": "🚀",
            "category": "tecnologia",
            "stars": 2,
            "description": "Usar la tecnología como herramienta para el bien",
            "details": "Crear, aprender y aportar con tecnología",
            "motivation": "¡La tecnología es poderosa: úsala para hacer el bien!",
            "micro_habits": [
                "💻 Programar o practicar código 20 min",
                "🌍 Investigar y compartir una noticia positiva sobre tecnología",
                "🤝 Usar la tecnología para ayudar a alguien (enseñar, crear para otros)",
            ],
        },
    ],
}


# ── Default reward tiers ──────────────────────────────────────

DEFAULT_WEEKLY_TIERS = [
    {
        "min_pct": 0.90,
        "multiplier": 2.0,
        "label": "ÉLITE 👑",
        "emoji": "👑",
        "sort_order": 0,
    },
    {
        "min_pct": 0.75,
        "multiplier": 1.5,
        "label": "Increíble 🌟",
        "emoji": "🌟",
        "sort_order": 1,
    },
    {
        "min_pct": 0.60,
        "multiplier": 1.0,
        "label": "Bien 💪",
        "emoji": "💪",
        "sort_order": 2,
    },
    {
        "min_pct": 0.40,
        "multiplier": 0.5,
        "label": "Regular 🌱",
        "emoji": "🌱",
        "sort_order": 3,
    },
    {
        "min_pct": 0.00,
        "multiplier": 0.0,
        "label": "Seguir 💙",
        "emoji": "💙",
        "sort_order": 4,
    },
]
