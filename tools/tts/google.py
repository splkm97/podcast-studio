"""Google Cloud Text-to-Speech adapter (REST v1, API key auth).

Env: GOOGLE_TTS_API_KEY (API key restricted to the Cloud Text-to-Speech API).
Voice dict: {name: <voice name, e.g. ko-KR-Chirp3-HD-Kore>}. The language code
is derived from the name prefix.
"""
import base64
import os
import time
from pathlib import Path

import requests

from tools.tts.base import TTSEngine

URL = "https://texttospeech.googleapis.com/v1/text:synthesize"
MAX_BYTES = 5000  # API limit on input text, in UTF-8 bytes


class GoogleEngine(TTSEngine):
    max_chars = 1600  # ~MAX_BYTES / 3 bytes per Hangul syllable

    def __init__(self, cfg):
        super().__init__(cfg)
        key = os.environ.get("GOOGLE_TTS_API_KEY")
        if not key:
            raise SystemExit("missing env GOOGLE_TTS_API_KEY")
        self.headers = {"X-Goog-Api-Key": key}

    def synth(self, text, voice, out_path: Path):
        if len(text.encode("utf-8")) > MAX_BYTES:
            raise ValueError(f"text {len(text.encode('utf-8'))} bytes > {MAX_BYTES}")
        name = voice["name"]
        body = {
            "input": {"text": text},
            "voice": {"languageCode": "-".join(name.split("-")[:2]), "name": name},
            "audioConfig": {"audioEncoding": "LINEAR16", "sampleRateHertz": self.SAMPLE_RATE},
        }
        for attempt in range(4):
            r = requests.post(URL, headers=self.headers, json=body, timeout=60)
            if r.status_code == 200:
                # LINEAR16 responses already carry a WAV header.
                out_path.write_bytes(base64.b64decode(r.json()["audioContent"]))
                return
            if r.status_code in (429, 500, 502, 503, 504) and attempt < 3:
                time.sleep(2 ** attempt)
                continue
            raise RuntimeError(f"Google TTS {r.status_code}: {r.text[:300]}")
