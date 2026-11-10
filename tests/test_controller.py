import unittest
import numpy as np
from src.fuzzy_ems import MamdaniEMS, RULES, Config, triangle
from src.simulator import generate_day, simulate


class ControllerTests(unittest.TestCase):
    def setUp(self):
        self.ems = MamdaniEMS()

    def test_all_9_rules_transcribed(self):
        self.assertEqual(len(RULES), 9)
        self.assertEqual(RULES['surplus', 'low'], 'charge')
        self.assertEqual(RULES['deficit', 'low'], 'hold')
        self.assertEqual(RULES['surplus', 'high'], 'hold')
        self.assertEqual(RULES['deficit', 'high'], 'discharge')

    def test_triangular_peak(self):
        self.assertAlmostEqual(float(triangle(0, -1, 0, 1)), 1)
        self.assertAlmostEqual(float(triangle(.5, -1, 0, 1)), .5)

    def test_fig3_anchors(self):
        for label, bal in [('surplus', -1), ('balanced', 0), ('deficit', 1)]:
            p, _ = self.ems.memberships(bal, 50)
            self.assertAlmostEqual(p[label], 1)
        for label, soc in [('low', 0), ('medium', 50), ('high', 100)]:
            _, s = self.ems.memberships(0, soc)
            self.assertAlmostEqual(s[label], 1)

    def test_fig3_directions(self):
        self.assertLess(self.ems.infer(-1, 0), -.4)
        self.assertGreater(self.ems.infer(1, 100), .4)
        self.assertAlmostEqual(self.ems.infer(0, 50), 0., places=9)

    def test_text_cutoff_vs_fig3_discrepancy_is_visible(self):
        self.assertNotEqual(self.ems.control(-1, 0, 'fig3_fis'),
                            self.ems.control(-1, 0, 'text_cutoff'))
        self.assertEqual(self.ems.control(-1, 0, 'text_cutoff'), 0)
        self.assertEqual(self.ems.control(1, 100, 'text_cutoff'), 0)

    def test_proposed_forbids_dangerous_direction(self):
        for s in (0, 10, 20):
            self.assertEqual(self.ems.safety_extension(.4, s), 0)
        for s in (80, 90, 100):
            self.assertEqual(self.ems.safety_extension(-.4, s), 0)
        self.assertEqual(self.ems.safety_extension(.6, 25), .3)
        self.assertEqual(self.ems.safety_extension(-.6, 75), -.3)

    def test_proposed_allows_recovery(self):
        self.assertLess(self.ems.control(-1, 10, 'proposed'), 0)
        self.assertGreater(self.ems.control(1, 90, 'proposed'), 0)
        self.assertEqual(self.ems.control(-1, 10, 'text_cutoff'), 0)

    def test_no_nan_or_overflows(self):
        for bal in np.linspace(-1, 1, 13):
            for soc in np.linspace(0, 100, 13):
                for mode in ('fig3_fis', 'text_cutoff', 'proposed'):
                    value = self.ems.control(float(bal), float(soc), mode)
                    self.assertTrue(np.isfinite(value))
                    self.assertLessEqual(abs(value), 1)

    def test_energy_conservation(self):
        _, pv, load = generate_day(seed=42)
        rows = simulate(pv, load, 30, mode='proposed')
        self.assertEqual(len(rows), 96)
        self.assertLess(max(abs(x['energy_residual_kw']) for x in rows), 1.e-8)
        self.assertTrue(all(0 <= x['soc_after'] <= 100 for x in rows))

    def test_validation(self):
        with self.assertRaises(ValueError):
            self.ems.infer(2, 50)
        with self.assertRaises(ValueError):
            self.ems.infer(0, float('nan'))
        with self.assertRaises(ValueError):
            self.ems.control(0, 20, 'unknown')
        with self.assertRaises(ValueError):
            MamdaniEMS(Config(guard_width=0))
        with self.assertRaises(ValueError):
            self.ems.from_power(-1, 2, 50)


if __name__ == '__main__':
    unittest.main()
