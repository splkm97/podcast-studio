"""Pipeline regressions run without loading the workstation's secrets."""
from pathlib import Path
from unittest.mock import patch

_env_file = Path(__file__).resolve().parents[1] / ".env"
_exists = Path.exists
with patch.object(Path, "exists", lambda p: False if p == _env_file else _exists(p)):
    from tools import common
