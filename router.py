#!/usr/bin/env python3
"""A small, local-first chat router for Ollama."""

import json
import os
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def load_env_file(path: Path = Path(".env")) -> None:
    """Load simple KEY=value settings without overriding shell variables."""
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("\"'")

        if key:
            os.environ.setdefault(key, value)


def setting(name: str, default: str) -> str:
    return os.environ.get(name, default).strip()


def request_json(method: str, path: str, payload: dict | None = None) -> dict:
    base_url = setting("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
    timeout = int(setting("OLLAMA_TIMEOUT_SECONDS", "300"))
    body = None if payload is None else json.dumps(payload).encode("utf-8")

    request = Request(
        f"{base_url}{path}",
        data=body,
        headers={"Content-Type": "application/json"},
        method=method,
    )

    try:
        with urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Ollama returned HTTP {error.code}: {detail}") from error
    except URLError as error:
        raise RuntimeError(
            "Could not connect to Ollama. Install and start Ollama, then try again."
        ) from error
    except (TimeoutError, ValueError) as error:
        raise RuntimeError(f"Could not complete the Ollama request: {error}") from error


def list_models() -> list[str]:
    result = request_json("GET", "/api/tags")
    return sorted(
        item["name"]
        for item in result.get("models", [])
        if isinstance(item, dict) and item.get("name")
    )


def print_models(models: list[str], selected: str) -> None:
    if not models:
        print("No local models found. Pull one first, for example: ollama pull llama3.2")
        return

    print("Installed models:")
    for model in models:
        marker = " (selected)" if model == selected else ""
        print(f"  - {model}{marker}")


def show_help() -> None:
    print(
        "Commands:\n"
        "  /models        List locally installed models\n"
        "  /use NAME      Switch to an installed model\n"
        "  /clear         Clear this conversation's history\n"
        "  /help          Show commands\n"
        "  /exit          Quit"
    )


def chat(model: str, history: list[dict[str, str]]) -> str:
    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant. Be clear, accurate, and practical.",
        },
        *history,
    ]
    result = request_json(
        "POST",
        "/api/chat",
        {"model": model, "messages": messages, "stream": False},
    )
    message = result.get("message", {})
    content = message.get("content", "")
    if not isinstance(content, str) or not content.strip():
        raise RuntimeError("The model returned an empty response.")
    return content.strip()


def main() -> int:
    load_env_file()
    selected = setting("OLLAMA_MODEL", "llama3.2")

    try:
        models = list_models()
    except (RuntimeError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        print("See README.md for setup instructions.", file=sys.stderr)
        return 1

    if not models:
        print_models(models, selected)
        return 1

    if selected not in models:
        print(f"Configured model '{selected}' is not installed.")
        print_models(models, selected)
        selected = models[0]
        print(f"Using '{selected}' for this session. Use /use NAME to switch.")

    history: list[dict[str, str]] = []
    print(f"ModelSwitch Local — using {selected}. Type /help for commands.")

    while True:
        try:
            text = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            return 0

        if not text:
            continue

        if text == "/exit":
            print("Goodbye.")
            return 0
        if text == "/help":
            show_help()
            continue
        if text == "/models":
            try:
                models = list_models()
                print_models(models, selected)
            except (RuntimeError, ValueError) as error:
                print(f"Error: {error}")
            continue
        if text == "/clear":
            history.clear()
            print("Conversation history cleared.")
            continue
        if text.startswith("/use "):
            requested = text[len("/use "):].strip()
            try:
                models = list_models()
                if requested in models:
                    selected = requested
                    print(f"Switched to {selected}.")
                else:
                    print(f"Model '{requested}' is not installed.")
                    print_models(models, selected)
            except (RuntimeError, ValueError) as error:
                print(f"Error: {error}")
            continue
        if text.startswith("/"):
            print("Unknown command. Type /help to see available commands.")
            continue

        history.append({"role": "user", "content": text})
        try:
            answer = chat(selected, history)
            history.append({"role": "assistant", "content": answer})
            print(f"\n{selected}: {answer}")
        except (RuntimeError, ValueError) as error:
            history.pop()
            print(f"Error: {error}")


if __name__ == "__main__":
    raise SystemExit(main())
