# %%
"""
    Test implementation of VNA driver
"""

from pathlib import Path
from datetime import datetime
import sys
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

current_dir = Path(".")
script_filename = Path(__file__).stem

sys.path.append(r"C:\Users\Lehnert Lab\GitHub")

from bcqt_hub.src.modules.DataAnalysis import DataAnalysis
import bcqt_hub.experiments.quick_helpers as qh

from bcqt_hub.src.drivers.instruments.VNA_Keysight import VNA_Keysight

# %% import VNA driver

### create dict to hold "default" configurations
VNA_Keysight_InstrConfig = {
    "instrument_name" : "VNA_Keysight",
    # "rm_backend" : "@py",
    "rm_backend" : None,
    "instr_address" : 'TCPIP0::192.168.0.105::inst0::INSTR',
    "edelay" : 70e-9,
    "averages" : 2,
    "sparam" : ['S11', 'S21'],  
    
    # "segment_type" : "linear",
    "segment_type" : "hybrid",
}

### create instrument driver from "VNA_Keysight" class, which inherits BaseDriver
PNA_X = VNA_Keysight(VNA_Keysight_InstrConfig, debug=True)  

    

# %%

all_freqs =  [ 
            4.363940e9,
            4.736490e9,
            5.106848e9,
            5.4742e9,
            5.8713e9,
            6.230608e9,
            6.624032e9,
            7.010540e9,
            ]

all_freqs = [4.363940e9]

all_powers = [-65, -70, -75, -80]  

Measurement_Configs = {
    "f_center" : all_freqs[0],
    "f_span" : 0.5e6,
    "n_points" : 5001,
    "if_bandwidth" : 15000,
    "power" : -30,
    "averages" : 10, # num avgs per power point measurement
    "sparam" : ['S21'],  
    "Noffres" : 8,
}


# %% 

dstr = datetime.today().strftime("%m_%d_%I%M%p")

if "all_dfs" not in locals().keys():
    all_resonator_data = {}

for idx, freq in enumerate(all_freqs):  # loop over all resonators
    freq_str = f"{freq/1e9:1.3f}".replace('.',"p")
    Measurement_Configs["f_center"] = freq
    resonator_name = f"Res{idx}_{freq_str}"
    
    res_power_sweep_dict = {}
    
    for power in all_powers:  # for each resonator, loop over all powers
        
        """ 
            use VNA to take & download data
        """
        
        Measurement_Configs["power"] = power
        
        ### update configs
        PNA_X.update_configs(**Measurement_Configs)
        
        ### compute segments for freq sweep
        Measurement_Configs["segments"] = PNA_X.compute_homophasal_segments() 
        
        ### send cmds to vna
        PNA_X.setup_s2p_measurement()
        
        ### run measurement
        PNA_X.run_measurement() 
        
        ### download and plot data
        s2p_df = PNA_X.return_data_s2p()
        axes = qh.plot_s2p_df(s2p_df, plot_complex=True)

        ### save data
        save_dir = "./cooldown59/Line4_MQC_BOE_02"
        expt_category = dstr
        num_avgs = Measurement_Configs["averages"]
        meas_name = rf"VNA_{freq_str}_GHz_{power}_dBm_{num_avgs}_avgs"

        filename, filepath = qh.archive_data(PNA_X, s2p_df, meas_name=meas_name, expt_category=expt_category, all_axes=axes)

        
        """ 
            use scresonators to fit the data mid power-sweep
        """
        
        

# %% use scresonators to plot data
        
    #     ### analyze data
    #     Res_PowSweep_Analysis = DataAnalysis(None, dstr)
        
    #     print(f"Fitting {filename}")
        
    #     try:
    #         # output_params, conf_array, error, init, output_path
    #         params, conf_intervals, err, init1, fig = Res_PowSweep_Analysis.fit_single_res(data_df=s2p_df, save_dcm_plot=False, plot_title=filename, save_path=filepath)
    #     except Exception as e:
    #         print(f"Failed to plot DCM fit for {power} dBm -> {filename}")
    #         continue
        
    #     # 1/Q = 1/Qi + cos(phi)/|Qc|
    #     # 1/Qi = 1/Q - cos(phi)/|Qc|
    #     # Qi = 1/(1/Q - cos(phi)/|Qc|)
        
    #     Q, Qc, f_center, phi = params
    #     Q_err, Qi_err, Qc_err, Qc_Re_err, phi_err, f_center_err = conf_intervals
        
    #     Qi = 1/(1/Q - np.cos(phi)/np.abs(Qc))
        
    #     params = [Q, Qi, Qc, f_center, phi]
        
    #     fit_results = {
    #         "power" : power,
    #         "Q" : Q,
    #         "Q_err" : Q_err,
    #         "Q_perc" : Q_err / Q,
            
    #         "Qi" : Qi,
    #         "Qi_err" : Qi_err,
    #         "Qi_perc" : Qi_err / Qi,
            
    #         "Qc" : Qc,
    #         "Qc_err" : Qc_err,
    #         "Qc_perc" : Qc_err / Qc,
            
    #         "f_center" : f_center,
    #         "f_center_err" : f_center_err,
    #         "phi" : phi,
    #         "phi_err" : phi_err,
    #     }
        
    #     res_power_sweep_dict[filename] = (s2p_df, fit_results, Measurement_Configs)
    #     plt.show()
    
    # all_resonator_data[resonator_name] = res_power_sweep_dict
    
    

    

# %% run analysis with scresonators


# init_params = [None]*4
# processed_data = { key : {"df": df, 
#                           "Measurement_Configs" : {**Measurement_Configs,  
#                                            "init_params" : init_params, 
#                                            "time_end" : time_end},  # add init_params and timestamp to config
#                           } 
#                   for key, (df, Measurement_Configs, time_end) in all_dfs.items() }

# Res_PowSweep_Analysis = DataAnalysis(processed_data, dstr)

    
# fit_results = {}
# for key, processed_data_dict in processed_data.items():
#     df, Measurement_Configs = processed_data_dict.values()
    
#     print(f"Fitting {key}")
    
#     power = Measurement_Configs["power"]
#     time_end = Measurement_Configs["time_end"]
    
#     save_dcm_plot = True if power <= -70 else False
    
#     if save_dcm_plot is not True:
#         continue
    
#     # output_params, conf_array, error, init, output_path
#     params, conf_intervals, err, init1, fig = Res_PowSweep_Analysis.fit_single_res(data_df=df, save_dcm_plot=False, plot_title=key, save_path=dcm_path)

#     # 1/Q = 1/Qi + cos(phi)/|Qc|
#     # 1/Qi = 1/Q - cos(phi)/|Qc|
#     # Qi = 1/(1/Q - cos(phi)/|Qc|)
    
#     Q, Qc, f_center, phi = params
#     Q_err, Qi_err, Qc_err, Qc_Re_err, phi_err, f_center_err = conf_intervals
    
#     Qi = 1/(1/Q - np.cos(phi)/np.abs(Qc))
    
#     params = [Q, Qi, Qc, f_center, phi]
    
#     parameters_dict = {
#         "power" : power,
#         "Q" : Q,
#         "Q_err" : Q_err,
#         "Qi" : Qi,
#         "Qi_err" : Qi_err,
#         "Qc" : Qc,
#         "Qc_err" : Qc_err,
#         "f_center" : f_center,
#         "f_center_err" : f_center_err,
#         "phi" : phi,
#         "phi_err" : phi_err,
#     }

#     perc_errs = {
#         "Q_perc" : Q_err / Q,
#         "Qi_perc" : Qi_err / Qi,
#         "Qc_perc" : Qc_err / Qc,
#     }
    
#     fit_results[key] = (df, Measurement_Configs, parameters_dict, perc_errs)
    
#     plt.show()
        
    
# %%

all_param_dicts = {}
for key, (df, Measurement_Configs, parameters_dict, perc_errs) in fit_results.items():
    all_param_dicts[key] = parameters_dict
    
df_fit_results = pd.DataFrame.from_dict(all_param_dicts, orient="index").reset_index()
# df_fit_results.drop("phi_err", axis="columns", inplace=True)  


n_pows = df_fit_results["power"].nunique()
powers = df_fit_results["power"].unique()

# for param in ["Q", "Qi", "Qc"]:
    
#     fig, axes = plt.subplots(n_pows, 1, figsize=(10, 4*n_pows))
    
#     # handle case where we have single plot
#     if type(axes) != list:
#         fig.set_figheight(10)
#         axes = [axes]
        
#     for ax, power in zip(axes, powers):
        
#         threshold_percentage = 20
#         matching_powers = df_fit_results.loc[ df_fit_results["power"] == power]
        
#         # param = "Q"
#         dataset = matching_powers[param]
#         dataset_err = matching_powers[f"{param}_err"]
#         xvals = range(len(dataset))
        
#         avg, std = np.average(dataset), np.std(dataset)
        
#         failed_points = []
#         for x, pt, pt_err in zip(xvals, dataset, dataset_err):
#             perc_err = pt_err/pt * 100
            
#             if perc_err > threshold_percentage:
#                 info_str = f"idx{x}, {power=}: {param}={pt:1.1f} +/- {pt_err:1.1f}  ({perc_err=:1.1f}% > {threshold_percentage=}%)"
#                 failed_points.append((x, pt, pt_err, info_str))
#                 pt_color = 'r' 
#             else:
#                 pt_color = 'b'
                
#             ax.errorbar(x=x, y=pt, yerr=pt_err, color=pt_color, markersize=6, capsize=3)
        
#             ax.plot(x, pt, 'o', markersize=6, color=pt_color)
            
        
#         ax.axhline(avg, linestyle='--', linewidth=1, color='k', label=f"Average {param} = {avg:1.1e}")
        
#         ax.set_title(f"Power = {power} dBm")
#         # ax.set_yscale("log")
        
#         ax.set_xlabel("idx")
#         ax.set_ylabel(f"{param} Values")
#         ax.legend()


#         display(f"[{power = }] Failed Points: ")
#         for (x, pt, pt_err, info_str) in failed_points:
#             print(info_str)


#         fig.suptitle(f"Tracking {param} values over time, \n1 min/pt, \nthreshold = {threshold_percentage}% \n50 points per trace \n1 kHz IF_BW \n 1000 averages", size=18)
#         fig.tight_layout()
        
#     plt.show()

# %%
