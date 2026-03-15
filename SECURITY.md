<!-- Version: 1.0.0 | Updated: 2026-03-15 | Author: AI-assisted -->

# SECURITY.md — HábitosFam

> **Zero-Privilege by Design** — Política de seguridad basada en OWASP + NIST Zero Trust.  
> *"Todo usuario, proceso y agente parte de cero privilegios y recibe solo lo mínimo necesario."*

---

## 🎯 Scope & Threat Model

**HábitosFam es una aplicación familiar privada:**

| Factor | Descripción |
|--------|-------------|
| **Usuarios** | Familia hogareña (<10 personas) + 1 administrador |
| **Datos sensibles** | Ninguno de categoría alta. Solo hábitos diarios de menores. |
| **Superficie de ataque** | Red local o hosting privado (Render/Fly.io) |
| **Nivel de riesgo** | **BAJO** — No hay datos financieros, médicos ni PII crítica |
| **Principal amenaza** | Acceso no autorizado al panel admin (cambiar recompensas) |

---

## 🔐 Zero-Privilege by Design

### Principio base (OWASP Proactive Control C3 + NIST SP 800-207)

> Cada capa del sistema comienza con **cero permisos**.  
> Los permisos se otorgan de forma explícita, mínima y revocable.

### Mapa de privilegios por capa

| Capa | Privilegio otorgado | Mecanismo de control | Estado |
|------|---------------------|---------------------|--------|
| **Frontend — usuario** | Leer/escribir solo su propio perfil (por slug) | Endpoints URL-scoped `/api/profiles/{slug}` | ✅ Implementado |
| **Frontend — admin** | CRUD completo solo tras validar PIN | Header `X-Admin-Pin` en cada request | ✅ Implementado |
| **API pública** | Solo lectura de perfiles activos, sin cross-profile | FastAPI route constraints | ✅ Implementado |
| **API admin** | CRUD completo solo tras `verify_admin_pin()` | `crud.verify_admin_pin()` dependency | ✅ Implementado |
| **DB session** | Una sesión por HTTP request, cerrada al finalizar | `Depends(get_db)` + `finally: db.close()` | ✅ Implementado |
| **Variables .env** | Solo `config.py` puede leer valores del entorno | Pydantic Settings, nunca `os.environ` directo | ✅ Implementado |
| **Agente AI** | No puede bypassar auth ni escalar privilegios | Este documento + AGENTS.md | ✅ Documentado |

---

## ⚠️ Known Limitations (Low Risk)

| Limitación | Riesgo | Estado |
|-----------|--------|--------|
| PIN hasheado con SHA-256 (sin salt) | Bajo — PIN corto, sin exposición de datos críticos | ⚠️ Documentado. Migrar a `bcrypt` en v2.2.0 |
| `secret_key` en `config.py` no usada actualmente | Ninguno — no está en uso en lógica de negocio | ⚠️ Preparada para JWT futuro |
| SQLite sin cifrado en disco | Muy bajo — Archivo local en dispositivo familiar | ⚠️ Aceptable para uso doméstico |
| No hay rate limiting en endpoints | Bajo — Sin exposición pública directa | 📝 En ROADMAP |

---

## 🔒 Security Rules for AI Agents

Los agentes (Antigravity, Gemini CLI, Copilot, Cursor, etc.) que trabajen en este proyecto **deben seguir estas reglas sin excepción**:

1. **Nunca añadir bypass** a `verify_admin_pin()` — ni en rutas de test, ni temporalmente.
2. **Nunca leer `.env`** directamente en código — solo `config.py` puede hacerlo.
3. **Nunca crear rutas** que retornen datos de un perfil diferente al del URL.
4. **Nunca generar** código con `os.system()`, `eval()`, `exec()` o inyección de shell.
5. **Nunca dropar tablas** sin confirmación explícita del usuario humano.
6. **Reportar, no corregir silenciosamente** — si el agente encuentra código con implicaciones de seguridad, debe notificar al usuario antes de cambiar nada.

---

## 🔎 Security Checklist (OWASP Top 10 aplicado)

| OWASP Risk | HábitosFam | Estado |
|-----------|-----------|--------|
| **A01 Broken Access Control** | Endpoints separados por perfil + PIN admin | ✅ Mitigado |
| **A02 Cryptographic Failures** | SHA-256 sin salt para PIN (datos no críticos) | ⚠️ Aceptado (bajo riesgo) |
| **A03 Injection** | SQLAlchemy ORM — sin SQL crudo | ✅ Mitigado |
| **A04 Insecure Design** | Zero-privilege by design, documentado | ✅ Mitigado |
| **A05 Security Misconfiguration** | CORS whitelist, modo debug en `.env` | ✅ Mitigado |
| **A06 Vulnerable Components** | `requirements.txt` con versiones fijadas | ⚠️ Revisar periódicamente |
| **A07 Auth Failures** | PIN + hash; sin intentos limitados | ⚠️ Rate limiting en ROADMAP |
| **A08 Software Integrity** | Skills auditadas antes de usar | ✅ Proceso documentado |
| **A09 Logging Failures** | Sin logging estructurado aún | 📝 En ROADMAP |
| **A10 Server-Side Request Forgery** | Sin llamadas a URLs externas desde backend | ✅ N/A |

---

## 📣 Reporting a Vulnerability

Este es un proyecto familiar privado. Si encuentras un problema de seguridad:

1. **No abrir un issue público** en el repo.
2. Contactar directamente al administrador del proyecto.
3. Describir: qué encontraste, cómo reproducirlo y el impacto estimado.

---

## 📋 Change Log

| Version | Date | Change |
|---------|------|--------|
| 1.0.0 | 2026-03-15 | Creación inicial del SECURITY.md con Zero-Privilege model + OWASP checklist |
