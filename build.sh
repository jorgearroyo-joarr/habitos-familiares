#!/usr/bin/env bash
# build.sh - Script unificado para despliegue en Render (Native Environment: Python)

set -e # Salir inmediatamente si un comando falla

echo "🚀 Iniciando proceso de build para HábitosFam en Render..."

# 0. Verificar Entorno
echo "🔍 Verificando entornos de runtime..."
python --version
pip --version

if command -v node >/dev/null 2>&1; then
    echo "✅ Node.js detectado: $(node -v)"
else
    echo "❌ Node.js NO detectado. Render Native Python environment might need a different approach or Node is not in PATH."
    # No fallamos aquí para permitir que Render intente usar buildpacks si están configurados, 
    # pero advertimos claramente.
fi

# 1. Compilar el Frontend
echo "💻 Compilando Frontend..."
if [ -d "frontend" ]; then
    cd frontend
    if [ -f "package.json" ]; then
        echo "📦 Instalando dependencias de Node..."
        npm install
        echo "🏗️ Ejecutando build de Vite..."
        npm run build
    else
        echo "⚠️ No se encontró package.json en frontend/. Saltando build de Node."
    fi
    cd ..
else
    echo "⚠️ Directorio 'frontend' no encontrado. Saltando paso de frontend."
fi

# 2. Instalar dependencias del Backend
echo "🐍 Instalando dependencias de Python..."
pip install --upgrade pip
pip install -r requirements.txt

# 3. Nota sobre Migraciones:
# Las migraciones (alembic upgrade head) se ejecutan automáticamente 
# al iniciar la aplicación en backend/main.py (lifespan).

echo "✅ Build completado exitosamente."
