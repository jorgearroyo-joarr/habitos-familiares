# Architecture & Design Justification — HábitosFam

## 🎯 Design Goals
1. **Zero-Latency Feel**: Frontend-heavy logic for immediate feedback.
2. **Infrastructure Agnostic**: Base code works with SQLite, PostgreSQL, or MySQL.
3. **Zero-Privilege Security**: Minimal permissions by default.
4. **Maintainability**: Clear separation of layers (Config → DB → Models → Schemas → CRUD → API).

## 🏗️ Architectural Pattern: Layered Monolith
We use a layered monolith approach instead of microservices to minimize cognitive overhead for a family project while maintaining clean boundaries.

### 1. Frontend: Vanilla JS & CSS
**Decision**: No React/Vue/Svelte. Folder structure organized into `frontend/` (scripts, styles, public).
**Justification**: 
- **Performance**: Near-instant load times with no hydration or heavy JS bundles.
- **Longevity**: Vanilla JS is the most stable "framework". 
- **Complexity**: For a CRUD app with simple state, frameworks add more overhead than they solve.

### 2. Backend: FastAPI (Python)
**Decision**: FastAPI + Pydantic v2.
**Justification**:
- **Speed**: One of the fastest Python frameworks available.
- **Auto-Documentation**: OpenAPI (Swagger) out of the box.
- **Type Safety**: Pydantic ensures data integrity at the API boundary.

### 3. ORM: SQLAlchemy 2.0
**Decision**: DB-Agnostic ORM.
**Justification**:
- Allows the user to start with a local `SQLite` file and scale to `PostgreSQL` (Supabase) just by changing an environment variable.

## 🔐 Security Decisions
- **PIN-based Auth**: SHA-256 hashing. Sufficient for internal family use.
- **Token Generation**: Secret-key based hashes to prevent session hijacking.
- **Scoped Endpoints**: Every route ensures that the profile slug in the URL matches the data being returned.

## 🚀 Scaling Strategy
- **Current**: Single-node SQLite.
- **Future**: Distributed PostgreSQL + Redis for caching (if needed).
