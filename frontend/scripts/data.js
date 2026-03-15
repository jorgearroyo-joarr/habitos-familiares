// ============================================
// HábitosFam – data.js  (v3)
// UI constants only. Habit data loaded from API.
// ============================================

// Progress messages by profile slug
const PROGRESS_MESSAGES = {
  _default: {
    0: '¡Empieza tu día con energía! 🚀',
    1: '¡Buen inicio, sigue así! ⭐',
    2: '¡Ya van 2! ¡Imparable! 🌟',
    3: '¡A mitad del camino! 💪',
    4: '¡Casi ahí! ¡Tú puedes! 🔥',
    5: '¡Solo uno más! 🚀',
    6: '¡¡DÍA PERFECTO!! 🌈✨',
  },
  alana: {
    0: '¡Empieza tu día con energía! 🚀',
    1: '¡Buen inicio, sigue así! ⭐',
    2: '¡Ya van 2! ¡Imparable! 🌟',
    3: '¡A mitad del camino! 💪',
    4: '¡Casi ahí! 2 más y eres HEROÍNA 🦸‍♀️',
    5: '¡Solo uno más! ¡Tú puedes! 🔥',
    6: '¡¡DÍA PERFECTO!! Eres increíble 🌈✨',
  },
  sofia: {
    0: '¡Empieza tu día con propósito! 🎯',
    1: '¡Primer paso dado! El momentum comienza ⚡',
    2: '¡Building momentum! Keep going 🔥',
    3: '¡A mitad! Eres más fuerte que ayer 💪',
    4: '¡4 de 6! Estás en modo CAMPEONA 🏆',
    5: '¡Solo uno más! No te detengas ahora 🚀',
    6: '¡¡PERFECT DAY!! Tú defines el estándar 👑🌸',
  }
};

// Days of week in Spanish
const DIAS = ['Dom', 'Lun', 'Mar', 'Miér', 'Jue', 'Vie', 'Sáb'];

// Theme colors for dynamic profiles
const THEME_COLORS = {
  alana: { primary: '#c084fc', gradient: 'linear-gradient(135deg, #7c3aed, #c084fc)' },
  sofia: { primary: '#f472b6', gradient: 'linear-gradient(135deg, #ec4899, #f472b6)' },
  default: { primary: '#60a5fa', gradient: 'linear-gradient(135deg, #3b82f6, #60a5fa)' },
};
