"""Offline engine for pipeline tests: a quiet tone sized like real speech."""
import math
import struct
import wave

from tools.tts.base import TTSEngine


class DryRunEngine(TTSEngine):
    SEC_PER_CHAR = 0.18

    def synth(self, text, voice, out_path):
        n = int(len(text) * self.SEC_PER_CHAR * self.SAMPLE_RATE)
        freq = 220 if voice.get("speaker", "").startswith("vg") else 330
        frames = b"".join(struct.pack("<h", int(3000 * math.sin(2 * math.pi * freq * i / self.SAMPLE_RATE)))
                          for i in range(n))
        with wave.open(str(out_path), "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(self.SAMPLE_RATE)
            w.writeframes(frames)
