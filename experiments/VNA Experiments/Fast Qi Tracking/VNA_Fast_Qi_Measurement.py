# %%
"""

    Fast Qi Tracking via VNA

"""

# %%

from pathlib import Path
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import time, sys, os
import copy

os.chdir(r"C:\Users\Lehnert Lab\GitHub\bcqt_hub\experiments\VNA Experiments\Fast Qi Tracking")

dstr = datetime.today().strftime("%m_%d_%H%M")
current_dir = Path(".").absolute()
script_filename = Path(__file__).stem


# %% create folders and make path

data_path = current_dir / "data" / dstr
csv_path = data_path / "raw_csvs"
dcm_path = data_path / "dcm_fits"

all_paths = [current_dir, data_path, csv_path, dcm_path]

# make sure all paths exist, then append to $PATH
for path in all_paths:
    path = path.resolve()  # convert relative Path objs to absolutes
    print(f"Checking if path exists:  ['{path}']")
    print(f"     {str(path.exists()).upper()}")
    
    # ensure our data/fit storage paths exists
    if path.exists() is False and path in [csv_path.absolute(), data_path.absolute(), dcm_path.absolute()]:
        path.mkdir(parents=True, exist_ok=True)
        print(f"       ->  Created! Path now exists. [{path.exists() = }]")
    
    # sys.path.append(str(path))

# %%

sys.path.append(r"C:\\Users\\Lehnert Lab\\GitHub")
sys.path.append(r"C:\\Users\\Lehnert Lab\\GitHub\\drivers")
import bcqt_hub
import bcqt_hub.bcqt_hub.drivers

# %%
########################################################
########################################################
########################################################

from bcqt_hub.bcqt_hub.drivers.instruments.VNA_Keysight import VNA_Keysight

VNA_Keysight_InstrConfig = {
    "instrument_name" : "VNA_Keysight",
    "rm_backend" : None,
    "instr_address" : 'TCPIP0::192.168.0.105::inst0::INSTR',
    "power" : -80,
    "averages" : 10,
    "sparam" : ['S21'],
    "edelay" : 72.4,
    "f_center": 1e9,
    "f_span": 100e6,
    "segment_type" : "homophasal",

    "n_points" : 41,
    "Noffres" : 10,
    "if_bandwidth" : 500,
}

PNA_X = VNA_Keysight(VNA_Keysight_InstrConfig, debug=True)

all_dfs = {}
    
PNA_X.check_instr_error_queue()
PNA_X.filter_configs()
PNA_X.setup_s2p_measurement()

display(PNA_X.configs)
# %%
sys.path.append(r"C:\\Users\\Lehnert Lab\\GitHub\\bcqt_hub\\experiments")

from bcqt_hub.bcqt_hub.src.DataAnalysis import DataAnalysis
import bcqt_hub.experiments.quick_helpers as qh

#%%
all_f_centers = [
             # MQC_BOE_02
            #  4.363937e9,
            #  4.736494e9,
            #  5.106847e9,
            #  5.474224e9,
            #  5.871315e9,
            #  6.230610e9,  # very low Q
            #  6.624036e9,  # very low Q
            # 7.010525e9   # very low Q
            
            # MQC_BOE_SOLV1
        #    4.3389418e9,
           4.7333838e9,
        #    5.1108957e9,
        #    5.4838248e9,
        #    5.8733538e9,
        #    6.2299400e9,  # very low Q
        #    6.6206182e9,  # very low Q
        #    6.9972504e9   # very low Q
            ] 

# %%

Measurement_Configs = {
    "n_points" : 201,
    "power" : -75.75,
    "averages": 200,
    "if_bandwidth": 1e3,
    "f_span": 6e6,
    "err_threshold_perc": 1,
    "max_avg": 1000,
    "Noffres" : 10,
}


fit_results = {}
start_time = time.time()

for res_idx, resonator_freq in enumerate(all_f_centers):
    
    configs = copy.copy(Measurement_Configs)
    
    res_start_time = time.time()

    configs["f_center"] = resonator_freq
    
    """ 
        use VNA to take & download data
    """
        
    ### update configs
    PNA_X.update_configs(**configs)
    
    ### compute segments for freq sweep
    configs["segments"] = PNA_X.compute_homophasal_segments() 
    
    ### send cmds to vna
    PNA_X.setup_s2p_measurement()
    
    dfs_in_progess, perc_errs_in_progress = [], [100]
    meas_idx = 0
    Qi_err_perc = 100
    
    """
        - possible errors for the while loop
        
        - while loop goes on forever
            
            ### Qi_err doesn't go below err_threshold:
                
                -> even though the error is still decreasing
                    ** break loop if the change in Qi_err doesn't improve enough 
                        (e.g. starts to saturate at 2% while threshold is 1%)
                        
                -> Qi_err gets worse as we go on  (physically impossible... averaging always improves SNR!)
                    **break loop if change in Qi_err is positive
                
                -> scresonators fails to fit
                
                    <- if data is too noisy, try again with more averages
                        **if this does not fix the issue, repeat until a maximum number of averages
            
                    <- Qc was not fixed properly, so the fit failed
                        **skip to do maximum # of avgs, then leave it to human to check
                        
                    <- homophasal segments failed because it did not estimate Q properly
                        **skip to maximum # of avgs, then leave it to human to check
                    
                    <- if bw/span/num_pts/f_res is incorrect , then leave it up to human to fix
                        **skip to do maximum # of avgs, then leave it to human to check
            
            ### VNA is unresponsive
            
            ### code freezes, while loop never evaulated
            
            ### RF switch or cryoswitch is on wrong setting
            
            ### HEMT or TWPA are not turned on
            
            ### 
            
            
            
            
    """
    
    while (Qi_err_perc > configs["err_threshold_perc"]):
        
        print(f"Number of averages: {configs["averages"]}")
        
        ### run measurement
        PNA_X.run_measurement() 
        
        # get data from VNA and plot
        s2p_df = PNA_X.return_data_s2p()
        axes = qh.plot_s2p_df(s2p_df)
        
        # update plot
        title_str = str(f"{PNA_X.configs["f_span"]/1e6:1.2f}MHz_span_{PNA_X.configs["averages"]}_avgs_{PNA_X.configs["if_bandwidth"]}_IFBW_{PNA_X.configs["power"]}_dBm")
        fig = axes[0][0].get_figure()
        fig.suptitle(title_str, size=16)
        fig.tight_layout()
        plt.show()
        
        dfs_in_progess.append(s2p_df)
        
        # get parameters from measurement config
        n_points = configs["n_points"]
        power = configs["power"]
        
        resonator_freq, span, ifbw, avg, power = PNA_X.configs["f_center"], PNA_X.configs["f_span"], PNA_X.configs["if_bandwidth"], configs["averages"], PNA_X.configs["power"]
        freq_str = f"{resonator_freq/1e9:1.3f}".replace('.',"p")
        name = f"Meas{meas_idx}_ span_{span/1e3:1.0f}kHz_{freq_str}GHz_power_{power}dBm_{avg}_avgs"

        res_dir = csv_path / f"Res{res_idx}_{resonator_freq/1e6:1.0f}MHz"
        res_dir.mkdir(parents=True, exist_ok=True)
        filename = str(res_dir / f"{name}.csv")
        
        s2p_df.to_csv(filename)

        time_end = time.time()
        configs["time_end"] = time_end
        
        resonator_elapsed_time = time_end - res_start_time
        total_elapsed_time = time_end - start_time 
        print(f"Finished Measurement [{meas_idx}]! \nElapsed time: {resonator_elapsed_time/60:1.1f} minutes.\nTotal measurement resonator elapsed time: {total_elapsed_time/60:1.1f} minutes.")
        
        
        ######################
        all_dfs_concat = pd.concat(dfs_in_progess)
        current_df = all_dfs_concat.groupby(all_dfs_concat.index).mean()

        Res_PowSweep_Analysis = DataAnalysis(current_df, dstr)
            
        power = configs["power"]
        time_end = configs["time_end"]
        
        try:
        
            params, conf_intervals, err, init1, fig = Res_PowSweep_Analysis.fit_single_res(data_df=current_df, save_dcm_plot=False, plot_title=name, save_path=dcm_path)
        
        except Exception as e: 
            
            print(f"Error: {e}")
            
            configs["averages"] = configs["averages"] + 100
            
            if configs["averages"] > configs["max_avg"]:
                break
            
            continue
            
        
        # 1/Q = 1/Qi + cos(phi)/|Qc|
        # 1/Qi = 1/Q - cos(phi)/|Qc|
        # Qi = 1/(1/Q - cos(phi)/|Qc|)
        
        Q, Qc, f_center, phi = params["Q"], params["Qc"], params["w1"], params["phi"]
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
        }

        perc_errs = {
            "Q_perc" : Q_err / Q  * 100,
            "Qi_perc" : abs(Qi_err / Qi * 100),
            "Qc_perc" : Qc_err / Qc * 100,
        }
        
        
        perc_errs_in_progress.append(perc_errs["Qi_perc"])
        
        change_per_step = np.diff(perc_errs_in_progress)
        
        print(f"\n\n\n[Meas #{meas_idx}]\n       Qi_perc = {perc_errs["Qi_perc"]:1.3f}\n       {change_per_step[-1] = :1.3f} %\n\n\n")
        
        # if np.abs(change_per_step[0]) > 50:
        #     change_per_step = change_per_step[1:]
        
        time.sleep(1)
        
        # if we ever get worse (which shouldnt be possible unless fit breaks)
        #   or our improvement is less than 1%, then stop taking data
        
        # If fit fails, Qi_err = infinity
        if perc_errs["Qi_perc"] == np.inf:
            
            print(f"Qi_err = {perc_errs["Qi_perc"] = }")
            
            # redo fit with more averages until reaching maximum
            configs["averages"] = configs["averages"] + 50 
            if configs["averages"] > configs["max_avg"]:
                break
            
        # elif change_per_step[-1] >= 0:
        #     print(f"Error is increasing - {change_per_step[-1] = }")
        #     break
        
        elif abs(change_per_step[-1]) < 0.5:
            
            # if  perc_errs["Qi_perc"] > 5: 
            #     configs["averages"] = configs["averages"] + 50 
            #     if configs["averages"] > configs["max_avg"]:
            #         break
            # else:   
            #     print(f"Error is saturating - {change_per_step[-1] = }")
            #     break
            
            print(f"Error is saturating - {change_per_step[-1] = }")
            break
            
        else: 
            
            Qi_err_perc = perc_errs["Qi_perc"]

            fit_results[name] = (s2p_df, configs, parameters_dict, perc_errs)

            plt.show()
        
        meas_idx += 1
    
    
    fig, ax1 = plt.subplots(1,1, figsize=(12,7))
    change_per_step = [x for x in change_per_step if abs(x) < 50]
    
    ax1.set_title(r"All $\Delta Q_i^{err}$")
    ax1.set_xlabel("Measurement #")
    ax1.set_ylabel("Percentage Change in $Q_i^{err}$")
    ax1.grid()
    
    ax1.plot(change_per_step, 'rx', markersize=12)
    
    fig.savefig(filename.replace(".csv", "_Qi_Error_Plot.png"))
    
    all_dfs[title_str] = current_df
    

