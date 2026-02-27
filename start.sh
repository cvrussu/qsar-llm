#!/bin/bash
# ─── QSAR LLM — Script de inicio ─────────────────────────────────────────────

set -e

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║           QSAR LLM — UranoIA  (v1.0.0-beta)         ║"
echo "║   Evaluación Regulatoria de Agroquímicos con IA      ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""

# 1. Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no encontrado. Instálalo desde python.org"
    exit 1
fi
echo "✓ Python: $(python3 --version)"

# 2. Verificar/crear entorno virtual
if [ ! -d "venv" ]; then
    echo "→ Creando entorno virtual..."
    python3 -m venv venv
fi

# 3. Activar venv
source venv/bin/activate
echo "✓ Entorno virtual activado"

# 4. Instalar dependencias
echo "→ Instalando dependencias..."
pip install -q -r requirements.txt
echo "✓ Dependencias instaladas"

# 5. Verificar .env
if [ ! -f ".env" ]; then
    echo "⚠️  No se encontró .env — copiando desde .env.example"
    cp .env.example .env
    echo "   → Edita .env y agrega tu ANTHROPIC_API_KEY"
fi

# 6. Cargar variables de entorno
export $(grep -v '^#' .env | xargs)

# 7. Verificar API key
if [ -z "$ANTHROPIC_API_KEY" ] || [ "$ANTHROPIC_API_KEY" = "sk-ant-xxxxxxxxxxxxxxxxxxxx" ]; then
    echo "⚠️  ANTHROPIC_API_KEY no configurado."
    echo "   La interfaz funcionará en modo demo (sin LLM real)."
fi

# 8. Iniciar servidor
PORT=${PORT:-5000}
echo ""
echo "🚀 Iniciando servidor en http://localhost:$PORT"
echo "   Presiona Ctrl+C para detener"
echo ""

python3 app.py
