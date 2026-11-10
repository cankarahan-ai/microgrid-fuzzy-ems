"""Live demonstration: python demo.py --pv 15 --load 23 --soc 18"""
import argparse
from src.fuzzy_ems import MamdaniEMS, MODES


def run(pv, load, soc):
    ems = MamdaniEMS()
    balance = max(-1., min(1., (load-pv)/ems.cfg.normalization_kw))
    details = ems.infer(balance, soc, details=True)
    print(f'PV={pv:.2f} kW | Load={load:.2f} kW | SOC={soc:.1f}% | balance={balance:+.3f}')
    print('Power memberships:', details['power_memberships'])
    print('SOC memberships:', details['soc_memberships'])
    for rule in sorted(details['rules'], key=lambda r: -r['strength']):
        if rule['strength'] > .00001:
            print(f"  IF {rule['condition']} THEN {rule['output']} (strength {rule['strength']:.3f})")
    for mode in MODES:
        value = ems.control(balance, soc, mode)
        print(f'  {mode:12}  {value:+.5f}')
    print('Sign convention: negative=charge; positive=discharge; zero=hold')


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--pv', type=float, default=15)
    p.add_argument('--load', type=float, default=23)
    p.add_argument('--soc', type=float, default=18)
    a = p.parse_args()
    if a.pv < 0 or a.load < 0 or not 0 <= a.soc <= 100:
        p.error('Require nonnegative PV/load and SOC in [0,100]')
    run(a.pv, a.load, a.soc)
