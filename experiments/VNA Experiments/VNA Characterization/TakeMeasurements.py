# %%
"""
    Test implementation of VNA driver
"""

# %load_ext autoreload
# %autoreload 2

# %%

from pathlib import Path
from datetime import datetime
import sys
import matplotlib.pyplot as plt
import pandas as pd

dstr = datetime.today().strftime("%m_%d_%I%M%p")
current_dir = Path(".")
script_filename = Path(__file__).stem

sys.path.append(r"C:\Users\Lehnert Lab\GitHub")

from bcqt_hub.src.modules.DataAnalysis import DataAnalysis
import bcqt_hub.experiments.quick_helpers as qh

from bcqt_hub.src.drivers.instruments.VNA_Keysight import VNA_Keysight

""" 
    most of the measurements for the characterization will be taken in the interactive window, so
        let's create some helper functions to speed up that process
        
    characterization workflow:
    
        1) begin by checking instrument errors, setting up configs, and setting up the s2p measurement
        2) use run_measurement() to tell VNA to start measurement, but will not download until next step!
        3) return_data_s2p() will transfer data from VNA to this script- no measurement parameters are modified!
             .
             .
        4) archive_data() will take whatever dataframe and save to a specified location with
            appropriate metadata.
            
        bonus:
        
        5) if you want to load a csv and plot the data, the final cell will use load_csv() and plot_s2p_df() to do so
"""

# %%

### create dict to hold "default" configurations
VNA_Keysight_InstrConfig = {
    "instrument_name" : "VNA_Keysight",
    # "rm_backend" : "@py",
    "rm_backend" : None,
    "instr_address" : 'TCPIP0::192.168.0.105::inst0::INSTR',
    "n_points" : 1001,
    "f_start" : 2e9,
    "f_stop" : 10e9,
    "if_bandwidth" : 1000,
    "power" : -50,
    "edelay" : 0,
    "averages" : 2,
    "sparam" : ['S11', 'S21'],  
    
    # "segment_type" : "linear",
    "segment_type" : "hybrid",
}

### create instrument driver from "VNA_Keysight" class, which inherits BaseDriver
PNA_X = VNA_Keysight(VNA_Keysight_InstrConfig, debug=True)  

### Manually initialize configs, should technically be unnecessary
PNA_X.init_configs(VNA_Keysight_InstrConfig)

    
# %%
Measurement_Configs = {
    "f_center" : 5.863250e9,
    "f_span" : 0.1e6,
    "n_points" : 10001,
    "if_bw" : 5000,
    "power" : -50,
    "averages" : 2,
    "sparam" : ['S11', 'S21'],  
}


#### read error queue 
PNA_X.check_instr_error_queue()

#### give instr driver a new dict to overwrite existing settings
PNA_X.update_configs(**Measurement_Configs)

### method to see what settings are applied
### NOTE: need to distinguish instr settings
###         that are in the object's config
###         and settings that are on the
###         physical instrument in the lab!
PNA_X.get_instr_params()  # show configs in the lab instrument
display(PNA_X.configs)    # show configs in the object itself

### sets everything up for a measurement without turning on the 
### power and recording data
PNA_X.setup_s2p_measurement()


# %%

### start measurement BUT DOES NOT SEND DATA TO LAB PC
PNA_X.run_measurement() 

### download data from instrument and plot
s2p_df = PNA_X.return_data_s2p()
all_axes = qh.plot_s2p_df(s2p_df)

### save data
save_dir = "./cooldown57"
expt_category = "Fast_Qi_Measurements"
meas_name = "Line4_TonyTa_NbSi_03"

filename, filepath = qh.Archive_Data(PNA_X, s2p_df, meas_name=meas_name, expt_category=expt_category, all_axes=all_axes)

# %%

basepath = Path(r"C:\Users\Lehnert Lab\GitHub\bcqt_hub\experiments\VNA Experiments\VNA Characterization\data\HEMT_Testing")
# file_dir = basepath / r"Line26_InsertionLoss"
file_dir = basepath / r"NbTi_Cable"

# %% manually load data and plot

filepath = list(file_dir.glob("*.csv"))[-1]

loaded_df, all_magns, all_phases, freqs = qh.load_csv(filepath)
loaded_df.drop(["datetime.now()"], inplace=True)


all_axes = qh.plot_s2p_df(loaded_df, plot_complex=False, track_min=False, title=filepath.stem, do_edelay_fit=False)


# %% two files and two dfs
file_dir_1 =  basepath / r"HEMT_ON_-55dBm_Line25"
file_dir_2 =  basepath / r"HEMT_ON_-55dBm_Line27"
# file_dir_2 =  basepath / r"HEMT_OFF_-55dBm_Line27_Background"
assert file_dir_1.exists() and file_dir_2.exists()

filepath_1 = list(file_dir_1.glob("*.csv"))[-1]
filepath_2 = list(file_dir_2.glob("*.csv"))[-1]


loaded_df_1, all_magns_1, all_phases_1, freqs_1 = qh.load_csv(filepath_1)
loaded_df_2, all_magns_2, all_phases_2, freqs_2 = qh.load_csv(filepath_2)

freq = loaded_df_2["Frequency"].values[1:].astype(float)
magn_1 = loaded_df_1["S21 magn_dB"].values[1:].astype(float)
magn_2 = loaded_df_2["S21 magn_dB"].values[1:].astype(float)

# %%

mosaic = "AA\nAA\nBB"
fig1, axes = plt.subplot_mosaic(mosaic, figsize=(8, 8))
ax1, ax2 = axes["A"], axes["B"]

ax1.set_title("VNA Power = -55 dBm")
ax1.plot(freq, magn_1, label="HEMT 25")
ax1.plot(freq, magn_2, label="HEMT 27")
ax1.legend()

ax2.set_title("[HEMT 27 - HEMT 25]")
ax2.plot(freq, (magn_1 - magn_2))
ax2.axhline(0, linestyle=':', color='k')


for ax in (ax1, ax2):
    ax.set_xlim([4e9, 8e9])
    


fig1.suptitle("Optimized HEMT S21 Measurements")
    
ax1.set_ylim([0, 30])
ax2.set_ylim([-20, 10])

fig1.tight_layout()

# %%
