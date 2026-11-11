import re
import unittest

from tools.render_video import build_srt


def seconds(value):
    h, m, s, ms = map(int, re.split("[:,]", value))
    return h * 3600 + m * 60 + s + ms / 1000


class SubtitleTests(unittest.TestCase):
    def cues(self, text):
        output = build_srt([{"id": "s001", "src": text}], [{"id": "s001", "start": 1.25, "end": 31.25}])
        cues = []
        for block in output.strip().split("\n\n"):
            lines = block.splitlines()
            start, end = map(seconds, lines[1].split(" --> "))
            cues.append((start, end, lines[2:]))
        return cues

    def assert_lossless(self, text):
        cues = self.cues(text)
        rendered = "".join("".join(lines) for _, _, lines in cues)
        self.assertEqual("".join(rendered.split()), "".join(text.split()))
        self.assertEqual(cues[0][0], 1.25)
        self.assertEqual(cues[-1][1], 31.25)
        previous_end = 1.25
        for start, end, lines in cues:
            self.assertEqual(start, previous_end)
            self.assertGreater(end, start)
            self.assertLessEqual(len(lines), 3)
            self.assertTrue(all(len(line) <= 32 for line in lines))
            previous_end = end
        return cues

    def test_wrap_boundary_preserves_tail_and_timing(self):
        for length, count in ((96, 1), (97, 2), (300, 4)):
            with self.subTest(length=length):
                text = "가" * (length - 1) + "끝"
                self.assertEqual(len(self.assert_lossless(text)), count)

    def test_multiple_sentences_and_original_technical_spelling_survive(self):
        text = "Kubernetes에서 context-window를 관리하는 조건과 제한을 설명합니다. " + "긴 문장도 핵심 근거와 실패 조건을 빠짐없이 자막으로 전달해야 합니다 " * 6 + "마지막은 etcd입니다."
        self.assert_lossless(text)

    def test_short_caption_remains_one_cue(self):
        cues = self.assert_lossless("etcd 복구를 시작합니다.")
        self.assertEqual(cues, [(1.25, 31.25, ["etcd 복구를 시작합니다."])])
