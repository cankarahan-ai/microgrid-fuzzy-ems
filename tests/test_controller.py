import unittest
import numpy as np
from src.fuzzy_ems import MamdaniEMS,RULES,triangle
from src.simulator import generate_day,simulate

class TestEMS(unittest.TestCase):
    def setUp(self):self.f=MamdaniEMS()
    def test_nine_rules(self):self.assertEqual(len(RULES),9)
    def test_input_memberships(self):
        for v,term in [(-1,'surplus'),(0,'balanced'),(1,'deficit')]:
            p,_=self.f.memberships(v,50);self.assertAlmostEqual(p[term],1)
        for v,term in [(0,'low'),(50,'medium'),(100,'high')]:
            _,s=self.f.memberships(0,v);self.assertAlmostEqual(s[term],1)
    def test_directions(self):
        self.assertLess(self.f.infer(-1,10),0)
        self.assertGreater(self.f.infer(1,90),0)
        self.assertAlmostEqual(self.f.infer(0,50),0,places=9)
    def test_safety_filter(self):
        self.assertEqual(self.f.safety_extension(.5,20),0)
        self.assertEqual(self.f.safety_extension(-.5,80),0)
        self.assertAlmostEqual(self.f.safety_extension(.6,25),.3)
        self.assertLess(self.f.safety_extension(-.5,10),0)
    def test_finite(self):
        for b in np.linspace(-1,1,11):
            for s in np.linspace(0,100,11):
                self.assertTrue(np.isfinite(self.f.infer(float(b),float(s))))
    def test_energy_conservation(self):
        _,p,l=generate_day(seed=3)
        for proposed in [False,True]:
            for r in simulate(p,l,25,proposed):
                self.assertAlmostEqual(r['pv_kw']+r['battery_kw']+r['grid_kw'],r['load_kw'])
                self.assertGreaterEqual(r['soc_after'],0)
                self.assertLessEqual(r['soc_after'],100)
    def test_membership_overlap_sum_not_required_one(self):
        _,s=self.f.memberships(-.5,25)
        self.assertGreater(s['low'],0)
        self.assertGreater(s['medium'],0)
if __name__=='__main__':unittest.main()
