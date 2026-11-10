"""Gate: every source in sources.json is reachable (URL) or present (local path).

usage: python3 -m tools.check_links episodes/<id>
"""
import sys
from pathlib import Path

import requests

from tools.common import episode_dir, finish_gate, read_json, ROOT

UA = {"User-Agent": "Mozilla/5.0 (podcast-studio link check)"}


def reachable(url: str) -> str | None:
    for method in ("head", "get"):
        try:
            r = requests.request(method, url, headers=UA, timeout=15,
                                 allow_redirects=True, stream=(method == "get"))
            if r.status_code < 400:
                return None
            last = f"HTTP {r.status_code}"
        except requests.RequestException as e:
            last = type(e).__name__
    return last


def main():
    ep = episode_dir(sys.argv[1])
    sources = read_json(ep / "sources.json")
    problems = []
    if not sources:
        problems.append("sources.json is empty")
    for s in sources:
        if s.get("url"):
            err = reachable(s["url"])
            if err:
                problems.append(f"{s['id']}: {s['url']} -> {err}")
        elif s.get("path"):
            p = Path(s["path"])
            if not (p if p.is_absolute() else ROOT / p).exists():
                problems.append(f"{s['id']}: missing file {s['path']}")
        else:
            problems.append(f"{s.get('id', '?')}: neither url nor path")
    finish_gate(ep, "links", problems, {"checked": len(sources)})


if __name__ == "__main__":
    main()
