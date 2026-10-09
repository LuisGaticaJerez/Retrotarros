import os
import shutil
import tempfile
import time
import unittest
from pathlib import Path

import common
from common import tarrodl as T


def stamp(seconds_ago: float) -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time() - seconds_ago))


class RecentLinksTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="tdl-links-"))
        common.isolate(cls.tmp)
        cls.srv, call = common.start_server()
        cls.call = staticmethod(call)
        cls.dl = cls.tmp / "dl"

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()
        cls.srv.server_close()
        for h in list(T.log.handlers):
            h.close()
            T.log.removeHandler(h)
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def setUp(self):
        f = T.links_file()
        if f.exists():
            f.unlink()
        for x in self.dl.iterdir():
            x.unlink()
        T.JOBS.clear()

    def test_archivo_vive_en_la_carpeta_de_config(self):
        self.assertEqual(T.links_file(), T.CONFIG_DIR / "links-recientes.txt")

    def test_agregar_crea_el_archivo_con_encabezado_y_la_linea(self):
        T.links_add("https://youtu.be/abc", "Mi video", "mp4", 1080)
        text = T.links_file().read_text(encoding="utf-8")
        self.assertTrue(text.startswith("# TarroDL"))
        self.assertIn(" | https://youtu.be/abc | Mi video | mp4 | 1080", text)
        got = T.links_recent()
        self.assertEqual(len(got), 1)
        self.assertEqual(got[0]["url"], "https://youtu.be/abc")
        self.assertEqual(got[0]["slug"], "Mi video")

    def test_varias_lineas_se_acumulan_en_orden(self):
        T.links_add("https://youtu.be/1", "uno", "mp4", 720)
        T.links_add("https://youtu.be/2", "dos", "mkv", 1080)
        self.assertEqual([k["slug"] for k in T.links_recent()], ["uno", "dos"])

    def test_lo_de_mas_de_48_horas_se_borra_al_leer(self):
        T.links_file().write_text(T.LINKS_HEADER + f"{stamp(49 * 3600)} | https://youtu.be/viejo | viejo | mp4 | 1080\n"
                                  + f"{stamp(47 * 3600)} | https://youtu.be/casi | casi | mp4 | 1080\n", encoding="utf-8")
        got = T.links_recent()
        self.assertEqual([k["slug"] for k in got], ["casi"])
        text = T.links_file().read_text(encoding="utf-8")
        self.assertNotIn("viejo", text)
        self.assertIn("casi", text)

    def test_si_todo_venció_el_archivo_desaparece(self):
        T.links_file().write_text(T.LINKS_HEADER + f"{stamp(72 * 3600)} | https://youtu.be/viejo | viejo | mp4 | 1080\n", encoding="utf-8")
        self.assertEqual(T.links_recent(), [])
        self.assertFalse(T.links_file().exists())

    def test_agregar_tambien_limpia_lo_vencido(self):
        T.links_file().write_text(T.LINKS_HEADER + f"{stamp(100 * 3600)} | https://youtu.be/viejo | viejo | mp4 | 1080\n", encoding="utf-8")
        T.links_add("https://youtu.be/nuevo", "nuevo", "mp4", 1080)
        text = T.links_file().read_text(encoding="utf-8")
        self.assertNotIn("viejo", text)
        self.assertIn("nuevo", text)

    def test_sin_archivo_no_falla(self):
        self.assertEqual(T.links_recent(), [])

    def test_lineas_basura_se_ignoran(self):
        T.links_file().write_text("basura sin formato\n" + T.LINKS_HEADER + "no | es | fecha | x | y\n"
                                  + f"{stamp(60)} | https://youtu.be/ok | ok | mp4 | 720\n", encoding="utf-8")
        self.assertEqual([k["slug"] for k in T.links_recent()], ["ok"])

    def test_el_separador_en_el_nombre_no_rompe_la_linea(self):
        T.links_add("https://youtu.be/x", "Parte 1 | Parte 2", "mp4", 1080)
        got = T.links_recent()
        self.assertEqual(len(got), 1)
        self.assertEqual(got[0]["slug"], "Parte 1 / Parte 2")

    def test_un_fallo_al_escribir_no_rompe_la_descarga(self):
        T.links_file().mkdir(parents=True)  # una carpeta donde deberia ir el archivo: escribir falla
        try:
            T.links_add("https://youtu.be/x", "x", "mp4", 1080)  # no debe lanzar
        finally:
            T.links_file().rmdir()

    def test_los_parciales_muestran_el_link_guardado(self):
        (self.dl / "Gameplay.f298.mp4.part").write_bytes(b"x" * 10)
        (self.dl / "Otro.f298.mp4.part").write_bytes(b"x" * 10)
        T.links_add("https://youtu.be/gameplay", "Gameplay", "mp4", 1080)
        st, r = self.call("/api/partials", None)
        self.assertEqual(st, 200)
        links = {g["slug"]: g["link"] for g in r["items"]}
        self.assertEqual(links["Gameplay"], "https://youtu.be/gameplay")
        self.assertEqual(links["Otro"], "")

    def test_si_hay_dos_links_del_mismo_nombre_gana_el_mas_reciente(self):
        (self.dl / "Gameplay.mp4.part").write_bytes(b"x" * 10)
        T.links_file().write_text(T.LINKS_HEADER + f"{stamp(3600)} | https://youtu.be/viejo | Gameplay | mp4 | 1080\n"
                                  + f"{stamp(60)} | https://youtu.be/nuevo | Gameplay | mp4 | 1080\n", encoding="utf-8")
        st, r = self.call("/api/partials", None)
        self.assertEqual(r["items"][0]["link"], "https://youtu.be/nuevo")

    def test_abrir_links_crea_el_archivo_y_lo_abre(self):
        abiertos = []
        real = getattr(os, "startfile", None)
        os.startfile = lambda p: abiertos.append(p)
        try:
            st, r = self.call("/api/open_links", {})
        finally:
            if real:
                os.startfile = real
        self.assertEqual(st, 200)
        self.assertEqual(abiertos, [str(T.links_file())])
        self.assertTrue(T.links_file().exists())


if __name__ == "__main__":
    unittest.main()
