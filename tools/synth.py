"""Synthesize segments, join them with pauses, write timings and episode.mp3.

Segments whose tts text is unchanged since the last run are reused, so a
retry after an STT failure only re-synthesizes what was edited.

usage: python3 -m tools.synth episodes/<id> [--only s001,s007] [--force]
"""
import argparse
import hashlib
import os
import subprocess
import wave

from tools.common import episode_dir, load_config, log, read_json, write_json
from tools.tts import get_engine


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("episode")
    ap.add_argument("--only", default="")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()

    ep = episode_dir(a.episode)
    cfg = load_config()
    tcfg = cfg["tts"]
    engine = get_engine(tcfg)
    segs = read_json(ep / "script.json")["segments"]
    seg_dir = ep / "audio" / "segments"
    seg_dir.mkdir(parents=True, exist_ok=True)
    manifest_p = seg_dir / "manifest.json"
    manifest = read_json(manifest_p) if manifest_p.exists() else {}
    only = set(filter(None, a.only.split(",")))

    for s in segs:
        voice = tcfg["voices"][s["speaker"]]
        key = hashlib.sha256(f"{tcfg['engine']}|{voice}|{s['tts']}".encode()).hexdigest()
        out = seg_dir / f"{s['id']}.wav"
        fresh = out.exists() and manifest.get(s["id"]) == key
        if fresh and not a.force and s["id"] not in only:
            continue
        engine.synth(s["tts"], voice, out)
        manifest[s["id"]] = key
        write_json(manifest_p, manifest)
        log(ep, "tts", f"synth {s['id']} ({len(s['tts'])} chars)")

    # join sample-exactly; timings feed subtitles
    params, timings, cursor = None, [], 0
    pause_frames = None
    with wave.open(str(ep / "audio" / "episode.wav"), "wb") as outw:
        for i, s in enumerate(segs):
            with wave.open(str(seg_dir / f"{s['id']}.wav"), "rb") as w:
                p = (w.getnchannels(), w.getsampwidth(), w.getframerate())
                if params is None:
                    params = p
                    outw.setnchannels(p[0]); outw.setsampwidth(p[1]); outw.setframerate(p[2])
                    pause_frames = b"\x00" * (p[0] * p[1] * int(p[2] * tcfg["pause_ms"] / 1000))
                elif p != params:
                    raise SystemExit(f"{s['id']}: wav format {p} != {params}")
                frames = w.readframes(w.getnframes())
            if i:
                outw.writeframes(pause_frames)
                cursor += len(pause_frames)
            start = cursor
            outw.writeframes(frames)
            cursor += len(frames)
            bps = params[0] * params[1] * params[2]
            timings.append({"id": s["id"], "start": start / bps, "end": cursor / bps})

    write_json(ep / "audio" / "timings.json", timings)
    subprocess.run([os.environ.get("FFMPEG", "ffmpeg"), "-y", "-loglevel", "error", "-i", str(ep / "audio/episode.wav"),
                    "-codec:a", "libmp3lame", "-b:a", "192k", str(ep / "episode.mp3")], check=True)
    log(ep, "tts", f"episode.mp3 {timings[-1]['end'] / 60:.1f} min, {len(segs)} segments")


if __name__ == "__main__":
    main()
