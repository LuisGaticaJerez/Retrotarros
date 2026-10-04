"""Utilidades compartidas de las pruebas de TarroDL (se corren desde tools/tarrodl)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import tarrodl  # noqa: E402,F401
