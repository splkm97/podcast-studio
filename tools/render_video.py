"""Static cover + burned-in subtitles + episode.mp3 -> episode.mp4.

Subtitles use the original-spelling script (src), timed from the exact
segment timings; long segments are split by sentence, proportional to length.

usage: python3 -m tools.render_video episodes/<id>
"""
import os
import re
import subprocess
import sys
import textwrap

from tools.common import ROOT, episode_dir, load_config, log, read_json

LINE_WIDTH = 32
TITLE_WIDTH = 24


def ts(sec: float) -> str:
    ms = int(round(sec * 1000))
    return f"{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02},{ms % 1000:03}"


def build_srt(segs, timings) -> str:
    by_id = {s["id"]: s for s in segs}
    cues = []
    for t in timings:
        chunks = []
        for sentence in re.split(r"(?<=[.?!])\s+", by_id[t["id"]]["src"].strip()):
            lines = textwrap.wrap(sentence, LINE_WIDTH, break_on_hyphens=False)
            chunks.extend("\n".join(lines[i:i + 3]) for i in range(0, len(lines), 3))
        total = sum(len(chunk) for chunk in chunks)
        consumed = 0
        cursor = t["start"]
        for chunk in chunks:
            consumed += len(chunk)
            end = t["start"] + (t["end"] - t["start"]) * consumed / total
            cues.append((cursor, end, chunk))
            cursor = end
    return "\n".join(f"{i}\n{ts(a)} --> {ts(b)}\n{txt}\n" for i, (a, b, txt) in enumerate(cues, 1))


def main():
    ep = episode_dir(sys.argv[1])
    cfg = load_config()["video"]
    script = read_json(ep / "script.json")
    (ep / "subtitles.srt").write_text(
        build_srt(script["segments"], read_json(ep / "audio" / "timings.json")), encoding="utf-8")

    cover = ROOT / cfg.get("cover", "")
    font = cfg.get("font", "Noto Sans CJK KR")
    if cfg.get("cover") and cover.is_file():
        cover_in = ["-loop", "1", "-i", str(cover)]
        base = "[0:v]scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2"
    else:  # generated title card
        # One drawtext per line: a single 72px line overflows 1920px past ~24 Hangul chars.
        lines = [w for part in script["episode"]["title"].replace("'", "’").split(": ")
                 for w in textwrap.wrap(part, TITLE_WIDTH, break_on_hyphens=False)]
        cover_in = ["-f", "lavfi", "-i", "color=c=0x111827:s=1920x1080:r=10"]
        base = "[0:v]" + ",".join(
            f"drawtext=font='{font}':text='{line.replace(':', chr(92) + ':')}':fontcolor=white:fontsize=72:"
            f"x=(w-tw)/2:y=h*0.30+{i * 100}" for i, line in enumerate(lines))
    style = f"FontName={font},FontSize=22,Outline=2,MarginV=40"
    vf = f"{base},subtitles=subtitles.srt:force_style='{style}'[v]"

    subprocess.run([os.environ.get("FFMPEG", "ffmpeg"), "-y", "-loglevel", "error", *cover_in, "-i", "episode.mp3",
                    "-filter_complex", vf, "-map", "[v]", "-map", "1:a", "-r", "10",
                    "-c:v", "libx264", "-tune", "stillimage", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "192k", "-shortest", "episode.mp4"],
                   cwd=ep, check=True)
    log(ep, "video", "episode.mp4 rendered")


if __name__ == "__main__":
    main()
