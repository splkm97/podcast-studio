"""Naver CLOVA Voice Premium adapter.

Env: CLOVA_CLIENT_ID, CLOVA_CLIENT_SECRET (API Gateway app credentials).
Voice dict keys are passed through as request fields (speaker, speed, pitch,
emotion, emotion-strength, alpha, end-pitch).
"""
import os
import time
from pathlib import Path

import requests

from tools.tts.base import TTSEngine

URL = "https://naveropenapi.apigw.ntruss.com/tts-premium/v1/tts"


class ClovaEngine(TTSEngine):
    max_chars = 2000  # Korean limit per request

    def __init__(self, cfg):
        super().__init__(cfg)
        try:
            self.headers = {
                "X-NCP-APIGW-API-KEY-ID": os.environ["CLOVA_CLIENT_ID"],
                "X-NCP-APIGW-API-KEY": os.environ["CLOVA_CLIENT_SECRET"],
            }
        except KeyError as e:
            raise SystemExit(f"missing env {e.args[0]}")

    def synth(self, text, voice, out_path: Path):
        if len(text) > self.max_chars:
            raise ValueError(f"text {len(text)} chars > {self.max_chars}")
        data = {**voice, "text": text, "format": "wav", "sampling-rate": self.SAMPLE_RATE}
        for attempt in range(4):
            r = requests.post(URL, headers=self.headers, data=data, timeout=60)
            if r.status_code == 200:
                out_path.write_bytes(r.content)
                return
            if r.status_code in (429, 500, 502, 503, 504) and attempt < 3:
                time.sleep(2 ** attempt)
                continue
            raise RuntimeError(f"CLOVA {r.status_code}: {r.text[:300]}")
