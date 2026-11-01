"""Write a report atomically without truncating an existing destination."""

import os
import stat
import tempfile
from pathlib import Path


def write_report(destination: Path, content: str) -> None:
    if destination.is_symlink():
        raise OSError("output must not be a symbolic link")
    mode = stat.S_IMODE(destination.stat().st_mode) if destination.exists() else None
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=destination.parent,
            prefix=f".{destination.name}.", suffix=".tmp", delete=False,
        ) as stream:
            temporary = Path(stream.name)
            stream.write(content)
        if mode is not None:
            temporary.chmod(mode)
        os.replace(temporary, destination)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
