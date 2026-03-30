<!-- Version: 1.1.0 | Updated: 2026-03-30 | Author: AI-assisted -->
# 🚀 Guía de Despliegue - HábitosFam

Este documento detalla cómo poner tu aplicación en internet de forma **completamente gratuita**.

---

## 💎 Opción 1: Render.com + Supabase (Recomendado)

Esta es la opción más estable. Render hospeda el código y Supabase hospeda la base de datos PostgreSQL.

### 🔌 Paso A: Configurar la Base de Datos (Supabase)
1. Entra en [Supabase.com](https://supabase.com) y crea un proyecto gratuito.
2. Ve a **Project Settings** -> **Database**.
3. Busca la sección **Connection String**, selecciona el modo **Pooler** (asegúrate de que esté en port **6543**) y copia la dirección. Se verá algo así:
   `postgresql://postgres.[ID_PROYECTO]:[TU_PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres`
4. **IMPORTANTE**: No uses el puerto 5432 en Render, ya que suele fallar por problemas de IPv6. El puerto 6543 es mucho más estable.

### 🚀 Paso B: Publicar la App (Render)
1. Sube tu código a un repositorio de **GitHub** (puede ser privado).
2. Entra en [Render.com](https://render.com) y crea un nuevo **Web Service**.
3. Conecta tu repositorio de GitHub.
4. Render detectará automáticamente el archivo `render.yaml` en la raíz del proyecto.
   - **IMPORTANTE**: No necesitas configurar el Build ni el Start Command manualmente, el archivo `render.yaml` ya contiene las instrucciones óptimas (incluyendo la compilación del frontend con Node.js y el backend con Python).
5. Ve a la pestaña **Environment** en Render para asegurarte de que las variables secretas estén configuradas (si no usas un archivo `.env` en el Dashboard):
   - `DATABASE_URL`: (Pega la URL de Supabase que copiaste arriba).
   - `ADMIN_PIN`: `1234` (O el PIN que prefieras para entrar al panel admin).
6. Haz clic en **Create Web Service**. Render ejecutará `./build.sh` para preparar todo. ¡Listo! Render te dará una URL (ej: `habitosfam.onrender.com`).

---

## 🎈 Opción 2: Fly.io (SQLite con persistencia)

Si prefieres seguir usando el archivo SQLite local en lugar de una base de datos externa, Fly.io es la mejor opción porque permite "Volúmenes" (discos virtuales que no se borran).

### 🛠️ Pasos:
1. Instala el CLI de Fly: `powershell -Command "iwr https://fly.io/install.ps1 | iex"`
2. Inicia sesión: `fly auth login`
3. Lanza la app: `fly launch`
4. Cuando te pregunte si quieres editar la configuración, di que **SÍ**.
5. Asegúrate de añadir una sección de **[mounts]** en el archivo `fly.toml` para que el archivo `.db` sea persistente:
   ```toml
   [mounts]
     source = "habitos_data"
     destination = "/data"
   ```
6. En tu código o variables de entorno, cambia la ruta de la base de datos a `/data/habitosfam.db`.
7. Despliega: `fly deploy`

---

## ❓ Preguntas Frecuentes

**¿Por qué mi app tarda en cargar en Render?**
Render suspende los servicios gratuitos después de 15 minutos de inactividad. El primer acceso "despierta" al servidor y tarda unos 30 segundos. Los siguientes accesos serán instantáneos.

**¿Es seguro usar Supabase gratis?**
Sí, el plan gratuito es muy generoso (500MB de base de datos) y es más que suficiente para años de registros de una familia.

**¿Cómo actualizo mi app?**
Cada vez que hagas un `git push` a tu repositorio de GitHub, Render detectará los cambios y actualizará la aplicación automáticamente sin que tengas que hacer nada.
