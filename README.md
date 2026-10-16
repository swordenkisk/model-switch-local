# ModelSwitch Local

A free, local-first command-line chat app for switching between models installed
with Ollama. No Claude subscription, cloud account, or paid API key is required.

## What it does

- Chats with models running locally through Ollama.
- Switches between installed models without restarting the app.
- Keeps conversation history during the session.
- Lists installed models and clears the current conversation.
- Uses only Python's standard library.

## Requirements

- Python 3.10 or newer
- Ollama installed and running
- At least one Ollama model downloaded

The application is free. Model downloads require internet access, and local
inference uses your computer's memory, processor, and electricity. Model
availability and hardware requirements vary.

## Setup

1. Install Ollama for your operating system and start its local service.
2. Download a model:

   ```bash
   ollama pull llama3.2

Make the setup script executable and run it:
bash


chmod +x setup.sh
./setup.sh
Start the app:
bash


.venv/bin/python router.py
If you prefer not to use the setup script, create the environment manually:

bash


python3 -m venv .venv
cp .env.example .env
.venv/bin/python router.py
Commands
Command	Action
/models	List installed models
/use MODEL_NAME	Switch to an installed model
/clear	Clear conversation history
/help	Show available commands
/exit	Quit
Use the exact model name shown by /models, such as llama3.2:latest.

Configuration
Edit .env to change the Ollama connection or default model:

dotenv


OLLAMA\_BASE\_URL=http://localhost:11434
OLLAMA\_MODEL=llama3.2
OLLAMA\_TIMEOUT\_SECONDS=300
The app reads these settings from .env. Existing shell environment variables
take precedence. Do not put API keys in this file; this project does not use
remote model APIs.
