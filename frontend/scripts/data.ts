/**
 * HábitosFam – frontend/scripts/data.ts
 * Frontend constants, messages and theme configurations.
 */

// Progress messages by profile slug
export const PROGRESS_MESSAGES: Record<string, Record<number, string>> = {
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
export const DIAS = ['Dom', 'Lun', 'Mar', 'Miér', 'Jue', 'Vie', 'Sáb'];

// Theme colors for dynamic profiles
export const THEME_COLORS: Record<string, { primary: string; gradient: string }> = {
  alana: { primary: '#c084fc', gradient: 'linear-gradient(135deg, #7c3aed, #c084fc)' },
  sofia: { primary: '#f472b6', gradient: 'linear-gradient(135deg, #ec4899, #f472b6)' },
  default: { primary: '#60a5fa', gradient: 'linear-gradient(135deg, #3b82f6, #60a5fa)' },
};

// Global Settings (Fallback)
export const DEFAULT_SETTINGS = {
  currency: "$",
  app_name: "HábitosFam",
  streak_days: 7,
  streak_bonus_pct: 1.5
};
