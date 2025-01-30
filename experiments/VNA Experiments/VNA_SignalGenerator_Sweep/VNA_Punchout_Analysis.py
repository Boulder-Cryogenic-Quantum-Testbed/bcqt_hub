# %%

from pathlib import Path
import pickle, time
import numpy as np
import matplotlib.pyplot as plt
 
# %%

all_data_folders = Path(f"data").glob("*")

data_folder = list(all_data_folders)[-1]
data_filepath = list(data_folder.glob("*.pk1"))[0]

with open(data_filepath, 'rb') as fp:
    all_punchout_results = pickle.load(fp)
    print(f'Pickle file loaded successfully to file from {data_filepath}')


# %%
# master plot for all power measurements of one resonator

global_key_list = list(all_punchout_results.keys())
global_powers_list = [list(x.keys()) for x in all_punchout_results.values()]

global_fit_dict = {}
global_powers, global_f_centers, global_f_center_errs, global_labels = [], [], [], []
for key, power_list in zip(global_key_list, global_powers_list):
    f_centers, f_center_errs, del_idxs = [], [], []
    for idx, power in enumerate(power_list):
        single_f_center = all_punchout_results[key][power]["fit_parameter_dict"]["f_center"]
        single_f_center_err = all_punchout_results[key][power]["fit_parameter_dict"]["f_center_err"]
        
        threshold = 100
        if single_f_center_err >= threshold*1e3:
            print(f"{key} - {power} dBm has error too high - ({single_f_center_err/1e3:1.2f} KHz > {threshold=} KHz !! ")
            time.sleep(0.2)
            del_idxs.append((idx, key, power))
            continue
        
        f_centers.append(single_f_center)
        f_center_errs.append(single_f_center_err)
        
        
    for (idx, key, power) in reversed(del_idxs):
        all_punchout_results[key].pop(power, None)
        power_list.pop(idx)
            
        
    
    global_fit_dict[key] = {"powers" : power_list, "f_centers" : f_centers, "f_center_errs" : f_center_errs}
    global_powers.append(power_list)
    global_f_centers.append(f_centers)
    global_f_center_errs.append(f_center_errs)
    global_labels.append(key)

for resonator_idx, (res_label, res_dict) in enumerate(all_punchout_results.items()):
    # mosaic = "AAACC\nAAACC\nBBBBB"
    # fig, axes = plt.subplot_mosaic(mosaic, figsize=(15, 12))
    # ax1, ax2, ax3 = axes["A"], axes["B"], axes["C"]
    
    fit_parameter_dict = [x["fit_parameter_dict"] for x in res_dict.values()]
    
    all_f_centers = np.array([fit_config["f_center"] for fit_config in fit_parameter_dict])/1e6
    all_f_center_errs = np.array([fit_config["f_center_err"] for fit_config in fit_parameter_dict])/1e3
    all_powers = np.array([fit_config["power"] for fit_config in fit_parameter_dict])
    
    min_error_idx = all_f_center_errs.argmin()
    
    fig, axes = plt.subplots(2, 1, figsize=(9,6))
    ax1, ax2 = axes
    
    # ax1.plot(all_powers, all_f_centers/1e6, 'r*', markersize=12)
    # ax2.plot(all_powers, all_f_center_errs/1e6, 'r*', markersize=12)
    
    for label, power_list, f_center_list, f_center_err_list in zip(global_labels, global_powers, global_f_centers, global_f_center_errs):
        f_center_list, f_center_err_list = np.array(f_center_list)/1e6, np.array(f_center_err_list)/1e3
        global_min_error_idx = f_center_err_list.argmin()
        
        # shorthand bool to check if the inner loop is on the same resonator as outer loop
        current_res = (res_label == label)  
        style = 'r*' if current_res else '.'
        alpha = 1.0 if current_res else 0.75
        capsize = 15 if current_res else 5
        msize = 12 if current_res else 10
        
        ax2.errorbar(x=power_list, y=100*abs(f_center_err_list - f_center_err_list[global_min_error_idx])/f_center_list, 
                     fmt=style[0:2], markersize=msize, label=label, alpha=alpha)
        ax1.errorbar(x=power_list, y=f_center_list, yerr=f_center_err_list, 
                     fmt=style, markersize=msize, alpha=alpha, capsize=capsize, mew=2)
    
    ax1.set_title("All $f_{res}$ where $f_{true}=f^{ \\ \\ lowest}_{error}$="+f'{all_f_centers[min_error_idx]:1.2f} MHz')
    ax1.set_ylabel("$f_{res}$ [MHz]", fontsize=14)
    ax2.set_title(r"$\delta f_{err}$ = fit errors in $f_{center}$")
    ax2.set_ylabel(r"$\delta f_{err}$ [% Percentage]", fontsize=14)
    ax2.set_xlabel("VNA Power [dBm]", fontsize=14)
    ax2.set_yscale("log")
    
    label = f'$f_{"{true}"}^{"{"}{f"({all_powers[min_error_idx]:1.0f}dBm)"}{"}"}$'+f'={all_f_centers[min_error_idx]:1.2f} MHz'
    ax1.axhline(all_f_centers[min_error_idx], linestyle='--', linewidth=1, color='k', label=label, alpha=0.9)
    # ax1.legend(loc="center left", bbox_to_anchor=(1.05, 0.9))

    fig.suptitle(f"{res_label} comparison to all fits", fontsize=16)    
    fig.tight_layout()
    
    ax2.legend(loc="center left", bbox_to_anchor=(1.05, 1.1))
    
    fig_filename = f"{label}_power_comparisons.png"
    fig_filepath = data_folder / fig_filename
    fig.savefig(fig_filepath)
    

    
# %%

for resonator_idx, (res_label, res_dict) in enumerate(all_punchout_results.items()):
    fig, axes = plt.subplots(2, 1)
    ax1, ax2 = axes
    
    all_f_res_fits = np.array([res_dict[power]["fit_parameter_dict"]["f_center"] for power in res_dict.keys()])
    all_f_res_errs = np.array([res_dict[power]["fit_parameter_dict"]["f_center_err"] for power in res_dict.keys()])
    
    
    min_error_idx = all_f_res_errs.argmin()
    f_res = all_f_res_fits[min_error_idx]
    
    for power, power_dict in res_dict.items():
        
        res_df, fit_parameter_dict, expt_config = power_dict.values()
        
        freqs, magn_dB, phase_rad = res_df["Frequency"], res_df["S21 magn_dB"], res_df["S21 phase_rad"]
        
        f_res_fit, f_res_fit_error = fit_parameter_dict["f_center"], fit_parameter_dict["f_center_err"]
        f_magn_min = freqs[magn_dB.argmin()]
        
        new_magn = magn_dB+10*power
        
        # plot S21 magn traces
        ax1.plot((freqs - f_res)/1e6, new_magn, "-", markersize=10, label=f"{power} dBm")
        ax1.axvline((f_magn_min - f_res)/1e6, linestyle='--', color='k', linewidth=0.5, alpha=0.5)
        
        # ax3.plot(freqs/1e9, magn_dB, "-", markersize=10, label=f"{power} dBm")
        
        # take minimum and compare to average
        ax2.plot(power, (f_res - f_magn_min)/1e3, '*', markersize=10,)
            
    ax1.set_title(f"All Power Measurements for f_res = {f_res/1e6:1.2f}")
    ax1.set_xlabel("Frequency deviation from lowest error $f_{res}$  [MHz]")
    ax1.set_ylabel("S21 Magn [dB]")
    ax1.axvline(f_res/1e6, linestyle='--', color='k', linewidth=1, alpha=0.8)

    # ax1.legend(loc="center left", bbox_to_anchor=(1.0, 0.5))

    ax2.set_title(f"All Power Measurements for f_res = {f_res/1e6:1.2f} MHz")
    ax2.set_xlabel("Power [dBm]")
    ax2.set_ylabel(r"$f_{res}$ deviation" + "\nfrom average \n[KHz]")

    ax2.axhline(0, linestyle='--', color='k', label=f"Average $f_{'{res}'}=$\n{f_res/1e6:1.2f} MHz")

    # ax2.legend(loc="upper center", bbox_to_anchor=(0.5, 1.0))

    label = f"Resonator{resonator_idx}_{f_res/1e6:1.0f}MHz"
    
    # take the maximum value of ax2 y-data, and then adjust top plot to zoom in
    # lower_xlim, upper_xlim = ax1.xaxis.get_data_interval()
    # avg_xlim = np.average([lower_xlim, upper_xlim])
    
    # left_bound = -1000
    # right_bound = 1000
    # ax1.set_xlim((left_bound, right_bound))
    
    ax1.set_xlim((-1, 1))

    ax1.grid()
    ax2.grid()
    # ax3.grid()
    
    fig.suptitle(res_label)
    fig.tight_layout()
    
    fig_filename = f"{label}_power_measurements.png"
    fig_filepath = data_folder / fig_filename
    fig.savefig(fig_filepath)
    
    plt.show()



# %%

# %%

