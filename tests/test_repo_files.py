from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent


@pytest.mark.parametrize("name", ["requirements.txt", "requirements-dev.txt"])
def test_requirements_files_are_plain_utf8(name):
    """Guards against PowerShell's `pip freeze > file` writing UTF-16.

    Use `pip freeze | Out-File -Encoding utf8NoBOM` (PowerShell 7) or
    `python -m pip freeze > requirements.txt` from Git Bash instead.
    """
    raw = (ROOT / name).read_bytes()
    assert not raw.startswith((b"\xef\xbb\xbf", b"\xff\xfe", b"\xfe\xff")), (
        f"{name} has a byte-order mark; save it as UTF-8 without BOM"
    )
    raw.decode("utf-8")
