#!/usr/bin/env bash
# TRACE AI  Startup Script
# Checks prerequisites, pulls models, and starts both backends.
# Usage: bash scripts/start.sh

set -e

BOLD="\033[1m"
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
RED="\033[0;31m"
CYAN="\033[0;36m"
RESET="\033[0m"

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REQUIREMENTS="$PROJECT_ROOT/Trace-app/requirements.txt"
FASTAPI_MODULE="backend.main:app"
STREAMLIT_ENTRY="$PROJECT_ROOT/ui.py"
FASTAPI_PORT=8000
STREAMLIT_PORT=8501

echo -e "${BOLD}${CYAN}"
echo "============================================"
echo "   TRACE AI  Startup Script"
echo "   Transparent Repair Automation"
echo "   with Compliance Engine"
echo "============================================"
echo -e "${RESET}"

# ── 1. Check Python ────────────────────────────────────────────────────────
echo -e "${BOLD}[1/5] Checking Python...${RESET}"
if command -v python3 &>/dev/null; then
    PY="python3"
elif command -v python &>/dev/null; then
    PY="python"
else
    echo -e "${RED}Python is not installed. Please install Python 3.10+.${RESET}"
    exit 1
fi
echo -e "  ${GREEN}Found: $($PY --version)${RESET}"

# ── 2. Install dependencies ───────────────────────────────────────────────
echo -e "${BOLD}[2/5] Installing Python dependencies...${RESET}"
if [ -f "$REQUIREMENTS" ]; then
    $PY -m pip install -r "$REQUIREMENTS" --quiet 2>&1 | tail -1
    echo -e "  ${GREEN}Dependencies installed.${RESET}"
else
    echo -e "  ${YELLOW}requirements.txt not found at $REQUIREMENTS. Skipping.${RESET}"
fi

# ── 3. Check Ollama ──────────────────────────────────────────────────────
echo -e "${BOLD}[3/5] Checking Ollama...${RESET}"
if ! command -v ollama &>/dev/null; then
    echo -e "  ${RED}Ollama is not installed.${RESET}"
    echo -e "  Install it from: ${CYAN}https://ollama.com/download${RESET}"
    echo -e "  ${YELLOW}The Streamlit frontend will still work with mock data,"
    echo -e "  but the FastAPI triage endpoint needs a running LLM.${RESET}"
else
    echo -e "  ${GREEN}Ollama found: $(ollama --version 2>/dev/null || echo 'installed')${RESET}"

    # Check if Ollama server is running
    if curl -s http://localhost:11434/api/tags &>/dev/null; then
        echo -e "  ${GREEN}Ollama server is running.${RESET}"
    else
        echo -e "  ${YELLOW}Ollama server is not running. Starting it...${RESET}"
        ollama serve &>/dev/null &
        sleep 2
        if curl -s http://localhost:11434/api/tags &>/dev/null; then
            echo -e "  ${GREEN}Ollama server started.${RESET}"
        else
            echo -e "  ${RED}Could not start Ollama. Please start it manually: ollama serve${RESET}"
        fi
    fi

    # Pull required models if not already present
    echo -e "${BOLD}[3b] Checking required models...${RESET}"
    for MODEL in llama3.1 mistral; do
        if ollama list 2>/dev/null | grep -q "$MODEL"; then
            echo -e "  ${GREEN}$MODEL is already available.${RESET}"
        else
            echo -e "  ${YELLOW}Pulling $MODEL (this may take a few minutes)...${RESET}"
            ollama pull "$MODEL" || echo -e "  ${RED}Failed to pull $MODEL. You can pull it manually: ollama pull $MODEL${RESET}"
        fi
    done
fi

# ── 4. Create data directory if needed ────────────────────────────────────
echo -e "${BOLD}[4/5] Ensuring data directory exists...${RESET}"
mkdir -p "$PROJECT_ROOT/data"
echo -e "  ${GREEN}data/ directory ready.${RESET}"

# ── 5. Start services ────────────────────────────────────────────────────
echo -e "${BOLD}[5/5] Starting TRACE AI services...${RESET}"
echo ""

# Set API key if not already set
if [ -z "$TRACE_API_KEY" ]; then
    if [ -f "$PROJECT_ROOT/.env" ]; then
        export $(grep -v '^#' "$PROJECT_ROOT/.env" | xargs)
        echo -e "  ${GREEN}Loaded API key from .env file.${RESET}"
    else
        export TRACE_API_KEY="trace-dev-key-$(date +%s)"
        echo -e "  ${YELLOW}No .env file found. Using auto-generated API key.${RESET}"
        echo -e "  ${YELLOW}For production, copy .env.example to .env and set a real key.${RESET}"
    fi
fi

# Start FastAPI in the background
echo -e "  ${CYAN}Starting FastAPI backend on port $FASTAPI_PORT...${RESET}"
cd "$PROJECT_ROOT"
$PY -m uvicorn $FASTAPI_MODULE --host 0.0.0.0 --port $FASTAPI_PORT --reload &
FASTAPI_PID=$!
sleep 2

# Start Streamlit
echo -e "  ${CYAN}Starting Streamlit frontend on port $STREAMLIT_PORT...${RESET}"
$PY -m streamlit run "$STREAMLIT_ENTRY" --server.port $STREAMLIT_PORT &
STREAMLIT_PID=$!
sleep 3

echo ""
echo -e "${BOLD}${GREEN}============================================${RESET}"
echo -e "${BOLD}${GREEN}   TRACE AI is running!${RESET}"
echo -e "${GREEN}============================================${RESET}"
echo ""
echo -e "  ${CYAN}Streamlit UI:${RESET}    http://localhost:$STREAMLIT_PORT"
echo -e "  ${CYAN}FastAPI docs:${RESET}    http://localhost:$FASTAPI_PORT/docs"
echo -e "  ${CYAN}Health check:${RESET}    http://localhost:$FASTAPI_PORT/"
echo ""
echo -e "  Press ${BOLD}Ctrl+C${RESET} to stop all services."
echo ""

# Trap Ctrl+C to clean up both processes
cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down TRACE AI...${RESET}"
    kill $FASTAPI_PID 2>/dev/null
    kill $STREAMLIT_PID 2>/dev/null
    echo -e "${GREEN}All services stopped.${RESET}"
    exit 0
}
trap cleanup SIGINT SIGTERM

# Wait for either process to exit
wait
