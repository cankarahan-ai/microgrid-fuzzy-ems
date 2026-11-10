# Microgrid Fuzzy EMS — Mamdani FIS Reproduction & SOC-Aware Extension

**Bulanık Mantık Dönem Projesi** · İstanbul Üniversitesi-Cerrahpaşa · Bilgisayar Mühendisliği  
**Öğrenci:** Can Karahan · **Öğrenci numarası:** [TESLİM ÖNCESİ EKLENECEK]  
**Güncel sürüm:** 10 Kasım 2026 (nihai teslim öncesi kontrol sürümü)

## Original Paper

M. Nur-E-Alam et al., “Optimization of energy management in Malaysian microgrids using fuzzy logic-based EMS scheduling controller,” *Scientific Reports*, vol. 15, art. 995 (2025). https://doi.org/10.1038/s41598-024-82360-4

> **Scope and honesty:** This project independently implements the **Figure 3 two-input, one-output, nine-rule Mamdani FIS** in Python. It is **not** the full original MATLAB/Simulink PV–converter–MPPT–PI/THD simulation. Its 24-hour PV/load profiles and 50 kWh plant parameters are **synthetic assumptions**, not the source paper's Malaysian field measurements. Numerical values from Figure S6 cannot be reproduced exactly from the nine rules/triangles in Figure 3; this discrepancy is documented rather than hidden.

## Problem & Method

A microgrid combines PV generation, load demand, a battery, and the public grid. The fuzzy controller consumes:

- **balance**: normalized `clip((Pload - Ppv)/20 kW, -1, 1)`. Negative = PV surplus. The **20 kW** is our explicit normalization assumption.
- **SOC**: battery state of charge, 0–100%.
- **Output**: normalized `c/d` command in [−1,1], **negative charging**, **positive discharging**, zero hold.

Each variable uses three triangular membership functions, consistent with Figure 3 of the article: balance and output `(-2,-1,0)`, `(-1,0,1)`, `(0,1,2)`; SOC `(-50,0,50)`, `(0,50,100)`, `(50,100,150)`.

### Figure 3(d) nine fuzzy rules

| Balance / SOC | Low | Medium | High |
|---|---|---|---|
| PV &gt; Load | Charge | Charge | Hold |
| PV &lt; Load | Hold | Discharge | Discharge |
| PV = Load | Hold | Hold | Hold |

Mamdani: AND=`min`, implication=`min`, aggregation=`max`, defuzzification=`centroid` with 1001 integration samples.

## Reproduction and the paper's ambiguity

The article's **Figure 3(d)** permits charging a low-SOC battery when PV is abundant and discharging a high-SOC battery when load is high. The **prose**, however, describes *no charge or discharge outside 20–80% SOC*. The published numerical Figure S6 prose values of about `+0.00494 / -0.00494` at balance −1 and SOC 0 / 100 also differ from the literal Figure 3 rule transcription.

We do **not** call these identical. Three independently labelled modes make comparisons reproducible:

| Mode | Explanation |
|---|---|
| `fig3_fis` | Raw 9-rule Mamdani FIS from Figure 3 |
| `text_cutoff` | Simplified, **interpreted** article prose: no current at SOC≤20 or SOC≥80 |
| `proposed` | Same raw FIS plus our gradual direction-aware protection envelope |

For exact boundary checks, see `results/tables/paper_anchor_checks.csv`. These are **reference-consistency attempts**, not a claim of successful numerical reproduction of Figure S6.

## Original contribution

The new feature is **not the idea of SOC protection itself** (already present in the paper). It is an explicitly defined **direction-sensitive, smooth output envelope** that preserves recovery commands outside the SOC band:

- Discharge (`u > 0`): `g = clip((SOC - 20)/w, 0, 1)`.
- Charge (`u < 0`): `g = clip((80 - SOC)/w, 0, 1)`.
- Proposed output: `u_new = u × g`.
- Main experiment: `w = 10` SOC percentage points; ablation: `w = 5,10,15,20`.

Thus low SOC can still **charge** from PV surplus while it cannot **discharge**; high SOC can **discharge** to meet load while it cannot **charge**. This is a modeling choice requiring battery-vendor BMS validation in real deployment.

## Data / Experiment environment

All PV/load data in `src/simulator.py` are **synthetically generated**, deterministic from seeds `[2,7,14,42,101,2026]`. Initial SOC `[10,19,25,50,75,81,90]` produces 42 matched scenarios per method, 126 runs of 96 steps (15 minutes per step). **50 kWh** battery capacity, **8 kW** limit and **95%** charge/discharge efficiencies are illustrative assumptions; original article provides a 500 Ah battery, which cannot be treated as 50 kWh without voltage information.

Additional robustness experiment: 401 paired SOC readings per condition with measurement error N(0,1.5²) percentage points and four nominal boundary conditions. Ablation: four guard widths.

## How to run

Python 3.10+ and Python dependencies in `requirements.txt`.

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python demo.py --pv 15 --load 23 --soc 18
python demo.py --pv 23 --load 12 --soc 90
python -m experiments.run_experiments
python report/build_report.py
python presentation/build_presentation.py
```

Google Colab: open `experiments/Microgrid_Fuzzy_EMS_Colab.ipynb` **after the latest code has been pushed to GitHub**. The notebook clones the public repository, runs tests, the demo, and experiments.

## Experimental results

These are **actual local Python computations from the synthetic setup**, not original article metrics:

| Metric over 42 scenarios | Figure 3 FIS | Paper prose cutoff (interpretation) | Proposed |
|---|---:|---:|---:|
| Unsafe-direction time steps | 983 | 0 | 0 |
| SOC outside-band time steps | 1555 | 2808 | 856 |
| Mean grid import kWh/day | 159.5707 | 167.6894 | 161.1140 |
| Mean battery energy throughput kWh/day | 18.8077 | 7.3509 | 16.8473 |

“Unsafe-direction” means battery discharge while SOC≤20 or charge while SOC≥80, which is **guaranteed by definition** to be zero for the proposed filter and the hard-cutoff interpretation; it is not independent evidence of superiority over the original article. “Outside-band” includes scenarios that **start** outside 20–80%.

More robust evidence includes `measurement_noise.csv` and `parameter_ablation.csv` and accompanying `noise_robustness.png`. The smooth gate typically reduces abrupt controller-output changes vs hard cutoff but can change battery throughput and grid reliance. More complete scientific evidence requires real data and full Simulink integration.

### Generated artifacts

- `results/tables/summary.json`: complete measured output, input configuration, seeds, noise and ablation.
- `results/tables/experiment_metrics.csv`: 126 run-level rows.
- `results/tables/paper_anchor_checks.csv`: direct source figure/prose consistency checks.
- `results/tables/measurement_noise.csv`: paired measurement-noise runs.
- `results/tables/parameter_ablation.csv`: four soft guard widths.
- `results/tables/example_trajectories.csv`: selected time series.
- `results/figures/`: membership functions, three control surfaces, daily trajectory, robustness bars.
- `report/Teknik_Rapor_Microgrid_Fuzzy_EMS.pdf`: full technical report.
- `presentation/Microgrid_Fuzzy_EMS_Sunum.pptx` and `.pdf`: editable and export presentation.
- `docs/SAVUNMA_HAZIRLIK.md`: demonstration and oral defense.

## Limitations

1. No source Matlab `.fis` file, plant model, physical battery BMS, inverter, MPPT, PI or THD computation.
2. Figure 3 rules, article prose and Figure S6 numeric snapshots are not internally identical; this is disclosed.
3. No Malaysian field data; sensor variation and grid tariffs are not modelled physically.
4. An additional direction-aware guard is an empirical modelling extension, **not a demonstrated real-world optimal EMS**.
5. Sensor-noise and ablation findings are limited to selected synthetic cases.

## References (verified)

1. Nur-E-Alam et al. (2025), https://doi.org/10.1038/s41598-024-82360-4
2. Zadeh (1965), *Fuzzy Sets*, https://doi.org/10.1016/S0019-9958(65)90241-X
3. Mamdani & Assilian (1975), https://doi.org/10.1016/S0020-7373(75)80002-2
4. Arcos-Avilés et al., *IEEE Trans. Smart Grid*, https://doi.org/10.1109/TSG.2016.2555245
5. Rodriguez et al. (2023), https://doi.org/10.1016/j.apenergy.2023.120771
6. El Zerk & Ouassaid (2023), https://doi.org/10.3390/en16052244

## Generative AI Usage Disclosure

ChatGPT helped research/compare sources, draft and test code, run synthetic experiments, create plots, and draft the technical report and slides. The student should inspect code, re-run experiments, verify results, and be ready to explain them in the oral defense. This use is reported in the PDF under **Generative AI Usage Disclosure**.
