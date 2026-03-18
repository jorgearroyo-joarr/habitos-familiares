#!/usr/bin/env bash
# build.sh - Script unificado para despliegue en Render (Native Environment: Python)

set -e # Salir inmediatamente si un comando falla

echo "🚀 Iniciando proceso de build para HábitosFam en Render..."

# 1. Instalar Node.js dinámicamente usando nvm para compilar el frontend
echo "📦 Instalando Node.js..."
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.5/install.sh | bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
nvm install 20
nvm use 20

# 2. Compilar el Frontend
echo "💻 Compilando Frontend..."
cd frontend
npm install
npm run build
cd ..

# 3. Instalar dependencias del Backend
echo "🐍 Instalando dependencias de Python..."
pip install --upgrade pip
pip install -r requirements.txt

# 4. Ejecutar Migraciones de Base de Datos
echo "🗄️ Ejecutando migraciones de base de datos..."
# La variable DATABASE_URL debe estar configurada en el Dashboard de Render, apuntando a Supabase
alembic upgrade head

echo "✅ Build completado exitosamente."
