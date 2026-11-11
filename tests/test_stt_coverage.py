import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from tools import verify_stt


class STTCoverageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.ep = Path(self.temp.name)
        self.segments = [
            {"id": "s012", "tts": "첫 문장입니다"},
            {"id": "s012a", "tts": "나머지 문장입니다"},
        ]
        (self.ep / "script.json").write_text(json.dumps({"segments": self.segments}))
        (self.ep / "gates").mkdir()
        self.gate = self.ep / "gates/stt.json"
        self.transcribed = []

    def run_gate(self, only=None):
        heard = {"s012": "첫 문장입니다", "s012a": "나머지 문장입니다"}

        def transcribe(path):
            self.transcribed.append(path.stem)
            return heard[path.stem]

        argv = ["verify_stt", str(self.ep)] + (["--only", only] if only else [])
        with patch("sys.argv", argv), \
             patch.object(verify_stt, "load_config", return_value={"stt": {"max_cer": 0.15}}), \
             patch.object(verify_stt, "load_glossary", return_value={}), \
             patch.object(verify_stt, "get_engine", return_value=SimpleNamespace(transcribe=transcribe)), \
             contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaises(SystemExit) as result:
                verify_stt.main()
        return result.exception.code, json.loads(self.gate.read_text())

    def test_partial_retry_cannot_pass_with_unchecked_split_segment(self):
        self.gate.write_text(json.dumps({"results": [{"id": "s012", "cer": 0.8}]}))
        code, gate = self.run_gate("s012")
        self.assertEqual(code, 1)
        self.assertFalse(gate["passed"])
        self.assertEqual(self.transcribed, ["s012"])
        self.assertEqual({r["id"] for r in gate["results"]}, {"s012"})

    def test_full_retry_covers_split_segments_and_clears_old_failure(self):
        self.gate.write_text(json.dumps({"passed": False, "results": [{"id": "s012", "cer": 0.8}]}))
        code, gate = self.run_gate()
        self.assertEqual(code, 0)
        self.assertTrue(gate["passed"])
        self.assertEqual(self.transcribed, ["s012", "s012a"])
        self.assertEqual({r["id"] for r in gate["results"]}, {"s012", "s012a"})

    def test_partial_retry_preserves_other_segment_failure(self):
        self.gate.write_text(json.dumps({"results": [{"id": "s012", "cer": 0.8}, {"id": "s012a", "cer": 0.7}]}))
        code, gate = self.run_gate("s012")
        self.assertEqual(code, 1)
        self.assertFalse(gate["passed"])
        self.assertEqual({r["id"]: r["cer"] for r in gate["results"]}, {"s012": 0.0, "s012a": 0.7})
