"""TTS engine registry. Add an engine: implement TTSEngine, register it here."""
import importlib

REGISTRY = {
    "clova": "tools.tts.clova:ClovaEngine",
    "dryrun": "tools.tts.dryrun:DryRunEngine",
    "google": "tools.tts.google:GoogleEngine",
    "qwen": "tools.tts.qwen:QwenEngine",
}


def engine_class(name: str):
    if name not in REGISTRY:
        raise SystemExit(f"unknown tts engine {name!r}; known: {sorted(REGISTRY)}")
    mod, cls = REGISTRY[name].split(":")
    return getattr(importlib.import_module(mod), cls)


def get_engine(cfg: dict):
    return engine_class(cfg["engine"])(cfg)
