"""Gate: script.json is structurally valid and TTS-safe.

Checks schema, speakers, per-segment TTS limits, leftover Latin letters or
symbols CLOVA skips, unsourced claims, and estimated length vs max_minutes.

usage: python3 -m tools.lint_script episodes/<id>
"""
import re
import sys

from tools.common import episode_dir, finish_gate, load_config, read_json
from tools.tts import engine_class

LATIN = re.compile(r"[A-Za-z]")
# CLOVA does not voice symbols or text inside brackets
BAD_SYMBOLS = re.compile(r"[()\[\]{}<>/\\|_*#@&%^~`=+]")
DECIMAL = re.compile(r"\d+\.\d+")
SUBTITLE_SOFT_MAX = 300


def main():
    ep = episode_dir(sys.argv[1])
    cfg = load_config()
    script = read_json(ep / "script.json")
    source_ids = {s["id"] for s in read_json(ep / "sources.json")}
    voices = set(cfg["tts"]["voices"])
    tts_max = engine_class(cfg["tts"]["engine"]).max_chars
    problems, warnings = [], []

    for key in ("title", "description"):
        if not script.get("episode", {}).get(key):
            problems.append(f"episode.{key} missing")

    segs = script.get("segments", [])
    if not segs:
        problems.append("no segments")
    seen = set()
    total_chars = 0
    for s in segs:
        sid = s.get("id", "?")
        if sid in seen:
            problems.append(f"{sid}: duplicate id")
        seen.add(sid)
        if s.get("speaker") not in voices:
            problems.append(f"{sid}: unknown speaker {s.get('speaker')!r}")
        src, tts = s.get("src", ""), s.get("tts", "")
        if not src or not tts:
            problems.append(f"{sid}: src/tts empty")
            continue
        total_chars += len(tts)
        if len(tts) > tts_max:
            problems.append(f"{sid}: tts {len(tts)} chars > {tts_max}")
        if len(src) > SUBTITLE_SOFT_MAX:
            warnings.append(f"{sid}: long segment ({len(src)} chars), consider splitting")
        if LATIN.search(tts):
            problems.append(f"{sid}: Latin letters left in tts: {LATIN.findall(tts)[:5]}")
        if BAD_SYMBOLS.search(tts):
            problems.append(f"{sid}: symbol not voiced by TTS: {sorted(set(BAD_SYMBOLS.findall(tts)))}")
        if DECIMAL.search(tts):
            problems.append(f"{sid}: decimal/version number not spelled out: {DECIMAL.findall(tts)}")
        if s.get("claim"):
            refs = s.get("sources", [])
            if not refs:
                problems.append(f"{sid}: claim without sources")
            for r in refs:
                if r not in source_ids:
                    problems.append(f"{sid}: unknown source {r}")

    est_min = total_chars / cfg["chars_per_minute"]
    if est_min > cfg["max_minutes"]:
        problems.append(f"estimated {est_min:.1f} min > max_minutes {cfg['max_minutes']}")
    for w in warnings:
        print("  warn:", w)
    finish_gate(ep, "script_lint", problems,
                {"segments": len(segs), "estimated_minutes": round(est_min, 1), "warnings": warnings})


if __name__ == "__main__":
    main()
