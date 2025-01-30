# %%
"""
    Test implementation of DataProcessor (eventually)
"""

from pathlib import Path
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import time, sys
import regex as re

current_dir = Path(".")
script_filename = Path(__file__).stem

dataset_path = Path(r"/Users/jlr7/Documents/fastqi_resonatordata/11_21_1251AM/raw_csvs/Res0_5863MHz")
parsed_dataset_path = dataset_path.parent / f"{dataset_path.name}_parsed"

# %%
sys.path.append(r"/Users/jlr7/Library/CloudStorage/OneDrive-UCB-O365/GitHub")
import bcqt_hub

# %%

all_datasets = [x for x in dataset_path.glob("*.csv") if "_parsed" not in str(x)]
all_datasets =  list(sorted(all_datasets))

sorted_dataset = []
for csv_file in all_datasets:
    filename, filepath = csv_file.name, csv_file.parent
    sorted_dataset.append(new_filepath)
    
final_dataset = list(sorted(sorted_dataset))
print(f"{len(final_dataset)} csv files in {dataset_path.name}")
msmt_num = int(re.search(r"Msmt\d{1,6}", filename).captures()[0].replace("Msmt",""))


# %% read all csvs and parse info from filename and csv contents
from bcqt_hub.bcqt_hub.modules.DataHandler import DataSet, DataHandler
import bcqt_hub.experiments.quick_helpers as qh

parsed_dataset_path.mkdir(exist_ok=True)

all_dsets = []
for csv_filepath in all_datasets:
    csv_filename = csv_filepath.stem
    
    # lazy lazy lazy
    set_str, msmt_str, _, span_str, _, power_str, avgs, _ = csv_filename.split("_")
    msmt_num = int(re.search(r"\d{1,6}", msmt_str)[0])
    msmt_num = f"{int(msmt_num):05.0f}"
    set_msmt = f"{set_str}-Msmt{msmt_num}"
    
    new_filename = f"{set_msmt}_span_{span_str}_power_{power_str}_{avgs}_avgs.csv"
    new_filepath = parsed_dataset_path / new_filename
    
    df = pd.read_csv(csv_filepath, index_col=0)
    
    basic_configs = {
        "filename" : csv_filename,
        "filepath" : csv_filepath.parent,
        "power" : int(power_str.replace("dBm","")),
        "span" : int(span_str.replace("kHz",""))*1e3,
        "set_num" : int(set_str[-1]),
        "msmt_num" : msmt_num,
        "avgs" : int(avgs),
        # "dstr" : datetime.fromisoformat(df.iloc[0,0]).strftime("%m_%d_%H%M"),
        # "timestamp" : datetime.fromisoformat(df.iloc[0,0]),
    }
    
    
    if csv_filepath.exists() is False:
        print(f"~~~Saving parsed csv for {set_str}-{msmt_num}")
        df.to_csv(new_filepath)
        
    # all_dfs[set_msmt] = {"df" : df, "configs" : basic_configs}
    
    csv_dataset = DataSet(df, expt_name="FastQi_Tracking", dataset_label=set_msmt, units="S21", configs=basic_configs)
    all_dsets.append(csv_dataset)
    
    
    



make_plots = False

    
# %% run analysis with scresonators
from bcqt_hub.bcqt_hub.modules.DataAnalysis import DataAnalysis
    
# window_size = len(all_dsets)//1000
window_size = 15*2
full_windows = range(len(all_dsets)//window_size + 1)
all_idxes = [x*window_size for x in full_windows]
all_idxes.append(len(all_dsets))

all_analyses, all_param_dicts = [], []
for idx in range(len(all_idxes)-1):
    start, end = all_idxes[idx], all_idxes[idx+1]-1
    # print(idx, start, end)
    
    
    label = f"idx -> {start}:{end}"
    
    
    # start by averaging all measurements in the window together
    dsets_in_window = [x for x in all_dsets[start:end]]
    window_dfs = [x.data for x in dsets_in_window]
    
    example_dset = dsets_in_window[0]
    
    # skip if window is too small
    if len(dsets_in_window) < window_size*0.75:
        continue
    
    freqs = dsets_in_window[0].data["Frequency"]
    all_ampls = [df["S21 magn_dB"].values for df in window_dfs]
    all_phases = [df["S21 phase_rad"].values for df in window_dfs]
    
    averaged_ampls = np.average(all_ampls, axis=0)
    averaged_phases = np.average(all_phases, axis=0)
    
    averaged_df = pd.DataFrame({"Frequency":freqs, "S21 magn_dB":averaged_ampls, "S21 phase_rad":averaged_phases})

    Res_Analysis = DataAnalysis(averaged_df)

    if make_plots is True:
        qh.plot_s2p_df(averaged_df)
    
    
    #               [Q, Qc, w1, phi]
    # init_params = [2.68e5, 1e6, 5.86325424e9, 0.028]
    init_params = None
    
    params, conf_intervals, err, init1, fig = Res_Analysis.fit_single_res(data_df=averaged_df, save_dcm_plot=False, plot_title=label, manual_init=init_params)

    # plt.show()
    
    power = example_dset.configs["power"]
    
    Q, Qc, f_center, phi = params
    Q_err, Qi_err, Qc_err, Qc_Re_err, phi_err, f_center_err = conf_intervals
    
    Qi = 1/(1/Q - np.cos(phi)/np.abs(Qc))
    
    params = [Q, Qi, Qc, f_center, phi]
    
    parameters_dict = {
        "power" : power,
        "Q" : Q,
        "Q_err" : Q_err,
        "Qi" : Qi,
        "Qi_err" : Qi_err,
        "Qc" : Qc,
        "Qc_err" : Qc_err,
        "f_center" : f_center,
        "f_center_err" : f_center_err,
        "phi" : phi,
        "phi_err" : phi_err,
        "Analysis" : Res_Analysis,
    }

    perc_errs = {
        "Q_perc" : Q_err / Q,
        "Qi_perc" : Qi_err / Qi,
        "Qc_perc" : Qc_err / Qc,
    }
    
    skip_value = False
    for err in perc_errs.values():
        if err >= 0.50 or err == 0.0:
            skip_value = True
            print(f"Skipping {label}  ({idx}/{len(all_idxes)})")
    
    if skip_value == True:
        continue
    
    Res_Analysis.configs = example_dset.configs
    Res_Analysis.parameters_dict = parameters_dict
    Res_Analysis.perc_errs = perc_errs
    
    all_analyses.append(Res_Analysis)
    all_param_dicts.append(parameters_dict)
    
    
# %% get all fit results and organize into a single 

    
for ResAnalysis in all_analyses:
    
    df = ResAnalysis.data
    configs = ResAnalysis.configs
    parameters_dict = ResAnalysis.parameters_dict
    perc_errs = ResAnalysis.perc_errs
    
    df_fit_results = pd.DataFrame(all_param_dicts)
    df_fit_results.drop("phi_err", axis="columns", inplace=True)  


n_pows = df_fit_results["power"].nunique()
powers = df_fit_results["power"].unique()
make_plots = True
# for param in ["Q", "Qi", "Qc"]:
for param in ["Qi"]:
    
    if make_plots is True:
        fig, axes = plt.subplots(n_pows, 1, figsize=(15, 3*n_pows))
        
        # handle case where we have single plot
        if type(axes) != np.ndarray:
            fig.set_figheight(10)
            axes = [axes]
            
        for ax, power in zip(axes, powers):
            threshold_percentage = 7
            matching_powers = df_fit_results.loc[ df_fit_results["power"] == power]
            
            analysis = matching_powers["Analysis"][0]
            dataset = matching_powers[param]
            dataset_err = matching_powers[f"{param}_err"]
            xvals = range(len(dataset))
            
            avg, std = np.average(dataset), np.std(dataset)
            
            failed_points = []
            added, popped = 0, 0
            for x, pt, pt_err in zip(xvals, dataset, dataset_err):
                perc_err = pt_err/pt * 100
                
                if pt >= avg*(1.5) or pt <= avg*(0.5):
                    print(f"\nRemoved idx={x}, {param} = {pt:1.1e} +/- {perc_err:1.1e} ({perc_err=:1.2f}%) \nupdating avg & stdev\n   from:   {avg:1.1e} / {std:1.1e}")
                    dataset.pop(x)
                    avg, std = np.average(dataset), np.std(dataset)
                    print(f"     to:   {avg:1.1e} / {std:1.1e}")
                    popped += 1
                    continue
                
                if perc_err > threshold_percentage:
                    info_str = f"idx{x}, {power=}: {param}={pt:1.1f} +/- {pt_err:1.1f}  ({perc_err=:1.1f}% > {threshold_percentage=}%)"
                    failed_points.append((x, pt, pt_err, info_str))
                    pt_color = 'r' 
                else:
                    pt_color = 'b'
                
                ax.errorbar(x=x, y=pt, yerr=pt_err, color=pt_color, markersize=6, capsize=3)
                added += 1
                ax.plot(x, pt, 'o', markersize=6, color=pt_color)
                
            ax.axhline(avg, linestyle='--', linewidth=1, color='k', label=f"Average {param} = {avg:1.1e}")
            
            ax.set_title(f"Power = {power} dBm")
            # ax.set_yscale("log")
            
            ax.set_xlabel("idx")
            ax.set_ylabel(f"{param} Values")
            ax.legend()

            display(f"[{power = }] Failed Points: ")
            for (x, pt, pt_err, info_str) in failed_points:
                print(info_str)
                
            title_str = f"Tracking {param} values over time" + \
                        f"\n{window_size} traces * {analysis.configs["avgs"]} avgs per point" + \
                        f"\n{len(failed_points)} failures to reach {threshold_percentage}% max uncertainty for {len(df_fit_results) - popped} points"
            fig.suptitle(title_str, size=18)
            fig.tight_layout()
            
            
        plt.show()

# %%

from matplotlib import colors
from matplotlib.ticker import PercentFormatter

all_qi_perc_errors = [x for x in df_fit_results["Qi_err"]/df_fit_results["Qi"]]
n_bins = 20

fig, axes = plt.subplots(1,1, figsize=(6,6))
axes = [axes]

N, bins, patches = axes[0].hist(all_qi_perc_errors, bins=n_bins, edgecolor='k')

# We'll color code by height, but you could use any scalar
fracs = N / N.max()
norm = colors.Normalize(0, 0)

# Now, we'll loop through our objects and set the color of each accordingly
for thisfrac, thispatch in zip(fracs, patches):
    color = plt.cm.summer(norm(thisfrac))
    thispatch.set_facecolor(color)
    thispatch

axes[0].xaxis.set_major_formatter(PercentFormatter(xmax=1))
axes[0].set_title("Histogram of uncertainty\n threshold counts")
    



# %%
