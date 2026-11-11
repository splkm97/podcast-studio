"""Upload episode.mp3 to Transistor.fm as a draft (by default). Never uploads twice.

Spotify, Apple and other apps read the show's Transistor RSS feed, so an episode
reaches them only after it is published. The show itself is submitted to
Spotify once from Transistor's Distribution tab (see the podcast-setup skill).

Env: TRANSISTOR_API_KEY   (Transistor dashboard > Account > API)
     TRANSISTOR_SHOW_ID   optional when the account has exactly one show

usage: python3 -m tools.upload_transistor --shows        # list shows and their ids
       python3 -m tools.upload_transistor episodes/<id>
"""
import argparse
import html
import os
import sys
import time
from pathlib import Path

import requests

from tools.common import episode_dir, load_config, log, read_json, write_json

API = "https://api.transistor.fm/v1"


def call(method: str, path: str, **kw) -> dict:
    key = os.environ.get("TRANSISTOR_API_KEY")
    if not key:
        sys.exit("missing env TRANSISTOR_API_KEY")
    for wait in (15, 60, 180, 0):  # 429 = rate limit (10 requests / 10 s); back off and retry
        r = requests.request(method, f"{API}{path}", headers={"x-api-key": key}, timeout=60, **kw)
        if r.status_code != 429 or not wait:
            break
        time.sleep(wait)
    if not r.ok:  # create returns 201
        sys.exit(f"Transistor {method} {path} failed {r.status_code}: {r.text[:300]}")
    return r.json()


def shows() -> list[dict]:
    return call("GET", "/shows", params={"pagination[per]": 50})["data"]


def show_id() -> str:
    if os.environ.get("TRANSISTOR_SHOW_ID"):
        return os.environ["TRANSISTOR_SHOW_ID"]
    found = shows()
    if len(found) != 1:
        names = ", ".join(f"{s['id']}={s['attributes']['title']}" for s in found) or "none"
        sys.exit(f"set TRANSISTOR_SHOW_ID in .env; shows: {names}")
    return found[0]["id"]


def upload_audio(path: Path) -> str:
    auth = call("GET", "/episodes/authorize_upload", params={"filename": path.name})["data"]["attributes"]
    with open(path, "rb") as f:
        put = requests.put(auth["upload_url"], data=f,
                           headers={"Content-Type": auth["content_type"]}, timeout=600)
    put.raise_for_status()
    return auth["audio_url"]


def show_notes(ep: Path, episode: dict) -> str:
    """Episode description, sources and TTS disclosure as simple HTML."""
    parts = [f"<p>{html.escape(episode['description'].strip(), quote=False)}</p>", "<p>참고 자료</p><ul>"]
    for s in read_json(ep / "sources.json"):
        if s.get("url"):
            url = html.escape(s["url"], quote=True)
            parts.append(f'<li><a href="{url}">{html.escape(s.get("title", s["url"]), quote=False)}</a></li>')
    parts += ["</ul>", "<p>이 에피소드의 음성은 TTS로 합성되었습니다.</p>"]
    return "".join(parts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("episode", nargs="?")
    ap.add_argument("--shows", action="store_true")
    a = ap.parse_args()
    if a.shows:
        for s in shows():
            print(s["id"], s["attributes"]["title"])
        return

    ep = episode_dir(a.episode)
    done = ep / "transistor.json"
    if done.exists():
        sys.exit(f"already uploaded to Transistor: {read_json(done)['share_url']}")

    if load_config()["transistor"]["status"] != "draft":
        sys.exit("transistor.status must be draft for uploads; use tools.publish_transistor to publish reviewed episodes")
    episode = read_json(ep / "script.json")["episode"]
    sid = show_id()
    audio_url = upload_audio(ep / "episode.mp3")
    e = call("POST", "/episodes", data={
        "episode[show_id]": sid, "episode[title]": episode["title"],
        "episode[summary]": episode["description"].strip()[:500],
        "episode[description]": show_notes(ep, episode),
        "episode[audio_url]": audio_url, "episode[type]": "full"})["data"]
    write_json(done, {"episode_id": e["id"], "show_id": sid, "share_url": e["attributes"].get("share_url"),
                      "status": e["attributes"].get("status")})
    log(ep, "upload", f"transistor {e['attributes'].get('status')} {e['attributes'].get('share_url')}")


if __name__ == "__main__":
    main()
