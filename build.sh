#!/usr/bin/env bash
# build.sh - Script unificado para despliegue en Render (Native Environment: Python)

set -e # Salir inmediatamente si un comando falla

echo "🚀 Iniciando proceso de build para HábitosFam en Render..."

# 1. Compilar el Frontend
# Nota: Node.js ya está disponible gracias a NODE_VERSION en render.yaml
echo "💻 Compilando Frontend..."
cd frontend
npm install
npm run build
cd ..

# 2. Instalar dependencias del Backend
echo "🐍 Instalando dependencias de Python..."
pip install --upgrade pip
pip install -r requirements.txt

# 3. Nota sobre Migraciones:
# Las migraciones (alembic upgrade head) se ejecutan automáticamente 
# al iniciar la aplicación en backend/main.py (lifespan).
# Esto garantiza que la DB esté lista antes de servir peticiones.

echo "✅ Build completado exitosamente."
