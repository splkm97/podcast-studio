import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools import publish_transistor


class PublishScopeTests(unittest.TestCase):
    def test_execution_requires_explicit_episode_paths_before_network(self):
        with patch("sys.argv", ["publish_transistor", "--yes"]), \
             patch.object(publish_transistor, "live_episodes", side_effect=AssertionError("network forbidden")) as api, \
             contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as error:
                publish_transistor.main()
            self.assertEqual(error.exception.code, 2)
            api.assert_not_called()

    def test_new_draft_after_preview_is_not_in_approved_execution(self):
        with tempfile.TemporaryDirectory() as directory, contextlib.ExitStack() as stack:
            root = Path(directory)
            live = {}

            def add_episode(name, episode_id):
                ep = root / "episodes" / name
                ep.mkdir(parents=True)
                (ep / "transistor.json").write_text(json.dumps({"episode_id": episode_id, "show_id": "show-1", "status": "draft", "share_url": f"https://example.test/{episode_id}"}))
                live[episode_id] = {"title": name, "status": "draft"}
                return ep

            approved = add_episode("approved", "101")
            stack.enter_context(patch.object(publish_transistor, "ROOT", root))
            stack.enter_context(patch.object(publish_transistor, "live_episodes", return_value=live))
            stack.enter_context(patch.object(publish_transistor.time, "sleep"))
            published = []

            def api(method, path, **kwargs):
                self.assertEqual(method, "PATCH")
                episode_id = path.split("/")[2]
                published.append(episode_id)
                live[episode_id]["status"] = "published"
                return {"data": {"attributes": {**live[episode_id], "published_at": "2026-01-01T00:00:00Z"}}}

            stack.enter_context(patch.object(publish_transistor, "call", side_effect=api))
            with patch("sys.argv", ["publish_transistor"]), contextlib.redirect_stdout(io.StringIO()) as output:
                publish_transistor.main()
            self.assertIn("approved", output.getvalue())
            self.assertEqual(published, [])

            unapproved = add_episode("unapproved", "102")
            with patch("sys.argv", ["publish_transistor", "--yes", str(approved)]), contextlib.redirect_stdout(io.StringIO()):
                publish_transistor.main()
            self.assertEqual(published, ["101"])
            self.assertEqual(json.loads((approved / "transistor.json").read_text())["status"], "published")
            self.assertEqual(json.loads((unapproved / "transistor.json").read_text())["status"], "draft")
