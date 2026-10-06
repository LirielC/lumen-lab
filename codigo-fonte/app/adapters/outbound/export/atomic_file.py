

from contextlib import contextmanager
import os
from pathlib import Path
import tempfile
from collections.abc import Iterator


@contextmanager
def atomic_output_path(destination: Path) -> Iterator[Path]:
    
    destination = Path(destination)
    descriptor, name = tempfile.mkstemp(
        prefix=f".{destination.stem}-", suffix=destination.suffix,
        dir=destination.parent,
    )
    os.close(descriptor)
    temporary = Path(name)
    try:
        yield temporary
        os.replace(temporary, destination)
    finally:
        temporary.unlink(missing_ok=True)
