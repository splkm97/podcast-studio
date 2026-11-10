"""Shared helpers: config, env, episode paths, JSON I/O, logging, gate results."""
import json
import os
import sys
import time
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = ROOT / ".env"


def load_env():
    """Load KEY=VALUE lines from .env into os.environ; already-exported vars win."""
    if not ENV_FILE.exists():
        return
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        value = value.strip().strip("'\"")
        if value:
            os.environ.setdefault(key.strip(), os.path.expanduser(value))


load_env()


def load_config() -> dict:
    with open(ROOT / "podcast.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)


def episode_dir(arg: str) -> Path:
    p = Path(arg)
    if not p.is_absolute():
        p = ROOT / p
    if not p.is_dir():
        sys.exit(f"episode dir not found: {p}")
    return p


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def log(ep: Path, stage: str, msg: str):
    line = f"{time.strftime('%Y-%m-%dT%H:%M:%S')} [{stage}] {msg}"
    print(line)
    (ep / "logs").mkdir(exist_ok=True)
    with open(ep / "logs" / "run.log", "a", encoding="utf-8") as f:
        f.write(line + "\n")


def finish_gate(ep: Path, gate: str, problems: list, extra: dict | None = None):
    """Write gates/<gate>.json and exit 0 (pass) or 1 (fail)."""
    passed = not problems
    write_json(ep / "gates" / f"{gate}.json",
               {"gate": gate, "passed": passed, "problems": problems,
                "checked_at": time.strftime("%Y-%m-%dT%H:%M:%S"), **(extra or {})})
    log(ep, gate, "PASS" if passed else f"FAIL ({len(problems)} problems)")
    for p in problems:
        print("  -", p)
    sys.exit(0 if passed else 1)


def load_glossary(ep: Path | None = None) -> dict:
    """English term -> Hangul from the skill glossaries, then the episode's own
    glossary.md (later files win), so parallel episodes never edit shared files."""
    ref = ROOT / ".claude/skills/tech-term-hangul/references"
    terms = {}
    files = [ref / "glossary.md", ref / "glossary-learned.md"] + ([ep / "glossary.md"] if ep else [])
    for f in files:
        if not f.exists():
            continue
        for line in f.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("- ") and " = " in line:
                en, ko = line[2:].split(" = ", 1)
                terms[en.strip()] = ko.split("#")[0].strip()
    return terms
