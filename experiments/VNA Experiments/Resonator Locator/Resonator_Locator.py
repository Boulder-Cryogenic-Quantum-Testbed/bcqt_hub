# %%
"""
    Finds resonators with a a focus on letting the user pick the
    span, number of points, and IF bandwidth easily, while stitching
    together all measurements from f_start to f_stop together
"""

from pathlib import Path
from datetime import datetime
import sys, time
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

dstr = datetime.today().strftime("%m_%d_%H%M")
current_dir = Path(".")
script_filename = Path(__file__).stem

sys.path.append(r"C:\Users\Lehnert Lab\GitHub\bcqt_hub\experiments")
sys.path.append(r"C:\Users\Lehnert Lab\GitHub\bcqt_hub")

import experiments.quick_helpers as qh
from bcqt_hub.drivers.instruments.VNA_Keysight import VNA_Keysight
from bcqt_hub.drivers.instruments.SG_Anritsu import SG_Anritsu


# %% import VNA driver

### create dict to hold "default" configurations
VNA_Keysight_InstrConfig = {
    "instrument_name" : "VNA_Keysight",
    # "rm_backend" : "@py",
    "rm_backend" : None,
    "instr_address" : 'TCPIP0::192.168.0.105::inst0::INSTR',
    "edelay" : 73.9,
    "averages" : 2,
    "sparam" : ['S21'],  
    
    "segment_type" : "linear",                    
    # "segment_type" : "hybrid",
    # "segment_type" : "homophasal",
}

### create instrument driver from "VNA_Keysight" class, which inherits BaseDriver
PNA_X = VNA_Keysight(VNA_Keysight_InstrConfig, debug=True)  
    

# %%

# all_freqs =  [   
#                 (4.0, 4.5),
#                 (4.5, 5.0),
#                 (5.5, 6.0),
#                 (6.0 ,6.5),
#                 (6.5, 7.0),
#                 (7.0, 7.5),
#                 (7.5, 8.0)
# ]

start, stop, step = 5.5, 7.5, 0.5
all_freqs = [
    (x, x+step) for x in np.arange(start, stop, step).round(2)
    ]

all_freqs.append((7.4, 7.6))

Measurement_Configs = {
    "n_points" : 30001,
    "if_bandwidth" : 1000,
    "sparam" : ['S21'],  
    "power" : -40,
    "averages" : 2,
}

print(f"Measuring {len(all_freqs)} spans with {Measurement_Configs["n_points"]} points each:", end="")
for freq_span in all_freqs:
    print(f"\n    {min(freq_span):1.1f} GHz to {max(freq_span):1.1f} GHz", end="")

# %%%
# from bcqt_hub.bcqt_hub.drivers.instruments.SG_Anritsu import SG_Anritsu

# SG_Generator_DefaultConfig = {
#     # "instrument_name" : "SG_MG3692C",
#     # "instrument_name" : "SG_MG3692C",
#     "rm_backend" : None,
#     "instr_address" : 'GPIB::8::INSTR',  
# }
#
# SG_MG3692C = SG_Anritsu(SG_Generator_DefaultConfig, debug=True)
#
# """ configure signal generator """
# SG_MG3692C.set_freq(7.909e9)
# SG_MG3692C.set_power(-17)
# SG_MG3692C.set_output(True)



# %% begin measuring
dstr = datetime.today().strftime("%m_%d_%H%M")

freq_span_data_dict = {}

tstart_all = time.time()
for idx, freq_span in enumerate(all_freqs):  # loop over all freq spans
    """
        define relevant variables, update meas params
    """
    
    freq_start = min(freq_span)
    freq_stop = max(freq_span)  # in case they are backwards!
    freq_str = f"{freq_start:1.1f}GHz_{freq_stop:1.1f}GHz".replace('.',"p")
    meas_name = f"Meas{idx}_{freq_str}"
    plot_title = f"{freq_start} GHz to {freq_stop} GHz"
    
    Measurement_Configs["f_start"] = freq_start
    Measurement_Configs["f_stop"] = freq_stop
    
    n_points = Measurement_Configs["n_points"]
    power = Measurement_Configs["power"]
    
    """ 
        use VNA to take & download data
    """
        
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
    
    # save freq span as key
    freq_span_data_dict[f"{freq_start}_{freq_stop}"] = s2p_df
    
    axes = qh.plot_s2p_df(s2p_df, plot_complex=False, zero_lines=False, plot_title=plot_title)
    axes = axes[0]
    
    freqs = s2p_df["Frequency"][1:].to_numpy()
    magn = s2p_df["S21 magn_dB"][1:].to_numpy()
    
    ### save data
    save_dir = r"./data/cooldown59/Line5_ManuelsQubit"
    expt_category = rf"Broad_Sweep/{dstr}"
    num_avgs = Measurement_Configs["averages"]
    meas_name = rf"{freq_str}_{power:1.1f}dBm_{num_avgs}avgs_{n_points}points".replace(".","p")

    filename, filepath = qh.archive_data(PNA_X, s2p_df, meas_name=meas_name, save_dir=save_dir, expt_category=expt_category, all_axes=axes)

    
tstop_all = time.time() - tstart_all
display(f"Measurement {idx} ({freq_str}) - {tstop_all:1.2f} seconds elapsed ({tstop_all/60:1.1f}) mins")
    

# %%

# we essentially want to stitch all df's together from top to bottom. no need to worry about
# x-axis since every dataframe has its proper frequency column

phase_offset_value = 0  # so we stitch the phase properly
freqs, magn_dB, phase_rad = [], [], []
for key, s2p_df in freq_span_data_dict.items():
    
    freq_start, freq_stop = key.split("_")
    freq_start, freq_stop = float(freq_start), float(freq_stop)
    
    df_freqs, df_magn_dB, df_phase_rad = s2p_df["Frequency"][::-1], s2p_df["S21 magn_dB"][::-1], s2p_df["S21 phase_rad"][::-1]
    
    freqs.append(df_freqs.values)
    magn_dB.append(df_magn_dB.values)
    phase_rad.append(df_phase_rad.values)# - phase_offset_value)
    
    # phase_offset_value += df_phase_rad.values[0]
    # print(phase_offset_value,  df_phase_rad.values[0])
    
    # phase_rad = list(np.array(phase_rad) - phase_offset_value)
    # phase_offset_value = phase_rad[0]
    
# freq_span_data_dict
freqs = np.array(freqs).flatten()
magn_dB = np.array(magn_dB).flatten()
phase_rad = np.array(phase_rad).flatten()

fig, axes = plt.subplots(2,1, figsize=(15,5))
ax1, ax2 = axes

ax1.plot(freqs, magn_dB, 'r.')
ax2.plot(freqs, phase_rad, 'b.')

ax1.set_title("Magn vs Frequency")
ax2.set_title("Phase vs Frequency")

ax1.set_xlabel("Frequency [MHz]")
ax2.set_xlabel("Frequency [MHz]")

ax1.set_ylabel("VNA S21 Magn [dB]")
ax2.set_ylabel("VNA S21 Phase [rad]")

# ax1.set_xlim([5e9, 7.7e9])

# %% now use qh.find_resonators() to... find the f_res points

freq_min, freq_max = 7e9, 7.35e9
freq_min_idx, freq_max_idx = np.argmin(abs(freqs - freq_min)), np.argmin(abs(freqs - freq_max))

df_dict = {
    "Frequency" : freqs[freq_min_idx:freq_max_idx],
    "S21 magn_dB" : magn_dB[freq_min_idx:freq_max_idx],
    "S21 phase_rad" : phase_rad[freq_min_idx:freq_max_idx]
}

find_peaks_kwargs = {
    "height" : 25,
    "threshold" : 0.5,
    "distance" : len(freqs)//100,
    "prominence" : 4,
    "width" : (None, 38),
}


res_finder_df = pd.DataFrame(df_dict)

peak_idxs, all_axes = qh.find_resonators(res_finder_df, find_peaks_kwargs=find_peaks_kwargs, fig_title=f"\n{expt_category}\n{meas_name}",
                                         plot_phase=True) 

peak_idxs += freq_min_idx  # shift indices back up since we truncated the dataframe


res_freqs = freqs[peak_idxs]

print(res_freqs)


# %%
