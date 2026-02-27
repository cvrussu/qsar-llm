#!/bin/bash

# QSAR LLM Quick Start Script
# Automatically sets up and runs QSAR LLM with proper environment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}QSAR LLM — UranoIA${NC}"
echo -e "${BLUE}Quick Start Setup${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Check Python version
echo -e "${YELLOW}1. Checking Python installation...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 not found!${NC}"
    echo "Install Python 3.9+ from https://www.python.org/downloads/"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo -e "${GREEN}✓ Python ${PYTHON_VERSION} found${NC}\n"

# Check if venv exists
echo -e "${YELLOW}2. Setting up virtual environment...${NC}"
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi
echo -e "${GREEN}✓ Virtual environment ready${NC}\n"

# Activate venv
echo -e "${YELLOW}3. Activating virtual environment...${NC}"
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}\n"

# Install dependencies
echo -e "${YELLOW}4. Installing dependencies...${NC}"
pip install -q -r requirements.txt 2>/dev/null || {
    echo "Installing with verbose output..."
    pip install -r requirements.txt
}
echo -e "${GREEN}✓ Dependencies installed${NC}\n"

# Check .env file
echo -e "${YELLOW}5. Checking configuration...${NC}"
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env file not found${NC}"
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${YELLOW}Created .env from template${NC}"
        echo -e "${YELLOW}⚠️  IMPORTANT: Edit .env and add your GEMINI_API_KEY${NC}"
        echo -e "${YELLOW}   Get one free from: https://aistudio.google.com/app/apikey${NC}\n"
    fi
else
    # Check if GEMINI_API_KEY is set
    if grep -q "GEMINI_API_KEY=AIza" .env; then
        echo -e "${GREEN}✓ GEMINI_API_KEY configured${NC}\n"
    else
        echo -e "${YELLOW}⚠️  GEMINI_API_KEY not configured in .env${NC}"
        echo -e "${YELLOW}   Get one free from: https://aistudio.google.com/app/apikey${NC}\n"
    fi
fi

# Check QSAR Toolbox connectivity
echo -e "${YELLOW}6. Checking QSAR Toolbox WebAPI...${NC}"
TOOLBOX_URL=$(grep "TOOLBOX_URL=" .env | cut -d'=' -f2)
if [ -z "$TOOLBOX_URL" ]; then
    TOOLBOX_URL="http://localhost:3000"
fi

if curl -s "$TOOLBOX_URL/api/v1/version" &>/dev/null; then
    echo -e "${GREEN}✓ QSAR Toolbox available at $TOOLBOX_URL${NC}\n"
else
    echo -e "${YELLOW}⚠️  QSAR Toolbox not found at $TOOLBOX_URL${NC}"
    echo -e "${YELLOW}   QSAR LLM will work in demo mode (PubChem + Gemini AI)${NC}"
    echo -e "${YELLOW}   To enable full features:${NC}"
    echo -e "${YELLOW}   1. Install QSAR Toolbox v4.8${NC}"
    echo -e "${YELLOW}   2. Open QSAR Toolbox → Tools → REST API Server → START${NC}"
    echo -e "${YELLOW}   3. See QSAR_TOOLBOX_SETUP.md for details${NC}\n"
fi

# Display configuration summary
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Configuration Summary${NC}"
echo -e "${BLUE}========================================${NC}\n"

PORT=$(grep "^PORT=" .env | cut -d'=' -f2 || echo "5000")
GEMINI_KEY=$(grep "GEMINI_API_KEY=" .env | cut -d'=' -f2)
DEBUG=$(grep "^DEBUG=" .env | cut -d'=' -f2 || echo "false")

echo "Backend Server:"
echo "  URL: http://localhost:${PORT}"
echo "  Debug: ${DEBUG}"
echo ""
echo "Gemini API:"
if [ -z "$GEMINI_KEY" ]; then
    echo -e "  ${RED}❌ Not configured${NC}"
else
    echo "  ✓ Configured ($(echo $GEMINI_KEY | cut -c1-10)...)"
fi
echo ""
echo "QSAR Toolbox:"
if curl -s "$TOOLBOX_URL/api/v1/version" &>/dev/null; then
    TOOLBOX_VERSION=$(curl -s "$TOOLBOX_URL/api/v1/version" | grep -o '"version":"[^"]*' | cut -d'"' -f4 || echo "4.8")
    echo "  ✓ Available at $TOOLBOX_URL (v${TOOLBOX_VERSION})"
else
    echo "  ⚠️  Not available (demo mode)"
fi

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Starting QSAR LLM Backend${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Start the server
export FLASK_APP=app.py
python app.py

