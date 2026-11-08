"""Simplified kWh energy balance model, distinct from MATLAB/Simulink plant."""
from dataclasses import dataclass
import numpy as np
from src.fuzzy_ems import MamdaniEMS

@dataclass(frozen=True)
class Plant:
    capacity_kwh:float=50.0 # assumed: paper states 500 Ah, voltage unspecified
    power_limit_kw:float=8.0 # assumed
    efficiency_charge:float=.95
    efficiency_discharge:float=.95
    dt_hours:float=.25

def generate_day(seed=42,dt_hours=.25):
    """Reproducible 24-h synthetic PV/load profile, NOT data from paper."""
    rng=np.random.default_rng(seed)
    t=np.arange(0,24,dt_hours)
    day=np.maximum(0,np.sin(np.pi*(t-6)/12))
    cloud=.78+.18*np.sin(2*np.pi*t/5+seed*.1)
    pv=np.clip(27*day*cloud+rng.normal(0,.9,len(t))*day,0,None)
    evening=7*np.exp(-.5*((t-20)/2.3)**2)
    morning=4*np.exp(-.5*((t-8)/2.4)**2)
    load=np.clip(9+morning+evening+1.4*np.sin(t*1.4)+rng.normal(0,.6,len(t)),2,None)
    return t,pv,load

def simulate(pv_kw,load_kw,initial_soc,proposed=False,plant=Plant(),controller=None):
    """Reproducible closed-loop simulation with PV+grid+storage power conservation."""
    controller=controller or MamdaniEMS()
    pv_kw=np.asarray(pv_kw,dtype=float)
    load_kw=np.asarray(load_kw,dtype=float)
    if pv_kw.shape!=load_kw.shape or pv_kw.ndim!=1 or (pv_kw<0).any() or (load_kw<0).any():
        raise ValueError('Power series must be matching nonnegative 1D arrays')
    soc=float(initial_soc);rows=[]
    for i,(pv,load) in enumerate(zip(pv_kw,load_kw)):
        delta=float(load-pv)
        command=controller.from_power(float(pv),float(load),soc,proposed)
        requested_power=float(command*min(abs(delta),plant.power_limit_kw))
        if abs(delta)<1e-12 or np.sign(requested_power)!=np.sign(delta):requested_power=0.
        before=soc
        if requested_power>=0:
            dsoc=-requested_power*plant.dt_hours/(plant.efficiency_discharge*plant.capacity_kwh)*100
        else:
            dsoc=-requested_power*plant.dt_hours*plant.efficiency_charge/plant.capacity_kwh*100
        soc=float(np.clip(before+dsoc,0,100))
        # Power actually transferred after physical SOC clipping.
        battery_kw=((before-soc)*plant.capacity_kwh/(100*plant.dt_hours))
        battery_kw*=plant.efficiency_discharge if requested_power>=0 else 1/plant.efficiency_charge
        grid_kw=float(load-pv-battery_kw)
        rows.append({'step':i,'hour':i*plant.dt_hours,'pv_kw':float(pv),'load_kw':float(load),
                     'soc_before':before,'soc_after':soc,'command':float(command),
                     'battery_kw':float(battery_kw),'grid_kw':grid_kw,
                     'unsafe_low_discharge':int(before<=20 and battery_kw>1e-9),
                     'unsafe_high_charge':int(before>=80 and battery_kw< -1e-9),
                     'outside_safe_band':int(soc<20-1e-9 or soc>80+1e-9)})
    return rows
