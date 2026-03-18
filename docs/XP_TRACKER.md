# 🧬 AI Experience Tracker (XP & Global Memory)

Este documento actúa como el "cerebro a largo plazo" y registro evolutivo de la IA trabajando en HábitosFam. El objetivo no es solo codificar, sino aprender tras cada iteración en el `core-loop` para volverse más rápido, eficiente en el uso de tokens y certero (estilo OpenClaw).

---

## 📊 Nivel de IA Actual
- **Nivel Actual:** 1 (Novato Brillante)
- **XP Total Acumulado:** 50 XP
- **Próximo Nivel (Nivel 2 - Agente Senior):** 100 XP

---

## 💡 Lecciones Aprendidas de Alto Impacto (Reglas Inquebrantables)
*(El Agente consultará esta sección primero antes de alucinar)*

- **Infraestructura de Render**: Especificar `PYTHON_VERSION` y `NODE_VERSION` en `render.yaml` elimina la necesidad de `nvm` y acelera el build en ~2 minutos. Es mejor delegar migraciones al arranque de la app para evitar fallos de conexión en la fase de build.
- **Auto-Preservación del Workflow**: Un agente debe auditar su propio manual de instrucciones (`core-loop.md`) para evitar la degradación del protocolo y la obsolescencia frente a nuevas reglas.

---

## 📜 Historial de Evolución y XP

| Fecha | Feature / Tarea Ejecutada | Modelo Óptimo Detectado | XP Ganado | Token Savings Tip | Key Insight (Lección) |
|-------|---------------------------|------------------------|-----------|------------------|----------------------|
| Inicio | Inicialización de Tracker | N/A | +0 | N/A | Sistema de evolución iniciado. |
| 2026-03-17 | Optimización de Render (v3.3.3) | Gemini 2.0 | +20 | Usar versiones nativas en `render.yaml` | Menos herramientas manuales = builds más robustos y rápidos. |
| 2026-03-17 | Sistema Core Loop Sentinel (v3.3.4) | Gemini 2.0 | +30 | Crear meta-skills de auditoría | La auto-reparación garantiza la longevidad del agente en el proyecto. |

*(Las nuevas entradas se añaden al final del documento siguiendo la plantilla proporcionada en la skill `ai-experience-tracker`)*
