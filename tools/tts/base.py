from pathlib import Path


class TTSEngine:
    """Contract: write a mono 16-bit PCM WAV at SAMPLE_RATE for one segment.

    All engines must emit the same WAV format so segments can be joined
    sample-exactly (timings drive the subtitles).
    """
    max_chars = 2000
    SAMPLE_RATE = 24000

    def __init__(self, cfg: dict):
        self.cfg = cfg

    def synth(self, text: str, voice: dict, out_path: Path) -> None:
        raise NotImplementedError
