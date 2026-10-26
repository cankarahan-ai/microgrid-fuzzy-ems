# Fuzzy Logic-Based Energy Management in Microgrids

**Status:** Project setup and literature review — no implementation or experimental results yet.

## Reference paper
Nur-E-Alam et al., **"Optimization of energy management in Malaysian microgrids using fuzzy logic-based EMS scheduling controller,"** *Scientific Reports*, vol. 15, article 995, 2025.

- Paper: https://www.nature.com/articles/s41598-024-82360-4
- DOI: https://doi.org/10.1038/s41598-024-82360-4

## Problem and motivation
This project studies a fuzzy logic controller used to manage charging and discharging of a microgrid battery, taking into account photovoltaic (PV) production and electrical load.

## Original fuzzy controller — confirmed from the paper
- Fuzzy inference approach: **Mamdani FIS**.
- Input 1: **Power balance**, i.e. PV generation compared with load demand.
- Input 2: **Battery state of charge (SOC)**.
- Output: **Battery charge/discharge current** (positive: discharge; negative: charge; approximately zero: no action).
- Membership function family: **triangular**.
- Number of fuzzy rules shown by the paper: **9**.
- Battery protection conditions discussed: avoid charging and discharging outside the **20%–80% SOC** operating boundaries.

**Important:** Exact membership-function vertices, numerical input/output ranges, the complete rule table and reproducibility details must be checked against Fig. 3 and the supplementary materials before coding. Do not claim a faithful reproduction until that is done.

## Planned project scope (proposed, not yet validated)
1. Reproduce the **fuzzy controller sub-system** in Python (e.g. Google Colab).
2. Test the baseline under multiple power-balance and SOC scenarios.
3. Propose a small, technically justified extension (e.g. alter membership functions or rule base).
4. Run controlled comparisons and generate genuine plots/tables.
5. Prepare an 8–12 page technical report and classroom presentation.

The instructor must confirm that this controller-only reproduction satisfies the **minimum reproduction requirement (MRR)**; a whole MATLAB/Simulink electrical microgrid is **not** being claimed as implemented.

## Planned repository structure
- `docs/` — paper analysis and working notes
- `src/` — implementation (to be added)
- `experiments/baseline/` — baseline experiments (to be added)
- `experiments/proposed/` — extension experiments (to be added)
- `results/figures/`, `results/tables/` — verified outputs (to be added)
- `report/`, `presentation/` — final deliverables (to be added)
- `references/` — bibliography and references

## How to run
Not available yet. Instructions and dependencies will be added when an executable baseline exists.

## Data and results
No dataset or measurements are included at this stage. Results will only be added after execution and validation.

## Academic use of AI tools
Assistance from generative AI tools, if used, will be disclosed accurately in the final technical report under **Generative AI Usage Disclosure**. The submitted code and conclusions must be checked and understood by the student.

## Deadline
**16 November 2026**, per the updated Google Classroom assignment pages; the older guideline PDF lists an outdated due date.
