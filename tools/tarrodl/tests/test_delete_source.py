import shutil
import tempfile
import time
import unittest
from pathlib import Path

import common
from common import tarrodl as T


class DeleteSourceTest(unittest.TestCase):
    """Opcion 'borrar el video original cuando terminen los clips': solo si todos los clips quedaron bien."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="tdl-delsrc-"))
        common.isolate(cls.tmp)
        cls.srv, call = common.start_server()
        cls.call = staticmethod(call)
        cls.dl = cls.tmp / "dl"
        cls.clips = cls.tmp / "clips"
        cls.base = common.make_video(cls.tmp / "base.mp4", 75)   # 75 s: alcanza para un clip seguido de 60 s

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()
        cls.srv.server_close()
        for h in list(T.log.handlers):
            h.close()
            T.log.removeHandler(h)
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def setUp(self):
        for d in (self.dl, self.clips):
            if d.exists():
                shutil.rmtree(d)
            d.mkdir(parents=True)
        T.JOBS.clear()

    def video(self, name="juego.mp4") -> Path:
        dst = self.dl / name
        shutil.copy(self.base, dst)
        return dst

    def run_clips(self, body, timeout=120):
        st, r = self.call("/api/clips", body)
        self.assertEqual(st, 200, r)
        t0 = time.time()
        while time.time() - t0 < timeout:
            j = self.call("/api/job?id=" + r["job"])[1]
            if j["state"] in ("done", "error", "cancelled"):
                return j
            time.sleep(0.3)
        self.fail("el job no termino")

    def test_con_la_opcion_borra_el_original_y_deja_el_clip(self):
        src = self.video()
        j = self.run_clips({"file": str(src), "mode": "seguido", "length_sec": 60, "delete_source": True})
        self.assertEqual(j["state"], "done", j)
        self.assertFalse(src.exists())
        self.assertTrue(j["result"].get("source_deleted"))
        self.assertIn("Se borro el video original", j["text"])
        clips = list(self.clips.glob("juego_clip*.mp4"))
        self.assertEqual(len(clips), 1)
        self.assertGreater(clips[0].stat().st_size, 0)

    def test_sin_la_opcion_el_original_se_queda(self):
        src = self.video()
        j = self.run_clips({"file": str(src), "mode": "seguido", "length_sec": 60})
        self.assertEqual(j["state"], "done", j)
        self.assertTrue(src.exists())
        self.assertNotIn("source_deleted", j["result"])

    def test_si_los_clips_fallan_el_original_no_se_toca(self):
        src = self.video()
        # el video dura 75 s y se piden 3 minutos: no alcanza, el job termina en error antes de crear nada
        j = self.run_clips({"file": str(src), "mode": "seguido", "length_sec": 180, "delete_source": True})
        self.assertEqual(j["state"], "error")
        self.assertTrue(src.exists())
        self.assertEqual(list(self.clips.glob("*.mp4")) if self.clips.exists() else [], [])

    def test_valor_falso_no_borra(self):
        src = self.video()
        j = self.run_clips({"file": str(src), "mode": "seguido", "length_sec": 60, "delete_source": False})
        self.assertEqual(j["state"], "done", j)
        self.assertTrue(src.exists())

    def test_el_original_se_borra_tambien_con_mosaico(self):
        src = self.video()
        j = self.run_clips({"file": str(src), "mode": "mosaico", "length_sec": 60, "piece_sec": 15, "max_clips": 1,
                            "delete_source": True})
        self.assertEqual(j["state"], "done", j)
        self.assertFalse(src.exists())
        self.assertEqual(len(list(self.clips.glob("juego_clip*.mp4"))), 1)

    def test_si_el_original_esta_en_uso_avisa_y_deja_los_clips(self):
        src = self.video()
        real = T.delete_files
        T.delete_files = lambda paths: []   # simula Windows con el archivo bloqueado
        try:
            j = self.run_clips({"file": str(src), "mode": "seguido", "length_sec": 60, "delete_source": True})
        finally:
            T.delete_files = real
        self.assertEqual(j["state"], "done", j)
        self.assertTrue(src.exists())
        self.assertTrue(j["result"].get("source_delete_error"))
        self.assertIn("No pude borrar el video original", j["text"])
        self.assertEqual(len(list(self.clips.glob("juego_clip*.mp4"))), 1)


if __name__ == "__main__":
    unittest.main()
