"""Regenerate independent numerical results: python -m experiments.run_experiments.

Three distinct comparators: Figure-3 FIS, literal article-text cutoff,
and new directional soft envelope. Synthetic experiments, no original site data.
"""
from pathlib import Path
import csv
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from src.fuzzy_ems import MamdaniEMS, RULES, MODES, triangle
from src.simulator import Plant, generate_day, simulate

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT/'results'/'figures'
TAB = ROOT/'results'/'tables'
FIG.mkdir(parents=True, exist_ok=True)
TAB.mkdir(parents=True, exist_ok=True)
SEEDS = [2, 7, 14, 42, 101, 2026]
INITIAL_SOC = [10, 19, 25, 50, 75, 81, 90]


def save_csv(path, rows):
    if not rows:
        return
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def metrics(trajectory, plant):
    return {
        'unsafe_direction_steps': sum(x['unsafe_low_discharge']+x['unsafe_high_charge'] for x in trajectory),
        'outside_band_steps': sum(x['outside_safe_band'] for x in trajectory),
        'grid_import_kwh': round(sum(max(x['grid_kw'],0)*plant.dt_hours for x in trajectory),5),
        'grid_export_kwh': round(sum(max(-x['grid_kw'],0)*plant.dt_hours for x in trajectory),5),
        'battery_throughput_kwh': round(sum(abs(x['battery_kw'])*plant.dt_hours for x in trajectory),5),
        'final_soc': round(trajectory[-1]['soc_after'],5),
        'energy_balance_max_abs_kw': max(abs(x['energy_residual_kw']) for x in trajectory),
    }


def source_checks(ems):
    # Figure 3 rule-viewer test. The two source paper prose values ~ +/-0.00494
    # conflict with Figure 3(d) for balance=-1, SOC=0. This is disclosed.
    combos = [(-1,0),(-1,100),(0,50),(1,0),(1,100),(-1,50),(1,50)]
    source_values = {(-1,0): .00494, (-1,100): -.00494}
    out=[]
    for balance,soc in combos:
        raw = ems.control(balance, soc, 'fig3_fis')
        article = source_values.get((balance,soc))
        out.append({
            'balance':balance,'soc':soc,
            'figure3_python_command':round(raw,6),
            'text_cutoff_command':round(ems.control(balance,soc,'text_cutoff'),6),
            'proposed_command':round(ems.control(balance,soc,'proposed'),6),
            'paper_S6_prose_reported': '' if article is None else article,
            'figure3_vs_reported_abs_difference': '' if article is None else round(abs(raw-article),6),
            'note': 'Reported S6 numeric mismatch with Figure 3(d) reconstruction' if article is not None else 'Figure 3 consistency check'
        })
    save_csv(TAB/'paper_anchor_checks.csv', out)
    return out


def make_memberships():
    x=np.linspace(-1,1,201);s=np.linspace(0,100,201)
    sets=[('Balance, normalized',x,[('PV surplus',-2,-1,0),('Balanced',-1,0,1),('Load surplus',0,1,2)]),
          ('Battery SOC (%)',s,[('Low',-50,0,50),('Medium',0,50,100),('High',50,100,150)]),
          ('Battery command: -charge, +discharge',x,[('Charge',-2,-1,0),('Hold',-1,0,1),('Discharge',0,1,2)])]
    fig,axes=plt.subplots(1,3,figsize=(13.2,3.8))
    for ax,(title,xx,curves) in zip(axes,sets):
        for name,a,b,c in curves:
            ax.plot(xx,triangle(xx,a,b,c),label=name)
        ax.set(title=title,xlabel='Input or output scale',ylabel='Membership',ylim=(-.05,1.05))
        ax.grid(alpha=.18);ax.legend(fontsize=8)
    fig.suptitle('Figure 3 membership functions — independent Python reconstruction',fontsize=13)
    fig.tight_layout();fig.savefig(FIG/'membership_functions.png',dpi=170);plt.close(fig)


def make_surface(ems):
    balances=np.linspace(-1,1,81); socs=np.linspace(0,100,81)
    raw=np.array([[ems.infer(float(b),float(s)) for b in balances] for s in socs])
    hard=np.array([[ems.text_cutoff(raw[i,j],float(s)) for j in range(len(balances))] for i,s in enumerate(socs)])
    proposed=np.array([[ems.safety_extension(raw[i,j],float(s)) for j in range(len(balances))] for i,s in enumerate(socs)])
    fig,axes=plt.subplots(1,3,figsize=(14,4.5),sharey=True)
    for ax,z,title in zip(axes,[raw,hard,proposed],['Figure 3 FIS','Paper prose cutoff (interpretation)','Proposed smooth directional gate']):
        im=ax.imshow(z,origin='lower',aspect='auto',extent=[-1,1,0,100],cmap='coolwarm',vmin=-.7,vmax=.7)
        for lim in (20,80): ax.axhline(lim,color='black',lw=.65,ls='--')
        ax.set(xlabel='Normalized demand - supply',title=title)
    axes[0].set_ylabel('Battery SOC (%)');fig.colorbar(im,ax=axes.ravel().tolist(),shrink=.78,label='Command: -charge / +discharge')
    fig.savefig(FIG/'controller_surface_comparison.png',dpi=160,bbox_inches='tight');plt.close(fig)


def make_day(trajectories):
    key=(42,25);k=trajectories[key]
    ref=k['fig3_fis'];t=[r['hour'] for r in ref]
    fig,axes=plt.subplots(3,1,figsize=(11.5,8.5),sharex=True)
    axes[0].plot(t,[r['pv_kw'] for r in ref],label='PV kW')
    axes[0].plot(t,[r['load_kw'] for r in ref],label='Load kW')
    for method,label in [('fig3_fis','Fig3 FIS'),('text_cutoff','Paper cutoff'),('proposed','Proposed')]:
        axes[1].plot(t,[r['soc_after'] for r in k[method]],label=label)
        axes[2].plot(t,[r['battery_kw'] for r in k[method]],label=label)
    axes[0].set_ylabel('kW');axes[1].set_ylabel('SOC (%)');axes[2].set_ylabel('Battery kW')
    for ax in axes: ax.legend(fontsize=9);ax.grid(alpha=.2)
    for limit in (20,80): axes[1].axhline(limit,color='gray',ls='--')
    axes[-1].set_xlabel('Hour of a synthetic day')
    fig.suptitle('Seed 42, initial SOC 25% — matched synthetic input profiles')
    fig.tight_layout();fig.savefig(FIG/'daily_trajectory.png',dpi=170);plt.close(fig)


def noise_experiment(ems):
    """Controlled measurement-noise experiment using same draws for all modes."""
    rows=[];rng=np.random.default_rng(20261110)
    for (balance,true_soc) in [(1,20),(-1,80),(1,22),(-1,78)]:
        measured=np.clip(true_soc+rng.normal(0,1.5,401),0,100)
        for mode in MODES:
            commands=np.array([ems.control(balance,float(s),mode) for s in measured])
            rows.append({'normalized_balance':balance,'true_soc':true_soc,'mode':mode,
                         'samples':len(commands),'noise_sigma_soc_points':1.5,
                         'command_mean':round(float(commands.mean()),6),
                         'command_std':round(float(commands.std()),6),
                         'mean_abs_step_change':round(float(np.abs(np.diff(commands)).mean()),6),
                         'total_variation':round(float(np.abs(np.diff(commands)).sum()),6)})
    save_csv(TAB/'measurement_noise.csv',rows)
    fig,axes=plt.subplots(1,2,figsize=(11.2,3.7))
    for ax,(balance,soc) in zip(axes,[(1,20),(-1,80)]):
        for mode in MODES:
            a=next(z for z in rows if z['normalized_balance']==balance and z['true_soc']==soc and z['mode']==mode)
            ax.bar(mode,a['mean_abs_step_change'],label=mode)
        ax.set_title(f'Balance {balance:+.0f} | actual SOC {soc}%')
        ax.set_ylabel('Mean absolute command step change');ax.tick_params(axis='x',labelrotation=18)
    fig.suptitle('Measurement noise response, 401 samples, Gaussian SOC noise σ=1.5')
    fig.tight_layout();fig.savefig(FIG/'noise_robustness.png',dpi=170);plt.close(fig)
    return rows


def main():
    ems=MamdaniEMS();plant=Plant();checks=source_checks(ems)
    scenarios=[];trajectory_rows=[];trajectories={}
    for seed in SEEDS:
        _,pv,load=generate_day(seed,plant.dt_hours)
        for initial in INITIAL_SOC:
            key=(seed,initial);trajectories[key]={}
            for mode in MODES:
                trajectory=simulate(pv,load,initial,mode,plant,ems)
                trajectories[key][mode]=trajectory
                scenarios.append({'seed':seed,'initial_soc':initial,'mode':mode,**metrics(trajectory,plant)})
                if key in [(42,25),(42,10),(42,90)]:
                    trajectory_rows.extend([{'seed':seed,'initial_soc':initial,'mode':mode,**row} for row in trajectory])
    save_csv(TAB/'experiment_metrics.csv',scenarios)
    save_csv(TAB/'example_trajectories.csv',trajectory_rows)
    summary={}
    for mode in MODES:
        subset=[row for row in scenarios if row['mode']==mode]
        summary[mode]={
            'scenarios':len(subset),
            'unsafe_direction_steps_total':sum(z['unsafe_direction_steps'] for z in subset),
            'outside_band_steps_total':sum(z['outside_band_steps'] for z in subset),
            'mean_grid_import_kwh':round(float(np.mean([z['grid_import_kwh'] for z in subset])),4),
            'mean_grid_export_kwh':round(float(np.mean([z['grid_export_kwh'] for z in subset])),4),
            'mean_battery_throughput_kwh':round(float(np.mean([z['battery_throughput_kwh'] for z in subset])),4),
            'mean_final_soc':round(float(np.mean([z['final_soc'] for z in subset])),4),
        }
    make_memberships();make_surface(ems);make_day(trajectories)
    noise=noise_experiment(ems)
    widths=[]
    for width in (5,10,15,20):
        selected=[]
        for seed in SEEDS:
            _,pv,load=generate_day(seed,plant.dt_hours)
            for soc in INITIAL_SOC:
                selected.append(metrics(simulate(pv,load,soc,'proposed',plant,ems,width),plant))
        widths.append({'guard_width_soc_points':width,
                       'unsafe_direction_steps_total':sum(z['unsafe_direction_steps'] for z in selected),
                       'outside_band_steps_total':sum(z['outside_band_steps'] for z in selected),
                       'mean_grid_import_kwh':round(float(np.mean([z['grid_import_kwh'] for z in selected])),4),
                       'mean_battery_throughput_kwh':round(float(np.mean([z['battery_throughput_kwh'] for z in selected])),4)})
    save_csv(TAB/'parameter_ablation.csv',widths)
    summary_blob={
        'reference':'Nur-E-Alam et al. Scientific Reports 15:995 (2025), Figure 3 / Fig S6 prose',
        'paper_numeric_mismatch':'Reconstructed Fig3 rule base does not match Fig S6 prose numerical snapshots; see paper_anchor_checks.csv',
        'data':'Synthetic deterministic PV and load, NOT the Malaysian site data',
        'plant_assumptions':plant.__dict__, 'controller_assumptions':ems.cfg.__dict__,
        'random_seeds':SEEDS,'initial_soc':INITIAL_SOC,'modes':summary,
        'noise_experiment':noise,'guard_width_ablation':widths,
    }
    (TAB/'summary.json').write_text(json.dumps(summary_blob,ensure_ascii=False,indent=2),encoding='utf-8')
    assert len(scenarios)==3*42
    assert max(z['energy_balance_max_abs_kw'] for z in scenarios)<1.e-7
    print(json.dumps(summary,ensure_ascii=False,indent=2))
    print('Source check:',checks[:2]); print('Width ablation:',widths)
    print('Finished 126 matched 24-h runs; 401-sample noise experiments; 4 guard widths.')

if __name__=='__main__': main()
