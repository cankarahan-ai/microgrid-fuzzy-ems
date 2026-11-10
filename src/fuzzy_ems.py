"""Transparent Python reproduction of the Figure 3 Mamdani FIS in Nur-E-Alam et al. (2025).

Reference: https://doi.org/10.1038/s41598-024-82360-4, Figure 3.
Three independently identified control modes are deliberately NOT conflated:
* fig3_fis: 9 IF-THEN rules from the published Figure 3(d), no postfilter;
* text_cutoff: literal interpretation of the paper's written no-current policy
               outside the 20-80% SOC band (ambiguous vs Figure 3 rules);
* proposed: original direction-aware 10%-wide soft boundary envelope.
This is a controller-subsystem approximation, not the original Simulink plant.
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
MODES = ('fig3_fis', 'text_cutoff', 'proposed')


def triangle(x, a, b, c):
    """Conventional triangular membership, including 'shoulder' at universe edge."""
    x = np.asarray(x, dtype=float)
    if not a < b < c:
        raise ValueError('Expected a < b < c')
    return np.maximum(0., np.minimum((x-a)/(b-a), (c-x)/(c-b)))


@dataclass(frozen=True)
class Config:
    normalization_kw: float = 20.0  # explicit project assumption
    points: int = 1001
    soc_min: float = 20.0
    soc_max: float = 80.0
    guard_width: float = 10.0  # new parameter; not from the original article


class MamdaniEMS:
    def __init__(self, cfg=Config()):
        if cfg.normalization_kw <= 0 or cfg.points < 101 or cfg.guard_width <= 0:
            raise ValueError('Bad model configuration')
        self.cfg = cfg
        self.output_x = np.linspace(-1, 1, cfg.points)
        self.output_mfs = {
            'charge': triangle(self.output_x, -2, -1, 0),
            'hold': triangle(self.output_x, -1, 0, 1),
            'discharge': triangle(self.output_x, 0, 1, 2),
        }

    @staticmethod
    def memberships(balance, soc):
        if not np.isfinite(balance) or not np.isfinite(soc):
            raise ValueError('Non-finite input')
        if not -1 <= balance <= 1 or not 0 <= soc <= 100:
            raise ValueError('Input outside universe')
        return ({
            'surplus': float(triangle(balance, -2, -1, 0)),
            'balanced': float(triangle(balance, -1, 0, 1)),
            'deficit': float(triangle(balance, 0, 1, 2)),
        }, {
            'low': float(triangle(soc, -50, 0, 50)),
            'medium': float(triangle(soc, 0, 50, 100)),
            'high': float(triangle(soc, 50, 100, 150)),
        })

    def infer(self, balance, soc, details=False):
        """Figure-3 FIS: min-AND, min-implication, max-aggregation, centroid."""
        power, soc_deg = self.memberships(balance, soc)
        aggregate = np.zeros_like(self.output_x)
        rules = []
        for (p, s), label in RULES.items():
            firing = min(power[p], soc_deg[s])
            rules.append({'condition': f'{p} & {s}', 'output': label,
                          'strength': float(firing)})
            aggregate = np.maximum(aggregate,
                                   np.minimum(firing, self.output_mfs[label]))
        area = float(np.trapezoid(aggregate, self.output_x))
        result = (float(np.trapezoid(aggregate*self.output_x, self.output_x)/area)
                  if area > 1.e-12 else 0.)
        if details:
            return {'action': result, 'power_memberships': power,
                    'soc_memberships': soc_deg, 'rules': rules}
        return result

    def text_cutoff(self, action, soc):
        """Simplified article-text interpretation, distinct from Figure 3 rule map.

        The prose reports no charge or discharge when SOC is below 20% or
        above 80%, although Figure 3(d) permits safe-direction recovery.
        We make this ambiguity visible rather than silently assert equivalence.
        """
        return 0.0 if soc <= self.cfg.soc_min or soc >= self.cfg.soc_max else float(action)

    def safety_extension(self, action, soc, width=None):
        """Our contribution: direction-specific gradual protection near SOC edges.

        It forbids discharge below 20 and charge above 80, but allows recovery
        charging at low SOC and recovery discharging at high SOC.
        """
        width = self.cfg.guard_width if width is None else width
        if width <= 0:
            raise ValueError('width must be positive')
        if action > 0:  # discharging
            factor = np.clip((soc-self.cfg.soc_min)/width, 0, 1)
        elif action < 0:  # charging
            factor = np.clip((self.cfg.soc_max-soc)/width, 0, 1)
        else:
            factor = 1.
        return float(action*factor)

    def control(self, balance, soc, mode='fig3_fis', width=None):
        if mode not in MODES:
            raise ValueError('Unknown mode')
        raw = self.infer(balance, soc)
        if mode == 'text_cutoff':
            return self.text_cutoff(raw, soc)
        if mode == 'proposed':
            return self.safety_extension(raw, soc, width)
        return raw

    def from_power(self, pv_kw, load_kw, soc, mode='fig3_fis', width=None):
        if not np.isfinite(pv_kw) or not np.isfinite(load_kw):
            raise ValueError('Non-finite power')
        if pv_kw < 0 or load_kw < 0:
            raise ValueError('Power must be nonnegative')
        balance = float(np.clip((load_kw-pv_kw)/self.cfg.normalization_kw, -1, 1))
        return self.control(balance, soc, mode, width)
