import unittest

from common import tarrodl as T


def V(dur, a=0.0, b=None, name="v"):
    return {"file": name, "duration": float(dur), "a": float(a), "b": float(dur if b is None else b)}


def counts(plan):
    return [len(l["starts"]) for l in plan["lanes"]]


class PlanMultiTest(unittest.TestCase):
    def test_suma_exacta_y_cantidad(self):
        p = T.plan_multi([V(3600, name=str(i)) for i in range(5)], 300, 15, "parejo", 0)
        self.assertEqual(p["pieces"], 20)
        self.assertEqual(p["seg"], 15.0)
        self.assertEqual(len(p["sequence"]), 20)
        self.assertLess(abs(p["sequence"][-1]["at"] + p["seg"] - 300), 1e-6)

    def test_seg_nunca_menor_que_piece(self):
        p = T.plan_multi([V(3600), V(3600)], 300, 40, "parejo", 0)
        self.assertEqual(p["pieces"], 7)
        self.assertGreater(p["seg"], 40)
        self.assertAlmostEqual(p["seg"] * p["pieces"], 300, places=6)

    def test_sin_solapes_dentro_de_cada_video(self):
        for seed in (0, 5):
            p = T.plan_multi([V(900, 100, 700), V(1200), V(400)], 300, 15, "parejo", seed)
            for l in p["lanes"]:
                a, b = l["range"]
                for s in l["starts"]:
                    self.assertGreaterEqual(s, a - 1e-6)
                    self.assertLessEqual(s + p["seg"], b + 1e-6)
                for x, y in zip(l["starts"], l["starts"][1:]):
                    self.assertGreaterEqual(y - x, p["seg"] - 1e-6)

    def test_intercalado(self):
        p = T.plan_multi([V(600, name="a"), V(600, name="b"), V(600, name="c")], 90, 10, "parejo", 0)
        self.assertEqual([s["video"] for s in p["sequence"]][:6], [0, 1, 2, 0, 1, 2])
        for v in range(3):
            st = [s["start"] for s in p["sequence"] if s["video"] == v]
            self.assertEqual(st, sorted(st))

    def test_parejo_reparte_igual_y_sobrante_a_las_secciones_largas(self):
        p = T.plan_multi([V(3600), V(1800), V(600)], 100, 10, "parejo", 0)
        self.assertEqual(p["pieces"], 10)
        self.assertEqual(counts(p), [4, 3, 3])

    def test_proporcional_sesga_al_largo(self):
        p = T.plan_multi([V(3600), V(1800), V(600)], 100, 10, "proporcional", 0)
        c = counts(p)
        self.assertEqual(sum(c), 10)
        self.assertGreater(c[0], c[2])

    def test_video_corto_cede_sus_trozos(self):
        p = T.plan_multi([V(3600), V(3600), V(20)], 150, 15, "parejo", 0)
        self.assertLessEqual(counts(p)[2], 1)
        self.assertEqual(sum(counts(p)), p["pieces"])

    def test_video_mas_corto_que_un_trozo_recibe_cero(self):
        p = T.plan_multi([V(3600), V(3600), V(8)], 150, 15, "parejo", 0)
        self.assertEqual(p["lanes"][2]["starts"], [])
        self.assertEqual(sum(counts(p)), p["pieces"])

    def test_no_caben_error_claro(self):
        with self.assertRaises(T.ApiError) as cm:
            T.plan_multi([V(100), V(100)], 300, 15, "parejo", 0)
        self.assertIn("no alcanzan", str(cm.exception))

    def test_semilla(self):
        vs = [V(1200), V(1200), V(1200)]
        a0, b0 = T.plan_multi(vs, 120, 10, "parejo", 0), T.plan_multi(vs, 120, 10, "parejo", 0)
        a7, b7 = T.plan_multi(vs, 120, 10, "parejo", 7), T.plan_multi(vs, 120, 10, "parejo", 7)
        self.assertEqual(a0, b0)
        self.assertEqual(a7, b7)
        self.assertNotEqual(a0["lanes"], a7["lanes"])
        w = 1200 / 4
        self.assertAlmostEqual(a0["lanes"][0]["starts"][0], (w - a0["seg"]) / 2, places=6)  # centrado en su ranura

    def test_frames_exactos_cuando_el_trozo_no_calza_con_30_fps(self):
        for total, piece in ((300, 13), (885, 10), (100, 13)):
            p = T.plan_multi([V(3600, name=str(i)) for i in range(3)], total, piece, "parejo", 0)
            frames = [s["frames"] for s in p["sequence"]]
            self.assertEqual(sum(frames), total * 30, (total, piece))
            self.assertLessEqual(max(frames) - min(frames), 1)
            acc = 0
            for s in p["sequence"]:
                self.assertAlmostEqual(s["at"], acc / 30, places=9)
                acc += s["frames"]

    def test_cada_trozo_cabe_en_su_video_incluso_redondeado_a_frames(self):
        for seed in (0, 3):
            p = T.plan_multi([V(100), V(100), V(100)], 285, 13, "parejo", seed)
            for s in p["sequence"]:
                lane = p["lanes"][s["video"]]
                self.assertLessEqual(s["start"] + s["frames"] / 30, lane["range"][1] + 1e-9)

    def test_validate_mosaic_params(self):
        bad = [(1, 300, 15, "parejo", 0, 1080), (13, 300, 15, "parejo", 0, 1080), (2, 59, 15, "parejo", 0, 1080),
               (2, 901, 15, "parejo", 0, 1080), (2, 300, 9, "parejo", 0, 1080), (2, 300, 61, "parejo", 0, 1080),
               (2, 60, 61, "parejo", 0, 1080), (2, 300, 15, "x", 0, 1080), (2, 300, 15, "parejo", -1, 1080),
               (2, 300, 15, "parejo", 0, 480)]
        for args in bad:
            with self.assertRaises(T.ApiError, msg=str(args)):
                T.validate_mosaic_params(*args)
        T.validate_mosaic_params(2, 300, 15, "parejo", 0, 1080)


if __name__ == "__main__":
    unittest.main()
