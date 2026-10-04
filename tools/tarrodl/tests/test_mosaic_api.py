import os
import shutil
import tempfile
import time
import unittest
from pathlib import Path

import common
from common import tarrodl as T


class MosaicApiTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="tdl-mosaic-"))
        common.isolate(cls.tmp)
        cls.srv, call = common.start_server()
        cls.call = staticmethod(call)
        v = cls.tmp / "videos"
        cls.a = str(common.make_video(v / "a.mp4", 40))
        cls.b = str(common.make_video(v / "b.mp4", 60))
        cls.c = str(common.make_video(v / "c.mp4", 90))
        cls.mudo = str(common.make_video(v / "mudo.mp4", 30, audio=False))
        cls.raro = str(common.make_video(v / "Juego ñandú [test] (1).mp4", 30))
        cls.solo_audio = str(common.make_audio_only(v / "solo-audio.mp4", 30))

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()
        cls.srv.server_close()
        for h in list(T.log.handlers):
            h.close()
            T.log.removeHandler(h)
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def body(self, files=None, **kw):
        files = files or [self.a, self.b, self.c]
        d = {"videos": [{"file": f} for f in files], "total_sec": 60, "piece_sec": 10, "seed": 0}
        d.update(kw)
        return d

    def test_probe_devuelve_duracion_y_audio(self):
        code, r = self.call("/api/probe", {"files": [self.a, self.b]})
        self.assertEqual(code, 200)
        self.assertAlmostEqual(r["videos"][0]["duration"], 40, delta=1)
        self.assertAlmostEqual(r["videos"][1]["duration"], 60, delta=1)
        self.assertTrue(r["videos"][0]["audio"])
        self.assertFalse(self.call("/api/probe", {"files": [self.mudo]})[1]["videos"][0]["audio"])

    def test_probe_archivo_inexistente_400_con_nombre(self):
        code, r = self.call("/api/probe", {"files": [str(self.tmp / "no-existe.mp4")]})
        self.assertEqual(code, 400)
        self.assertIn("no-existe.mp4", r["error"])

    def test_probe_acepta_nombres_raros(self):
        code, r = self.call("/api/probe", {"files": [self.raro]})
        self.assertEqual(code, 200)
        self.assertEqual(r["videos"][0]["name"], "Juego ñandú [test] (1).mp4")

    def test_plan_ok(self):
        code, r = self.call("/api/mosaic_plan", self.body())
        self.assertEqual(code, 200)
        self.assertEqual(len(r["sequence"]), 6)
        self.assertEqual([l["file"] for l in r["lanes"]], [self.a, self.b, self.c])
        self.assertEqual(r["total"], 60)

    def test_plan_respeta_rango_por_video(self):
        d = self.body()
        d["videos"][0].update(range_start=10, range_end=30)
        code, r = self.call("/api/mosaic_plan", d)
        self.assertEqual(code, 200)
        for s in r["lanes"][0]["starts"]:
            self.assertGreaterEqual(s, 10)
            self.assertLessEqual(s, 30)

    def test_plan_mismos_parametros_mismo_plan(self):
        r1 = self.call("/api/mosaic_plan", self.body())[1]
        r2 = self.call("/api/mosaic_plan", self.body())[1]
        r3 = self.call("/api/mosaic_plan", self.body(seed=3))[1]
        self.assertEqual(r1, r2)
        self.assertNotEqual(r1["lanes"], r3["lanes"])

    def test_duplicados_normalizados(self):
        for dup in (self.a.replace("\\", "/"), self.a.upper()):
            code, r = self.call("/api/mosaic_plan", self.body([self.a, dup]))
            self.assertEqual(code, 400, dup)
            self.assertIn("repetido", r["error"])

    def test_validaciones(self):
        (self.tmp / "x.txt").write_text("hola")
        cases = [self.body([self.a]), self.body([self.a] * 13), self.body([self.a, str(self.tmp / "x.txt")]),
                 self.body(total_sec=30), self.body(height=480), self.body(share="x")]
        for c in cases:
            self.assertEqual(self.call("/api/mosaic_plan", c)[0], 400, str(c)[:80])

    def test_session_files_lista_videos_recientes_primero_y_sin_temporales(self):
        for old_f in T.out_base().iterdir():
            old_f.unlink()
        dl = T.out_base()
        old, new = dl / "viejo.mp4", dl / "nuevo.mkv"
        old.write_bytes(b"x")
        new.write_bytes(b"x")
        (dl / "x.temp.mp4").write_bytes(b"x")
        (dl / "notas.txt").write_text("x")
        os.utime(old, (time.time() - 100, time.time() - 100))
        code, r = self.call("/api/session_files")
        self.assertEqual(code, 200)
        self.assertEqual([f["name"] for f in r["files"]], ["nuevo.mkv", "viejo.mp4"])

    def test_archivo_sin_video_se_rechaza_con_su_nombre(self):
        code, r = self.call("/api/probe", {"files": [self.solo_audio]})
        self.assertEqual(code, 400)
        self.assertIn("solo-audio.mp4", r["error"])
        code, r = self.call("/api/mosaic_plan", self.body([self.a, self.solo_audio]))
        self.assertEqual(code, 400)
        self.assertIn("solo-audio.mp4", r["error"])

    def test_session_files_excluye_pistas_sueltas_de_yt_dlp(self):
        for old_f in T.out_base().iterdir():
            old_f.unlink()
        dl = T.out_base()
        for n in ("pista.f137.mp4", "pista.f251.webm", "pista.f401.mkv"):
            (dl / n).write_bytes(b"x")
        (dl / "completo.mp4").write_bytes(b"x")
        names = [f["name"] for f in self.call("/api/session_files")[1]["files"]]
        self.assertIn("completo.mp4", names)
        self.assertFalse([n for n in names if ".f137." in n or ".f251." in n or ".f401." in n])

    def test_parse_picked(self):
        self.assertEqual(T.parse_picked("C:\\a.mp4\r\n\r\nC:\\b.txt\r\nC:\\c.MKV\r\n"), ["C:\\a.mp4", "C:\\c.MKV"])

    def test_probe_cache_no_vuelve_a_medir(self):
        calls, orig = [], T.probe_duration
        T.probe_duration = lambda fp, src: (calls.append(1), orig(fp, src))[1]
        try:
            T.PROBE_CACHE.clear()
            T.probe_video(Path(self.a))
            T.probe_video(Path(self.a))
            self.assertEqual(len(calls), 1)
            st = os.stat(self.a)
            os.utime(self.a, ns=(st.st_atime_ns, st.st_mtime_ns + 5_000_000_000))
            T.probe_video(Path(self.a))
            self.assertEqual(len(calls), 2)
        finally:
            T.probe_duration = orig


if __name__ == "__main__":
    unittest.main()
