"""Las copias de _studio_layout.py que viven en las herramientas (TarroDL, etc.) tienen que ser identicas a la canonica.

Busca la carpeta TarroTools (variable TARROTOOLS_ROOT, o una carpeta hermana de algun padre de este repo) y compara.
Si no encuentra ninguna copia, se salta: no obliga a tener las herramientas instaladas.

Correr:  python scripts/test_studio_layout_copias.py
"""
import os
import unittest
from pathlib import Path

CANONICA = Path(__file__).resolve().parent / "_studio_layout.py"
PATRONES = (
    "*/tarrodl_taller/teaser/_studio_layout.py",
    "*/.claude/worktrees/*/tarrodl_taller/teaser/_studio_layout.py",
    "*/scripts/_studio_layout.py",
)


def raiz_tarrotools():
    env = os.environ.get("TARROTOOLS_ROOT")
    if env and Path(env).is_dir():
        return Path(env)
    for padre in CANONICA.parents:
        cand = padre.parent / "TarroTools"
        if cand.is_dir():
            return cand
    return None


def copias():
    raiz = raiz_tarrotools()
    if raiz is None:
        return []
    return sorted({p.resolve() for pat in PATRONES for p in raiz.glob(pat)})


def normal(p: Path) -> bytes:
    return p.read_bytes().replace(b"\r\n", b"\n")


class CopiasDeStudioLayoutTest(unittest.TestCase):
    def test_las_copias_son_identicas_a_la_canonica(self):
        encontradas = copias()
        if not encontradas:
            self.skipTest("no hay copias de _studio_layout.py en TarroTools")
        for c in encontradas:
            if c == CANONICA.resolve():
                continue
            self.assertEqual(normal(c), normal(CANONICA), f"copia desfasada: {c}")


if __name__ == "__main__":
    unittest.main()
