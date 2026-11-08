"""Reconstructed Mamdani EMS subsystem based on Nur-E-Alam et al. (2025), Fig. 3.

This is NOT the original full Simulink microgrid implementation. Our kW input
normalization is an explicit assumption. Output: negative charge, positive
discharge, zero hold. 9 rules transcribed from the figure image.
"""
from dataclasses import dataclass
import numpy as np

RULES = {
    ('surplus', 'low'): 'charge',
    ('surplus', 'medium'): 'charge',
    ('surplus', 'high'): 'hold',
    ('deficit', 'low'): 'hold',
    ('deficit', 'medium'): 'discharge',
    ('deficit', 'high'): 'discharge',
    ('balanced', 'low'): 'hold',
    ('balanced', 'medium'): 'hold',
    ('balanced', 'high'): 'hold',
}

def triangle(x,a,b,c):
    """Triangle membership including clipped-shoulders outside plotted universe."""
    x=np.asarray(x,dtype=float)
    if not a<b<c: raise ValueError('Must satisfy a<b<c')
    return np.maximum(0,np.minimum((x-a)/(b-a),(c-x)/(c-b)))

@dataclass(frozen=True)
class Config:
    normalization_kw: float=20.0  # assumption, not given by original article
    points: int=1001
    soc_min: float=20.0
    soc_max: float=80.0
    guard_width: float=10.0

class MamdaniEMS:
    def __init__(self,cfg=Config()):
        self.cfg=cfg
        self.output_x=np.linspace(-1,1,cfg.points)
        self.output_mfs={
            'charge':triangle(self.output_x,-2,-1,0),
            'hold':triangle(self.output_x,-1,0,1),
            'discharge':triangle(self.output_x,0,1,2)}

    @staticmethod
    def memberships(balance,soc):
        if not -1<=balance<=1 or not 0<=soc<=100:raise ValueError('outside universe')
        return ({'surplus':float(triangle(balance,-2,-1,0)),
                 'balanced':float(triangle(balance,-1,0,1)),
                 'deficit':float(triangle(balance,0,1,2))},
                {'low':float(triangle(soc,-50,0,50)),
                 'medium':float(triangle(soc,0,50,100)),
                 'high':float(triangle(soc,50,100,150))})

    def infer(self,balance,soc,details=False):
        """Mamdani: min AND; min implication; max aggregation; centroid."""
        p,s=self.memberships(balance,soc)
        agg=np.zeros_like(self.output_x)
        rules=[]
        for (pname,sname),action in RULES.items():
            strength=min(p[pname],s[sname])
            rules.append({'condition':f'{pname} & {sname}','output':action,'strength':strength})
            agg=np.maximum(agg,np.minimum(strength,self.output_mfs[action]))
        area=float(np.trapezoid(agg,self.output_x))
        value=float(np.trapezoid(agg*self.output_x,self.output_x)/area) if area>1e-12 else 0.0
        if details: return {'action':value,'power_memberships':p,'soc_memberships':s,'rules':rules}
        return value

    def from_power(self,pv_kw,load_kw,soc,proposed=False):
        balance=float(np.clip((load_kw-pv_kw)/self.cfg.normalization_kw,-1,1))
        raw=self.infer(balance,soc)
        return self.safety_extension(raw,soc) if proposed else raw

    def safety_extension(self,action,soc):
        """Our original extension: direction-sensitive smooth SOC safety filter.
        At SOC <=20, prohibit discharging; at SOC >=80, prohibit charging.
        Allow charging at low SOC and discharging at high SOC (safe recovery).
        """
        width=self.cfg.guard_width
        if width<=0:raise ValueError('guard_width must be > 0')
        if action>0:
            strength=np.clip((soc-self.cfg.soc_min)/width,0,1)
        elif action<0:
            strength=np.clip((self.cfg.soc_max-soc)/width,0,1)
        else: strength=1
        return float(action*strength)
