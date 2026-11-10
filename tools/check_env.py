"""Preflight: secrets and tokens needed by the configured pipeline are present.

Prints only key names and paths, never secret values. Dryrun needs nothing.
Exit 0 = ready, 1 = setup needed (run the podcast-setup skill),
2 = tool environment broken (e.g. requirements not installed).

usage: python3 -m tools.check_env
"""
import os
import sys
from pathlib import Path

try:
    from tools.common import ENV_FILE, load_config
except ImportError as e:
    print(f"tool environment broken: {e} (run: pip install -r requirements.txt)")
    sys.exit(2)

TTS_KEYS = {"clova": ["CLOVA_CLIENT_ID", "CLOVA_CLIENT_SECRET"], "google": ["GOOGLE_TTS_API_KEY"]}
DEFAULT_TOKEN = Path.home() / ".config/podcast-studio/youtube-token.json"


def problems(cfg: dict) -> list[str]:
    engine = cfg["tts"]["engine"]
    if engine == "dryrun":
        return []
    found = [f"{k} is empty" for k in TTS_KEYS.get(engine, []) if not os.environ.get(k)]
    secrets = os.environ.get("YOUTUBE_CLIENT_SECRETS")
    if not secrets:
        found.append("YOUTUBE_CLIENT_SECRETS is empty")
    elif not Path(secrets).is_file():
        found.append(f"YOUTUBE_CLIENT_SECRETS file not found: {secrets}")
    token = Path(os.environ.get("YOUTUBE_TOKEN", DEFAULT_TOKEN))
    if not token.is_file():
        found.append(f"YouTube token not found: {token} (run: python3 -m tools.upload_youtube --auth)")
    return found


def main():
    found = problems(load_config())
    if not found:
        print("env OK")
        sys.exit(0)
    print(f"env NOT ready ({ENV_FILE} {'exists' if ENV_FILE.exists() else 'missing'}):")
    for p in found:
        print("  -", p)
    sys.exit(1)


if __name__ == "__main__":
    main()
