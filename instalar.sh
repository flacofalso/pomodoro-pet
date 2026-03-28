#!/bin/bash
# ============================================================
#  Pomodoro Pet — Instalador para macOS
#  Ejecutar con: bash instalar.sh
# ============================================================

set -e

YELLOW='\033[1;33m'
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo ""
echo "🐾  Pomodoro Pet — Instalador"
echo "================================"
echo ""

# 1. Verificar Python 3
if ! command -v python3 &>/dev/null; then
    echo -e "${RED}✗ Python 3 no está instalado.${NC}"
    echo "  Descárgalo en: https://www.python.org/downloads/"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo -e "${GREEN}✓ Python $PYTHON_VERSION encontrado${NC}"

# 2. Crear entorno virtual
if [ ! -d ".venv" ]; then
    echo "→ Creando entorno virtual..."
    python3 -m venv .venv
fi
echo -e "${GREEN}✓ Entorno virtual listo${NC}"

# 3. Activar venv e instalar dependencias
source .venv/bin/activate

echo "→ Instalando dependencias (puede tardar un par de minutos)..."
pip install --upgrade pip -q

# PyQt6 compatible con macOS 12+
pip install "PyQt6==6.4.2" "PyQt6-Qt6==6.4.2" "PyQt6-sip" -q 2>/dev/null || \
pip install "PyQt6" -q

pip install pynput --no-deps -q
pip install opencv-python Pillow -q

echo -e "${GREEN}✓ Dependencias instaladas${NC}"

# 4. Crear script de inicio
cat > iniciar.sh << 'LAUNCHER'
#!/bin/bash
cd "$(dirname "$0")"
source .venv/bin/activate
python3 main.py
LAUNCHER
chmod +x iniciar.sh

# 5. Crear app lanzador .command (doble clic en Finder)
cat > "Pomodoro Pet.command" << 'COMMAND'
#!/bin/bash
cd "$(dirname "$0")"
source .venv/bin/activate
python3 main.py
COMMAND
chmod +x "Pomodoro Pet.command"

echo -e "${GREEN}✓ Lanzador creado${NC}"
echo ""
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}  ¡Instalación completada! 🎉${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo "Para abrir la app:"
echo "  • Doble clic en 'Pomodoro Pet.command'"
echo "  • O desde terminal: bash iniciar.sh"
echo ""
echo -e "${YELLOW}⚠️  Primera vez en macOS:${NC}"
echo "  Si macOS bloquea la app, ve a:"
echo "  Preferencias del Sistema → Privacidad y Seguridad"
echo "  → haz clic en 'Abrir de todos modos'"
echo ""
echo "  Para detección de teclado/mouse, también necesitas:"
echo "  Privacidad y Seguridad → Accesibilidad → agregar Terminal"
echo ""
