import shutil
import tempfile
import unittest
from pathlib import Path

import common
from common import tarrodl as T


class PartialsApiTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="tdl-partials-"))
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
        for f in self.dl.iterdir():
            f.unlink() if f.is_file() else shutil.rmtree(f)
        T.JOBS.clear()

    def touch(self, name, size=10):
        (self.dl / name).write_bytes(b"x" * size)

    def items(self):
        st, r = self.call("/api/partials", None)
        self.assertEqual(st, 200)
        return {g["slug"]: g for g in r["items"]}, r

    def test_carpeta_vacia_no_encuentra_nada(self):
        items, r = self.items()
        self.assertEqual(items, {})
        self.assertEqual(r["folder"], str(self.dl))

    def test_agrupa_las_pistas_y_el_ytdl_de_un_mismo_video(self):
        self.touch("Mi video.f298.mp4.part", 300)
        self.touch("Mi video.f140.m4a.part", 100)
        self.touch("Mi video.f298.mp4.ytdl", 5)
        items, _ = self.items()
        self.assertEqual(list(items), ["Mi video"])
        g = items["Mi video"]
        self.assertEqual(len(g["files"]), 3)
        self.assertEqual(g["size"], 405)
        self.assertTrue(g["resumable"])
        self.assertFalse(g["final_exists"])

    def test_detecta_part_simple_temp_y_pista_suelta(self):
        self.touch("uno.mp4.part")
        self.touch("dos.temp.mp4")
        self.touch("tres.f137.mp4")
        self.touch("cuatro.mp4.part-Frag3")
        items, _ = self.items()
        self.assertEqual(sorted(items), ["cuatro", "dos", "tres", "uno"])
        self.assertTrue(items["uno"]["resumable"])
        self.assertFalse(items["dos"]["resumable"])   # sin .part no hay nada que retomar
        self.assertTrue(items["cuatro"]["resumable"])

    def test_videos_terminados_no_aparecen(self):
        self.touch("listo.mp4", 500)
        self.touch("otro.mkv", 500)
        self.touch("clip_1.mp4", 500)
        items, _ = self.items()
        self.assertEqual(items, {})

    def test_si_el_final_ya_existe_son_restos_y_no_se_puede_retomar(self):
        self.touch("viejo.mp4", 500)
        self.touch("viejo.f298.mp4.part", 50)
        items, _ = self.items()
        self.assertTrue(items["viejo"]["final_exists"])
        self.assertFalse(items["viejo"]["resumable"])

    def test_descarga_en_curso_se_marca_activa(self):
        self.touch("bajando.f298.mp4.part", 50)
        T.JOBS["j1"] = {"id": "j1", "kind": "download", "state": "running", "target": str(self.dl / "bajando.mp4")}
        items, _ = self.items()
        self.assertTrue(items["bajando"]["active"])
        self.assertFalse(items["bajando"]["resumable"])

    def test_nombres_con_puntos_y_acentos(self):
        self.touch("Juego ñandú v1.2 (final).f298.mp4.part", 20)
        items, _ = self.items()
        self.assertEqual(list(items), ["Juego ñandú v1.2 (final)"])

    def test_carpeta_inexistente_no_falla(self):
        shutil.rmtree(self.dl)
        try:
            st, r = self.call("/api/partials", None)
            self.assertEqual(st, 200)
            self.assertEqual(r["items"], [])
            self.assertFalse(r["exists"])
        finally:
            self.dl.mkdir()

    def test_borrar_un_video_solo_toca_sus_restos(self):
        self.touch("uno.f298.mp4.part", 30)
        self.touch("uno.f298.mp4.ytdl", 5)
        self.touch("dos.f298.mp4.part", 30)
        self.touch("terminado.mp4", 99)
        st, r = self.call("/api/partials_delete", {"slug": "uno"})
        self.assertEqual(st, 200)
        self.assertEqual(sorted(r["deleted"]), ["uno.f298.mp4.part", "uno.f298.mp4.ytdl"])
        self.assertEqual(sorted(p.name for p in self.dl.iterdir()), ["dos.f298.mp4.part", "terminado.mp4"])

    def test_borrar_todos_deja_los_videos_terminados(self):
        self.touch("a.mp4.part")
        self.touch("b.temp.mp4")
        self.touch("final.mp4", 99)
        st, r = self.call("/api/partials_delete", {"all": True})
        self.assertEqual(st, 200)
        self.assertEqual(len(r["deleted"]), 2)
        self.assertEqual([p.name for p in self.dl.iterdir()], ["final.mp4"])

    def test_no_borra_una_descarga_en_curso(self):
        self.touch("bajando.f298.mp4.part", 50)
        T.JOBS["j1"] = {"id": "j1", "kind": "download", "state": "running", "target": str(self.dl / "bajando.mp4")}
        st, r = self.call("/api/partials_delete", {"all": True})
        self.assertEqual(r["deleted"], [])
        self.assertEqual(r["skipped"], ["bajando"])
        self.assertTrue((self.dl / "bajando.f298.mp4.part").exists())

    def test_borrar_sin_slug_o_inexistente_da_error(self):
        self.assertEqual(self.call("/api/partials_delete", {})[0], 400)
        self.assertEqual(self.call("/api/partials_delete", {"slug": "no-existe"})[0], 400)

    def test_no_sale_de_la_carpeta_con_slug_raro(self):
        outside = self.tmp / "fuera.mp4.part"
        outside.write_bytes(b"x")
        st, _ = self.call("/api/partials_delete", {"slug": "../fuera"})
        self.assertEqual(st, 400)
        self.assertTrue(outside.exists())


if __name__ == "__main__":
    unittest.main()
