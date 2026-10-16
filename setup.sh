#!/usr/bin/env bash
set -eu

cd "$(dirname "$0")"

if ! command -v python3 >/dev/null 2>&1; then
    echo "Python 3 is required. Install Python 3.10 or newer and rerun this script."
    exit 1
fi

python3 -m venv .venv
echo "Created Python virtual environment: .venv"

if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env from .env.example"
fi

if ! command -v ollama >/dev/null 2>&1; then
    echo "Ollama is not installed or is not on PATH."
    echo "Install Ollama, start it, then run: ollama pull llama3.2"
    exit 0
fi

if ollama list >/dev/null 2>&1; then
    model="${OLLAMA_MODEL:-llama3.2}"
    echo "Pulling default model: ${model}"
    ollama pull "${model}"
else
    echo "Ollama is installed but its local service is not responding."
    echo "Start Ollama, then run: ollama pull llama3.2"
fi

echo "Setup complete. Start the app with: .venv/bin/python router.py"
