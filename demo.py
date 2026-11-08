"""Interactive or example command-line demo of the reconstructed FIS.

Examples:
    python demo.py --pv 15 --load 23 --soc 18
    python demo.py --pv 23 --load 12 --soc 85
    python demo.py
"""
import argparse
from src.fuzzy_ems import MamdaniEMS

def demo(pv,load,soc):
    ems=MamdaniEMS()
    normalized=max(-1,min(1,(load-pv)/ems.cfg.normalization_kw))
    result=ems.infer(normalized,soc,details=True)
    base=result['action'];safe=ems.safety_extension(base,soc)
    print(f'PV: {pv:.2f} kW | Load: {load:.2f} kW | SOC: {soc:.1f}%')
    print(f'Normalized balance: {normalized:+.3f}')
    print('Power memberships:',', '.join(f'{k}={v:.3f}' for k,v in result['power_memberships'].items()))
    print('SOC memberships:',', '.join(f'{k}={v:.3f}' for k,v in result['soc_memberships'].items()))
    print('Active rules:')
    for r in sorted(result['rules'],key=lambda x:-x['strength']):
        if r['strength']>1e-6:print(f"  [{r['strength']:.3f}] IF {r['condition']} THEN {r['output']}")
    print(f'Baseline action: {base:+.5f} | Proposed action: {safe:+.5f}')
    print('Sign meaning: negative charge | positive discharge | zero hold')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description='Fuzzy microgrid energy controller demo')
    parser.add_argument('--pv',type=float,default=14.0,help='PV generation, kW')
    parser.add_argument('--load',type=float,default=22.0,help='Load, kW')
    parser.add_argument('--soc',type=float,default=19.0,help='Battery SOC, 0..100 percent')
    args=parser.parse_args()
    if args.pv<0 or args.load<0:parser.error('PV/load must be >=0')
    if not 0<=args.soc<=100:parser.error('SOC must be within [0,100]')
    demo(args.pv,args.load,args.soc)
