"""Upload episode.mp4 to YouTube (private by default). Never uploads twice.

Env: YOUTUBE_CLIENT_SECRETS  path to the OAuth client JSON (Desktop app)
     YOUTUBE_TOKEN           token path (default ~/.config/podcast-studio/youtube-token.json)

usage: python3 -m tools.upload_youtube --auth          # one-time, interactive
       python3 -m tools.upload_youtube episodes/<id>
"""
import argparse
import os
import sys
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from tools.common import episode_dir, load_config, log, read_json, write_json

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
TOKEN = Path(os.environ.get("YOUTUBE_TOKEN",
                            Path.home() / ".config/podcast-studio/youtube-token.json"))


def credentials(interactive: bool) -> Credentials:
    creds = Credentials.from_authorized_user_file(str(TOKEN), SCOPES) if TOKEN.exists() else None
    if creds and creds.valid:
        return creds
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
        except Exception as e:
            if not interactive:
                sys.exit(f"token refresh failed ({e}); run: python3 -m tools.upload_youtube --auth")
            creds = None
    if not creds or not creds.valid:
        if not interactive:
            sys.exit("no valid YouTube token; run: python3 -m tools.upload_youtube --auth")
        flow = InstalledAppFlow.from_client_secrets_file(os.environ["YOUTUBE_CLIENT_SECRETS"], SCOPES)
        creds = flow.run_local_server(port=0)
    TOKEN.parent.mkdir(parents=True, exist_ok=True)
    TOKEN.write_text(creds.to_json())
    os.chmod(TOKEN, 0o600)
    return creds


def description(ep: Path, episode: dict) -> str:
    lines = [episode["description"].strip(), "", "참고 자료"]
    for s in read_json(ep / "sources.json"):
        if s.get("url"):
            lines.append(f"- {s.get('title', s['url'])}: {s['url']}")
    lines += ["", "이 에피소드의 음성은 TTS로 합성되었습니다."]
    return "\n".join(lines)[:5000]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("episode", nargs="?")
    ap.add_argument("--auth", action="store_true")
    a = ap.parse_args()
    if a.auth:
        credentials(interactive=True)
        print(f"token saved to {TOKEN}")
        return

    ep = episode_dir(a.episode)
    done = ep / "upload.json"
    if done.exists():
        sys.exit(f"already uploaded: {read_json(done)['url']} (delete upload.json to re-upload)")

    cfg = load_config()["youtube"]
    episode = read_json(ep / "script.json")["episode"]
    body = {
        "snippet": {"title": episode["title"][:100], "description": description(ep, episode),
                    "tags": episode.get("tags", []), "categoryId": cfg["category_id"],
                    "defaultLanguage": "ko", "defaultAudioLanguage": "ko"},
        "status": {"privacyStatus": cfg["privacy"], "selfDeclaredMadeForKids": False,
                   "containsSyntheticMedia": bool(cfg.get("contains_synthetic_media", True))},
    }
    yt = build("youtube", "v3", credentials=credentials(interactive=False))
    req = yt.videos().insert(part="snippet,status", body=body,
                             media_body=MediaFileUpload(str(ep / "episode.mp4"),
                                                        chunksize=8 * 1024 * 1024, resumable=True))
    resp = None
    while resp is None:
        _, resp = req.next_chunk()
    url = f"https://youtu.be/{resp['id']}"
    write_json(done, {"video_id": resp["id"], "url": url, "privacy": resp["status"]["privacyStatus"]})
    log(ep, "upload", f"uploaded {url} ({resp['status']['privacyStatus']})")


if __name__ == "__main__":
    main()
