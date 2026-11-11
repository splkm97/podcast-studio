"""Publish Transistor draft episodes, oldest upload first, so the RSS feed keeps upload order.

Only episodes with a transistor.json (uploaded by tools.upload_transistor) are
considered. Without --yes it only prints the plan. Publishing makes episodes
public and sends them to every app the show is distributed to (Spotify etc.).

usage: python3 -m tools.publish_transistor                       # plan for all drafts
       python3 -m tools.publish_transistor --yes episodes/<id> ...   # only these
"""
import argparse
import time
from pathlib import Path

from tools.common import ROOT, episode_dir, log, read_json, write_json
from tools.upload_transistor import call


def live_episodes(show_ids: set[str]) -> dict[str, dict]:
    """Episode id -> attributes, one paged list call per show (API limit: 10 requests / 10 s)."""
    out = {}
    for sid in show_ids:
        page = 0
        while True:
            body = call("GET", "/episodes", params={"show_id": sid, "pagination[page]": page, "pagination[per]": 50})
            out.update({e["id"]: e["attributes"] for e in body["data"]})
            if page + 1 >= body.get("meta", {}).get("totalPages", 1):
                break
            page += 1
    return out


def drafts(only: list[Path]) -> list[tuple[Path, dict]]:
    eps = only or sorted(p.parent for p in (ROOT / "episodes").glob("*/transistor.json"))
    recs = {}
    for ep in eps:
        if (ep / "transistor.json").exists():
            recs[ep] = read_json(ep / "transistor.json")
        else:
            print(f"skip {ep.name}: not uploaded to Transistor")
    live = live_episodes({r["show_id"] for r in recs.values()})
    found = []
    for ep, rec in recs.items():
        attrs = live.get(rec["episode_id"])
        if attrs is None:
            print(f"skip {ep.name}: episode {rec['episode_id']} no longer exists in Transistor")
        elif attrs["status"] != "draft":
            print(f"skip {ep.name}: already {attrs['status']}")
        else:
            found.append((ep, {**rec, "title": attrs["title"]}))
    return sorted(found, key=lambda x: int(x[1]["episode_id"]))  # Transistor ids grow with upload time


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("episodes", nargs="*")
    ap.add_argument("--yes", action="store_true", help="actually publish")
    a = ap.parse_args()
    if a.yes and not a.episodes:
        ap.error("--yes requires explicit episode paths from the approved plan")

    plan = drafts([episode_dir(e) for e in a.episodes])
    for i, (ep, rec) in enumerate(plan, 1):
        print(f"{i:2}. {ep.name}  {rec['title'][:60]}")
    if not plan:
        print("no drafts to publish")
        return
    if not a.yes:
        print(f"\n{len(plan)} drafts. After approval, re-run with --yes and the approved episode paths explicitly.")
        return
    for ep, rec in plan:
        e = call("PATCH", f"/episodes/{rec['episode_id']}/publish",
                 data={"episode[status]": "published"})["data"]["attributes"]
        write_json(ep / "transistor.json", {**{k: v for k, v in rec.items() if k != "title"},
                                            "status": e["status"], "share_url": e.get("share_url", rec.get("share_url")),
                                            "published_at": e.get("published_at")})
        log(ep, "publish", f"transistor {e['status']} {e.get('share_url')}")
        print(f"published {ep.name}")
        time.sleep(1.5)  # API limit: 10 requests / 10 s, and distinct publish times keep feed order


if __name__ == "__main__":
    main()
