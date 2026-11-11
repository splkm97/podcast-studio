import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools import upload_transistor, upload_youtube


class UploadSafetyTests(unittest.TestCase):
    def test_transistor_rejects_publication_before_network(self):
        with tempfile.TemporaryDirectory() as directory:
            ep = Path(directory)
            for status in ("published", "scheduled", "unlisted"):
                with self.subTest(status=status), contextlib.ExitStack() as stack:
                    stack.enter_context(patch("sys.argv", ["upload_transistor", str(ep)]))
                    stack.enter_context(patch.object(upload_transistor, "load_config", return_value={"transistor": {"status": status}}))
                    api = stack.enter_context(patch.object(upload_transistor, "call", side_effect=AssertionError("network forbidden")))
                    audio = stack.enter_context(patch.object(upload_transistor, "upload_audio", side_effect=AssertionError("upload forbidden")))
                    with self.assertRaisesRegex(SystemExit, "must be draft"):
                        upload_transistor.main()
                    api.assert_not_called()
                    audio.assert_not_called()
                    self.assertFalse((ep / "transistor.json").exists())

    def test_youtube_rejects_nonprivate_upload_before_authentication(self):
        with tempfile.TemporaryDirectory() as directory:
            ep = Path(directory)
            for privacy in ("public", "unlisted"):
                with self.subTest(privacy=privacy), contextlib.ExitStack() as stack:
                    stack.enter_context(patch("sys.argv", ["upload_youtube", str(ep)]))
                    stack.enter_context(patch.object(upload_youtube, "load_config", return_value={"youtube": {"privacy": privacy}}))
                    auth = stack.enter_context(patch.object(upload_youtube, "credentials", side_effect=AssertionError("authentication forbidden")))
                    api = stack.enter_context(patch.object(upload_youtube, "build", side_effect=AssertionError("network forbidden")))
                    with self.assertRaisesRegex(SystemExit, "must be private"):
                        upload_youtube.main()
                    auth.assert_not_called()
                    api.assert_not_called()
                    self.assertFalse((ep / "upload.json").exists())

    def test_draft_upload_creates_episode_without_publication(self):
        with tempfile.TemporaryDirectory() as directory, contextlib.ExitStack() as stack:
            ep = Path(directory)
            (ep / "script.json").write_text(json.dumps({"episode": {"title": "Example", "description": "Details"}}))
            (ep / "sources.json").write_text("[]")
            stack.enter_context(patch("sys.argv", ["upload_transistor", str(ep)]))
            stack.enter_context(patch.object(upload_transistor, "load_config", return_value={"transistor": {"status": "draft"}}))
            stack.enter_context(patch.object(upload_transistor, "show_id", return_value="show-1"))
            stack.enter_context(patch.object(upload_transistor, "upload_audio", return_value="https://example.test/audio.mp3"))
            calls = []

            def api(method, path, **kwargs):
                calls.append((method, path))
                if (method, path) != ("POST", "/episodes"):
                    raise AssertionError("Unexpected publication request")
                return {"data": {"id": "episode-1", "attributes": {"status": "draft", "share_url": "https://example.test/episode"}}}

            stack.enter_context(patch.object(upload_transistor, "call", side_effect=api))
            stack.enter_context(contextlib.redirect_stdout(io.StringIO()))
            upload_transistor.main()
            self.assertEqual(calls, [("POST", "/episodes")])
            self.assertEqual(json.loads((ep / "transistor.json").read_text())["status"], "draft")
