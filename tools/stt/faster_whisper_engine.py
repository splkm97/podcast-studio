"""Local open-source STT (faster-whisper, CPU int8 by default)."""
from faster_whisper import WhisperModel


class FasterWhisperEngine:
    def __init__(self, cfg):
        self.model = WhisperModel(cfg.get("model", "small"),
                                  device=cfg.get("device", "auto"),
                                  compute_type=cfg.get("compute_type", "int8"))

    def transcribe(self, wav_path) -> str:
        segments, _ = self.model.transcribe(str(wav_path), language="ko", beam_size=5)
        return " ".join(s.text.strip() for s in segments)
