"""STT engine registry, mirrors tools.tts."""
import importlib

REGISTRY = {"faster-whisper": "tools.stt.faster_whisper_engine:FasterWhisperEngine"}


def get_engine(cfg: dict):
    name = cfg["engine"]
    if name not in REGISTRY:
        raise SystemExit(f"unknown stt engine {name!r}; known: {sorted(REGISTRY)}")
    mod, cls = REGISTRY[name].split(":")
    return getattr(importlib.import_module(mod), cls)(cfg)
