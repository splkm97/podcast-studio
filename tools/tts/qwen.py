"""Local Qwen3-TTS adapter (open weights, no API key, no per-character cost).

Install: pip install -r requirements-qwen.txt (torch + qwen-tts, several GB).
Config (podcast.yaml tts.qwen): model (Hugging Face id or local path, default
Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice), device (auto | cuda:0 | mps | cpu).
Voice dict: {speaker: Sohee, language: Korean, instruct: <optional, 1.7B only>}.
The model loads on the first synth call, so fully cached runs stay fast.
"""
import os
import subprocess
from pathlib import Path

from tools.tts.base import TTSEngine

DEFAULT_MODEL = "Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice"


class QwenEngine(TTSEngine):
    max_chars = 1000  # keep generations short; long inputs drift

    def __init__(self, cfg):
        super().__init__(cfg)
        self.opts = cfg.get("qwen") or {}
        self.model = None

    def _load(self):
        try:
            import torch
            from qwen_tts import Qwen3TTSModel
        except ImportError as e:
            raise SystemExit(f"qwen engine needs: pip install -r requirements-qwen.txt ({e})")
        device = self.opts.get("device", "auto")
        if device == "auto":
            device = ("cuda:0" if torch.cuda.is_available()
                      else "mps" if torch.backends.mps.is_available() else "cpu")
        dtype = torch.bfloat16 if device.startswith("cuda") else torch.float32
        self.model = Qwen3TTSModel.from_pretrained(self.opts.get("model", DEFAULT_MODEL),
                                                   device_map=device, dtype=dtype)

    def synth(self, text, voice, out_path: Path):
        if len(text) > self.max_chars:
            raise ValueError(f"text {len(text)} chars > {self.max_chars}")
        if self.model is None:
            self._load()
        import numpy as np
        kw = {"instruct": voice["instruct"]} if voice.get("instruct") else {}
        wavs, sr = self.model.generate_custom_voice(
            text=text, language=voice.get("language", "Korean"), speaker=voice["speaker"], **kw)
        pcm = np.clip(np.asarray(wavs[0], dtype=np.float32).reshape(-1), -1.0, 1.0)
        # Normalize to the shared contract (mono s16 @ SAMPLE_RATE) with ffmpeg's resampler.
        subprocess.run([os.environ.get("FFMPEG", "ffmpeg"), "-y", "-loglevel", "error",
                        "-f", "f32le", "-ar", str(sr), "-ac", "1", "-i", "pipe:0",
                        "-ar", str(self.SAMPLE_RATE), "-ac", "1", "-c:a", "pcm_s16le", str(out_path)],
                       input=pcm.tobytes(), check=True)
