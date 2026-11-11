"""Gate: audio length is sane and there are no long silences.

- per segment seconds-per-char outside [0.06, 0.5] -> truncated or garbled
- total length over max_minutes
- any silence >= 2.5s inside episode.wav (inserted pauses are far shorter)

usage: python3 -m tools.check_audio episodes/<id>
"""
import os
import re
import subprocess
import sys

from tools.common import episode_dir, finish_gate, load_config, read_json

MIN_SPC, MAX_SPC, MAX_SILENCE = 0.06, 0.5, 2.5


def main():
    ep = episode_dir(sys.argv[1])
    cfg = load_config()
    segs = {s["id"]: s for s in read_json(ep / "script.json")["segments"]}
    timings = read_json(ep / "audio" / "timings.json")
    problems = []

    for t in timings:
        dur = t["end"] - t["start"]
        spc = dur / max(len(segs[t["id"]]["tts"]), 1)
        if not MIN_SPC <= spc <= MAX_SPC:
            problems.append(f"{t['id']}: {dur:.1f}s for {len(segs[t['id']]['tts'])} chars ({spc:.2f}s/char)")

    total = timings[-1]["end"]
    if total > cfg["max_minutes"] * 60:
        problems.append(f"total {total / 60:.1f} min > max_minutes {cfg['max_minutes']}")

    try:
        run = subprocess.run(
            [os.environ.get("FFMPEG", "ffmpeg"), "-i", str(ep / "audio" / "episode.wav"), "-af",
             f"silencedetect=noise=-45dB:d={MAX_SILENCE}", "-f", "null", "-"],
            capture_output=True, text=True)
    except OSError as e:
        print(f"ffmpeg not runnable: {e}", file=sys.stderr)
        sys.exit(2)
    if run.returncode != 0:
        print(f"ffmpeg failed ({run.returncode}), silence check did not run:\n{run.stderr[-500:]}", file=sys.stderr)
        sys.exit(2)
    out = run.stderr
    for start, dur in zip(re.findall(r"silence_start: ([\d.]+)", out),
                          re.findall(r"silence_duration: ([\d.]+)", out)):
        seg = next((t["id"] for t in timings if t["start"] <= float(start) < t["end"]), "pause")
        problems.append(f"silence {float(dur):.1f}s at {float(start):.1f}s ({seg})")

    finish_gate(ep, "audio", problems, {"total_minutes": round(total / 60, 1)})


if __name__ == "__main__":
    main()
