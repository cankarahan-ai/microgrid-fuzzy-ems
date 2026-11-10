"""Transparent 15-minute energy-balance toy model, NOT Matlab/Simulink.

Everything in Plant, the PV/load generator and conversion between FIS commands
and kW is an illustrative project assumption, not an article parameter.
"""
from dataclasses import dataclass
import numpy as np
from src.fuzzy_ems import MamdaniEMS


@dataclass(frozen=True)
class Plant:
    capacity_kwh: float = 50.0
    power_limit_kw: float = 8.0
    efficiency_charge: float = .95
    efficiency_discharge: float = .95
    dt_hours: float = .25


def generate_day(seed=42, dt_hours=.25):
    rng = np.random.default_rng(seed)
    t = np.arange(0, 24, dt_hours)
    solar = np.maximum(0, np.sin(np.pi*(t-6)/12))
    cloud = .78+.18*np.sin(2*np.pi*t/5+seed*.1)
    pv = np.clip(27*solar*cloud+rng.normal(0, .9, len(t))*solar, 0, None)
    evening = 7*np.exp(-.5*((t-20)/2.3)**2)
    morning = 4*np.exp(-.5*((t-8)/2.4)**2)
    load = np.clip(9+morning+evening+1.4*np.sin(t*1.4)+rng.normal(0, .6, len(t)), 2, None)
    return t, pv, load


def simulate(pv_kw, load_kw, initial_soc, mode='fig3_fis', plant=Plant(),
             controller=None, width=None):
    """Grid balances load-PV-battery; positive battery output is discharge."""
    controller = controller or MamdaniEMS()
    pv_kw = np.asarray(pv_kw, dtype=float)
    load_kw = np.asarray(load_kw, dtype=float)
    if (pv_kw.shape != load_kw.shape or pv_kw.ndim != 1 or
        not np.all(np.isfinite(pv_kw)) or not np.all(np.isfinite(load_kw)) or
        (pv_kw < 0).any() or (load_kw < 0).any()):
        raise ValueError('Invalid PV/load series')
    if not 0 <= initial_soc <= 100:
        raise ValueError('Initial SOC must be 0..100')
    if not (plant.capacity_kwh > 0 and plant.power_limit_kw > 0 and
            plant.dt_hours > 0 and 0 < plant.efficiency_charge <= 1 and
            0 < plant.efficiency_discharge <= 1):
        raise ValueError('Bad plant')
    soc = float(initial_soc)
    rows = []
    for i, (pv, load) in enumerate(zip(pv_kw, load_kw)):
        delta = float(load-pv)
        cmd = controller.from_power(float(pv), float(load), soc, mode, width)
        requested_kw = float(cmd*min(abs(delta), plant.power_limit_kw))
        # A battery cannot charge from a deficit or discharge into a surplus
        # in this deliberately simple grid-following model.
        if abs(delta) < 1.e-12 or np.sign(requested_kw) != np.sign(delta):
            requested_kw = 0.0
        before = soc
        if requested_kw >= 0:  # discharge
            dsoc = -requested_kw*plant.dt_hours / (plant.efficiency_discharge*plant.capacity_kwh)*100
        else:  # charge
            dsoc = -requested_kw*plant.dt_hours*plant.efficiency_charge/plant.capacity_kwh*100
        soc = float(np.clip(before+dsoc, 0, 100))
        # Recompute actual battery-to-bus power after physical SOC clipping.
        battery_kw = (before-soc)*plant.capacity_kwh/(100*plant.dt_hours)
        battery_kw *= plant.efficiency_discharge if requested_kw >= 0 else 1/plant.efficiency_charge
        grid_kw = float(load-pv-battery_kw)
        rows.append({
            'step': i, 'hour': i*plant.dt_hours,
            'pv_kw': float(pv), 'load_kw': float(load),
            'soc_before': before, 'soc_after': soc, 'command': float(cmd),
            'battery_kw': float(battery_kw), 'grid_kw': grid_kw,
            'unsafe_low_discharge': int(before <= 20 and battery_kw > 1.e-9),
            'unsafe_high_charge': int(before >= 80 and battery_kw < -1.e-9),
            'outside_safe_band': int(soc < 20-1.e-9 or soc > 80+1.e-9),
            'energy_residual_kw': float(pv+battery_kw+grid_kw-load),
        })
    return rows
