import glob
import json
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

import common
from common import tarrodl as T

FFPROBE = None


def ffprobe(path):
    r = subprocess.run([T.find_tool("ffprobe"), "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)],
                       capture_output=True, text=True, creationflags=T.NOWIN)
    return json.loads(r.stdout)


def graphs():
    return set(glob.glob(str(Path(tempfile.gettempdir()) / "*.ffgraph")))


class FilterUnitTest(unittest.TestCase):
    def test_mosaic_filter_estructura(self):
        seq = [{"video": 0, "start": 0, "at": 0, "frames": 300}, {"video": 1, "start": 0, "at": 10, "frames": 300}, {"video": 2, "start": 0, "at": 20, "frames": 300}]
        f = T.mosaic_filter(seq, [True, False, True], 10.0, 1080)
        self.assertEqual(f.count("scale=1920:1080"), 3)
        self.assertEqual(f.count("anullsrc"), 1)
        self.assertTrue(f.strip().endswith("concat=n=3:v=1:a=1[v][a]"))
        self.assertIn("scale=1280:720", T.mosaic_filter(seq, [True] * 3, 10.0, 720))

    def test_unique_name(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            self.assertEqual(T.unique_name(d, "mosaico").name, "mosaico.mp4")
            (d / "mosaico.mp4").write_bytes(b"x")
            (d / "mosaico_2.mp4").write_bytes(b"x")
            self.assertEqual(T.unique_name(d, "mosaico").name, "mosaico_3.mp4")


class MosaicRenderTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="tdl-render-"))
        common.isolate(cls.tmp)
        cls.srv, call = common.start_server()
        cls.call = staticmethod(call)
        v = cls.tmp / "videos"
        cls.a = str(common.make_video(v / "a.mp4", 45))
        cls.b = str(common.make_video(v / "b.mp4", 60, size="320x180", fps=25))
        cls.c = str(common.make_video(v / "c.mp4", 50, audio=False))
        cls.d = str(common.make_video(v / "d.mp4", 50, size="120x216"))
        cls.raro = str(common.make_video(v / "Juego ñandú [test] (1).mp4", 50))
        cls.long = [str(common.make_video(v / f"largo{i}.mp4", 300, size="320x180")) for i in range(3)]

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()
        cls.srv.server_close()
        for h in list(T.log.handlers):
            h.close()
            T.log.removeHandler(h)
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def setUp(self):
        shutil.rmtree(T.clips_base(), ignore_errors=True)
        self.graphs0 = graphs()

    def body(self, files, **kw):
        d = {"videos": [{"file": f} for f in files], "total_sec": 60, "piece_sec": 10, "seed": 0, "height": 720}
        d.update(kw)
        return d

    def wait(self, job_id, states=("done", "error", "cancelled"), timeout=240):
        t0 = time.time()
        while time.time() - t0 < timeout:
            j = self.call("/api/job?id=" + job_id)[1]
            if j["state"] in states:
                return j
            time.sleep(0.3)
        self.fail(f"el job {job_id} no llego a {states}: {j['state']} {j['text']}")

    def render(self, files, **kw):
        code, r = self.call("/api/mosaic", self.body(files, **kw))
        self.assertEqual(code, 200, r)
        return self.wait(r["job"])

    def test_mosaico_mixto_dura_lo_pedido(self):
        j = self.render([self.a, self.b, self.c, self.d])
        self.assertEqual(j["state"], "done", j["text"])
        out = T.clips_base() / "mosaico.mp4"
        info = ffprobe(out)
        self.assertAlmostEqual(float(info["format"]["duration"]), 60, delta=0.5)
        vs = [s for s in info["streams"] if s["codec_type"] == "video"]
        au = [s for s in info["streams"] if s["codec_type"] == "audio"]
        self.assertEqual((len(vs), len(au)), (1, 1))
        self.assertEqual((vs[0]["width"], vs[0]["height"], vs[0]["r_frame_rate"]), (1280, 720, "30/1"))
        self.assertEqual((au[0]["sample_rate"], au[0]["channels"]), ("48000", 2))
        self.assertEqual(j["result"]["file"], "mosaico.mp4")

    def test_largo_exacto_cuando_el_trozo_no_calza_con_30_fps(self):
        j = self.render([self.a, self.b], total_sec=100, piece_sec=13)
        self.assertEqual(j["state"], "done", j["text"])
        dur = float(ffprobe(T.clips_base() / "mosaico.mp4")["format"]["duration"])
        self.assertAlmostEqual(dur, 100, delta=0.1)

    def test_vertical_queda_con_barras(self):
        j = self.render([self.d, self.a])
        self.assertEqual(j["state"], "done", j["text"])
        out = T.clips_base() / "mosaico.mp4"
        self.assertEqual((ffprobe(out)["streams"][0]["width"]), 1280)
        # primer trozo = video vertical: la columna izquierda es barra negra y el centro tiene imagen
        r = subprocess.run([T.find_tool("ffmpeg"), "-v", "error", "-ss", "1", "-i", str(out), "-frames:v", "1", "-vf", "format=gray",
                            "-f", "rawvideo", "-"], capture_output=True, creationflags=T.NOWIN)
        px, w = r.stdout, 1280
        left = [px[y * w + x] for y in range(720) for x in range(0, 40)]
        center = [px[y * w + x] for y in range(0, 720, 4) for x in range(600, 680, 2)]
        self.assertLessEqual(max(left), 20)
        self.assertGreater(sum(center) / len(center), 25)

    def test_nombre_con_caracteres_raros(self):
        j = self.render([self.raro, self.a, self.b], name="Mi Mosaico ñ")
        self.assertEqual(j["state"], "done", j["text"])
        self.assertTrue((T.clips_base() / "mi-mosaico-n.mp4").is_file())

    def test_nombre_repetido_agrega_sufijo(self):
        for _ in range(2):
            self.assertEqual(self.render([self.a, self.b], name="x")["state"], "done")
        self.assertTrue((T.clips_base() / "x.mp4").is_file() and (T.clips_base() / "x_2.mp4").is_file())

    def test_cancelar_borra_parcial_y_temporal(self):
        code, r = self.call("/api/mosaic", self.body(self.long, total_sec=300, piece_sec=15, height=1080, name="cancelame"))
        self.assertEqual(code, 200, r)
        t0 = time.time()
        while time.time() - t0 < 120:
            j = self.call("/api/job?id=" + r["job"])[1]
            if j["state"] == "running" and j["percent"] > 0:
                break
            self.assertNotIn(j["state"], ("done", "error"), j["text"])
            time.sleep(0.2)
        self.assertEqual(self.call("/api/cancel", {"job": r["job"]})[0], 200)
        self.assertEqual(self.wait(r["job"])["state"], "cancelled")
        self.assertEqual(list(T.clips_base().glob("cancelame*")), [])
        self.assertEqual(graphs(), self.graphs0)

    def test_cancelar_en_cola_no_crea_nada(self):
        code, r1 = self.call("/api/mosaic", self.body(self.long, total_sec=300, piece_sec=15, height=1080, name="primero"))
        self.assertEqual(code, 200, r1)
        t0 = time.time()
        while self.call("/api/job?id=" + r1["job"])[1]["state"] != "running" and time.time() - t0 < 60:
            time.sleep(0.2)
        code, r2 = self.call("/api/mosaic", self.body([self.a, self.b], name="segundo"))
        self.assertEqual(code, 200, r2)
        time.sleep(1)
        self.assertEqual(self.call("/api/job?id=" + r2["job"])[1]["state"], "queued")
        self.call("/api/cancel", {"job": r2["job"]})
        self.assertEqual(self.wait(r2["job"])["state"], "cancelled")
        self.call("/api/cancel", {"job": r1["job"]})
        self.wait(r1["job"])
        self.assertEqual(list(T.clips_base().glob("segundo*")), [])

    def test_archivo_desaparece_antes_de_crear(self):
        gone = str(common.make_video(self.tmp / "videos" / "tmp-borrar.mp4", 30))
        self.assertEqual(self.call("/api/mosaic_plan", self.body([self.a, gone]))[0], 200)
        Path(gone).unlink()
        n = len(T.JOBS)
        code, r = self.call("/api/mosaic", self.body([self.a, gone]))
        self.assertEqual(code, 400)
        self.assertIn("tmp-borrar.mp4", r["error"])
        self.assertEqual(len(T.JOBS), n)

    def test_error_de_ffmpeg_borra_parcial(self):
        fake_py = self.tmp / "fake_ffmpeg.py"
        fake_py.write_text("import sys\nopen(sys.argv[-1], 'wb').write(b'parcial')\nprint('boom')\nsys.exit(1)\n")
        fake = self.tmp / "fake_ffmpeg.cmd"
        fake.write_text(f'@"{sys.executable}" "{fake_py}" %*\r\n')
        orig = T.need_tool
        T.need_tool = lambda name, label=None: str(fake) if name == "ffmpeg" else orig(name, label)
        try:
            j = self.render([self.a, self.b], name="falla")
        finally:
            T.need_tool = orig
        self.assertEqual(j["state"], "error")
        self.assertEqual(list(T.clips_base().glob("falla*")), [])
        self.assertEqual(graphs(), self.graphs0)


if __name__ == "__main__":
    unittest.main()
