# %%
"""
    Measure with the VNA set to zero span and the signal generator sweeping
    
    last update: 1/28/25
"""

# %load_ext autoreload
# %autoreload 2

# %%

from pathlib import Path
from datetime import datetime
import sys, time
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import pickle

dstr = datetime.today().strftime("%m_%d_%H%M")
current_dir = Path(".")
script_filename = Path(__file__).stem

sys.path.append(r"C:\Users\Lehnert Lab\GitHub\bcqt_hub\experiments")
import quick_helpers as qh

from bcqthub.src.DataAnalysis import DataAnalysis
import bcqthub.experiments.quick_helpers as qh
from bcqthub.drivers.instruments.VNA_Keysight import VNA_Keysight
from bcqthub.drivers.instruments.SG_Anritsu import SG_Anritsu


# %%

### create dict to hold "default" configurations
VNA_Keysight_InstrConfig = {
    "instrument_name" : "VNA_Keysight",
    # "rm_backend" : "@py",
    "rm_backend" : None,
    "instr_address" : 'TCPIP0::192.168.0.105::inst0::INSTR',
    'sparam' : ['S21'],
}

### create instrument driver from "VNA_Keysight" class, which inherits BaseDriver
PNA_X = VNA_Keysight(VNA_Keysight_InstrConfig, debug=True)  

#### read error queue 
PNA_X.check_instr_error_queue()


# %%
res_freqs = {
    1 : 6.29930e9,
    2 : 6.52210e9,
    3 : 6.70715e9,
    4 : 6.80295e9,
    5 : 6.87905e9,
    6 : 7.04815e9,
    7 : 7.21825e9
}

# %% now that we have the resonator frequencies...

# power_sweep = np.linspace(-30, -80, 10).round(2)
power_sweep = np.arange(-40, -81, -5).round(2)

Qubit_Punchout_Config = {
    # "segment_type" : "linear",
    "segment_type" : "hybrid",
    # "segment_type" : "homophasal",
    
    # "f_center" : f_res,  # set in loop
    # "power" : power,  # also set in loop
    "f_span" : 20e6,
        
    "n_points" : 201,
    "if_bandwidth" : 2000,
    # "averages" : averages,
    "edelay" : 75e-9,
    "plot_complex" : True
}
    
tstart = time.time()

averages_array = []
all_punchout_results = {}
for res_idx, f_res_estimate in res_freqs.items():
    tstart_res = time.time()
    
    # start f_res at the estimate, which was given either in the previous cell
    # or at the end of the previous power measurement
    f_res = f_res_estimate
    single_resonator_power_sweep, all_magn_mins = {}, {}
    for power_idx, power in enumerate(power_sweep):
        
        tstart_power = time.time()
        
        if power <= -80:
            avg = 600     # 87s
        elif power <= -70:
            avg = 400     # 58s
        elif power <= -60:
            avg = 200     # 30s
        elif power <= -50:
            avg = 50      # 8s
        elif power <= -40:
            avg = 50      # 5s
        
        averages_array.append(avg)
        Qubit_Punchout_Config["averages"] = avg
        
        display(f"Measuring Res #{res_idx} at {power:1.2f} dBm for {avg} averages")
        
        # park the VNA at the resonator frequency
        Qubit_Punchout_Config["f_center"] = f_res
        Qubit_Punchout_Config["power"] = power
        
        PNA_X.update_configs(**Qubit_Punchout_Config)
        
        if Qubit_Punchout_Config["segment_type"] != "linear":
            Qubit_Punchout_Config["segments"] = PNA_X.compute_homophasal_segments() 
        else:
            if "segments" in Qubit_Punchout_Config:
                del Qubit_Punchout_Config["segments"]
        
        f_span, n_points = Qubit_Punchout_Config["f_span"], Qubit_Punchout_Config["n_points"]
        
        PNA_X.update_configs(**Qubit_Punchout_Config)
        PNA_X.setup_s2p_measurement() 
        
        # freq_start, freq_stop, n_points = Qubit_Punchout_Config["f_start"], Qubit_Punchout_Config["f_stop"], Qubit_Punchout_Config["n_points"]
        freq_start, freq_stop = f_res - f_span/2, f_res + f_span/2
        
        PNA_X.run_measurement() 
        
        res_df = PNA_X.return_data_s2p()
        
        #### plotting ###
        if Qubit_Punchout_Config["plot_complex"] is False:
            fig, axes = plt.subplots(2, 1, figsize=(8,8))
            ax1, ax2 = axes
        else:
            mosaic = "AACCC\nBBCCC"
            fig, axes = plt.subplot_mosaic(mosaic, figsize=(12,8))
            ax1, ax2, ax3 = axes["A"], axes["B"], axes["C"]
        
        freqs, magn_dB, phase_rad = res_df["Frequency"], res_df["S21 magn_dB"], res_df["S21 phase_rad"]
        ax1.plot(freqs, magn_dB, ".", markersize=6, color='r')    
        ax2.plot(freqs, phase_rad, ".",  markersize=6, color='b')
        
        ax1.set_title("Magn vs Resonator Freq")
        ax2.set_title("Phase vs Resonator Freq")
        
        ax1.set_xlabel("Frequency [MHz]")
        ax2.set_xlabel("Frequency [MHz]")
        
        ax1.set_ylabel("VNA S21 [dB]")
        ax2.set_ylabel("VNA Phase [rad]")
        
        if Qubit_Punchout_Config["plot_complex"] is True:
            magn_lin = 10**(magn_dB/20)
            cmpl = magn_lin * np.exp(1j*phase_rad)
            real, imag = np.real(cmpl), np.imag(cmpl)
            
            ax3.set_title("Real vs Imag")
            ax3.set_xlabel("Real")
            ax3.set_ylabel("Imag")
            ax3.plot(real, imag, ".", markersize=10, color='g' )
        
        title_str = f"VNA Resonator Spectroscopy\n f_res = {f_res/1e9:1.3f} GHz\n RF Power = {power} dBm" 
        fig.suptitle(title_str)
        
        fig.tight_layout()
        plt.show()
        #### plotting ###

        # try to calculate res_freq of the resonator
        SingleFit = DataAnalysis(None, dstr)
        
        try:
            params, conf_intervals, err, init1, fig = SingleFit.fit_single_res(data_df=res_df, save_dcm_plot=False, plot_title=title_str)
        except Exception as e:
            print(f"Failed to plot DCM fit for {power} dBm")
            print(f"Error: {e}")
            continue
        
        Q, Qc, f_center, phi = params["Q"].value, params["Qc"].value, params["w1"].value, params["phi"].value
        Q_err, Qi_err, Qc_err, Qc_Re_err, phi_err, f_center_err = conf_intervals
        
        Qi = 1/(1/Q - np.cos(phi)/np.abs(Qc))
        
        params = [Q, Qi, Qc, f_center, phi]
        
        perc_errs = {
            "f_perc" : f_center_err / f_center, 
            "Q_perc" : Q_err / Q,
            "Qi_perc" : Qi_err / Qi,
            "Qc_perc" : Qc_err / Qc,
        }
        
        parameters_dict = {
            "power" : power,
            
            "Q" : Q,
            "Q_err" : Q_err,
            
            "Qi" : Qi,
            "Qi_err" : Qi_err,
            
            "Qc" : Qc, 
            "Qc_err" : Qc_err,
            
            "phi" : phi,
            "phi_err" : phi_err,
            
            "f_center" : f_center,
            "f_center_err" : f_center_err,
            
            "perc_errs" : perc_errs,
        }
        
        single_resonator_power_sweep[power] = {"res_df" : res_df, "fit_parameter_dict" : parameters_dict, "Expt_Config" : Qubit_Punchout_Config}
    
        display(f"Power {power} dBm - [{time.time() - tstart_power:1.2f} seconds]")
        
        # shift f_res to be the minimum of this measurement for the next measurement
        # f_magn_min = freqs[magn_dB.argmin()]
        # f_res = f_magn_min
    # save results from power sweep for this resonator
    label = f"Res_{res_idx}_{f_res_estimate/1e6:1.0f}_MHz"
    all_punchout_results[label] = single_resonator_power_sweep
    
    t_elapsed = tstart_res - tstart
    display(f"Finished measuring {label} - {t_elapsed = :1.2f} seconds.")
    
t_elapsed_total = round(time.time() - tstart, 2)
display(f"Finished measuring {len(all_punchout_results)} resonators - {t_elapsed_total = } seconds.")


expt_folder = Path(f"data/PunchOut_{dstr}")
expt_folder.mkdir(exist_ok=True)
data_filepath = expt_folder / f"all_punchout_results.pk1"

with open(data_filepath, 'wb') as fp:
    pickle.dump(all_punchout_results, fp)
    print(f'Dictionary saved successfully to file at {expt_folder}')
