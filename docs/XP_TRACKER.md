# 🧬 AI Experience Tracker (XP & Global Memory)

Este documento actúa como el "cerebro a largo plazo" y registro evolutivo de la IA trabajando en HábitosFam. El objetivo no es solo codificar, sino aprender tras cada iteración en el `core-loop` para volverse más rápido, eficiente en el uso de tokens y certero (estilo OpenClaw).

---

## 📊 Nivel de IA Actual
- **Nivel Actual:** 2 (Agente Senior)
- **XP Total Acumulado:** 100 XP
- **Próximo Nivel (Nivel 3 - Arquitecto):** 200 XP

---

## 💡 Lecciones Aprendidas de Alto Impacto (Reglas Inquebrantables)
*(El Agente consultará esta sección primero antes de alucinar)*

- **Infraestructura de Render**: Especificar `PYTHON_VERSION` y `NODE_VERSION` en `render.yaml` elimina la necesidad de `nvm` y acelera el build en ~2 minutos. Es mejor delegar migraciones al arranque de la app para evitar fallos de conexión en la fase de build.
- **Auto-Preservación del Workflow**: Un agente debe auditar su propio manual de instrucciones (`core-loop.md`) para evitar la degradación del protocolo y la obsolescencia frente a nuevas reglas.
- **🆕 Migraciones Alembic idempotentes (PostgreSQL)**: La migración `v330_initial` crea el schema COMPLETO (incluyendo columnas que migraciones posteriores añaden). Las migraciones delta NUNCA deben asumir que las columnas no existen — usar `inspector.get_columns()` como guard. El `INSERT INTO app_settings` DEBE incluir columnas `NOT NULL` aunque sean temporales ('changeme' → seed las sobreescribe). Violación = crash loop infinito en Render.
- **🆕 WeekReward tiene `earned_amount`, NO `amount`**: Al referenciar columnas del modelo `WeekReward` en queries, siempre usar `earned_amount`. La columna `amount` no existe y provoca un AttributeError silencioso en endpoints de admin.

---

## 📜 Historial de Evolución y XP

| Fecha | Feature / Tarea Ejecutada | Modelo Óptimo Detectado | XP Ganado | Token Savings Tip | Key Insight (Lección) |
|-------|---------------------------|------------------------|-----------|------------------|----------------------|
| Inicio | Inicialización de Tracker | N/A | +0 | N/A | Sistema de evolución iniciado. |
| 2026-03-17 | Optimización de Render (v3.3.3) | Gemini 2.0 | +20 | Usar versiones nativas en `render.yaml` | Menos herramientas manuales = builds más robustos y rápidos. |
| 2026-03-17 | Sistema Core Loop Sentinel (v3.3.4) | Gemini 2.0 | +30 | Crear meta-skills de auditoría | La auto-reparación garantiza la longevidad del agente en el proyecto. |
| 2026-03-29 | Fix crash loop PostgreSQL (v3.4.1) | Claude Sonnet 4.6 Thinking | +50 | Leer logs de Render antes de buscar el bug en el código — los logs muestran exactamente dónde rompe (ROLLBACK tras query alana = falla en seed = falla en migration). | Migraciones Alembic deben ser idempotentes para PostgreSQL. `v330_initial` crea schema COMPLETO — migraciones delta deben verificar existencia de columnas antes de ADD COLUMN. INSERT en migraciones debe incluir todas las columnas NOT NULL. |

*(Las nuevas entradas se añaden al final del documento siguiendo la plantilla proporcionada en la skill `ai-experience-tracker`)*
- **Falla**: Error 500 en arranque de Render por violación de unicidad en `seed_default_data`.
- **Causa**: El "seed" intentaba insertar hábitos/tiers duplicados en cada reinicio.
- **Lección**: Las funciones de población de datos iniciales (*seeding*) deben ser 100% idempotentes independientemente de si el perfil existe o no.
- **Acción**: Refactorizada lógica de semillas para usar "get_or_create" a nivel de cada registro individual.

🆕 **2026-03-30: Robustez de API & Pydantic**
- **Falla**: Error 500 potencial al serializar modelos ORM con nombres de columnas cambiados (ej: `amount` → `earned_amount`).
- **Lección**: Nunca retornar modelos ORM crudos en la API sin un `response_model` explícito.
- **Acción**: Reforzados los endpoints de `admin.py` con esquemas Pydantic para garantizar una salida tipada y segura.
