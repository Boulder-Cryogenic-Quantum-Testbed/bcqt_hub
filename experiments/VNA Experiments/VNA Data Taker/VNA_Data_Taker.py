# %%
"""
    Example implementation of VNA driver
    
    last update: 1/13/25
"""

# %load_ext autoreload
# %autoreload 2

# %%

from pathlib import Path
from datetime import datetime
import sys
import matplotlib.pyplot as plt
import pandas as pd

dstr = datetime.today().strftime("%m_%d_%H%M")
current_dir = Path(".")
script_filename = Path(__file__).stem

display(current_dir.resolve())
sys.path.append(r"C:\Users\Lehnert Lab\GitHub\bcqt_hub\experiments")
sys.path.append(r"C:\Users\Lehnert Lab\GitHub\bcqt_hub")
# sys.path.append(r"C:\Users\Lehnert Lab\GitHub")

from bcqt_hub.src.DataAnalysis import DataAnalysis
import quick_helpers as qh

from bcqt_hub.drivers.instruments.VNA_Keysight import VNA_Keysight

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
        
        5) if you want to load a csv and plot the data, use the associated xxx_Analyze script in this directory.
"""

# %%

### create dict to hold "default" configurations
VNA_Keysight_InstrConfig = {
    "instrument_name" : "VNA_Keysight",
    # "rm_backend" : "@py",
    "rm_backend" : None,
    "instr_address" : 'TCPIP0::192.168.0.105::inst0::INSTR',
    
    'sparam' : ['S21'],
    "segment_type" : "linear",
    # "segment_type" : "hybrid",
    
    "f_start" : 5.5e9,
    "f_stop" : 7.6e9,
    # "f_center" : 6e9,
    # "f_span" : 3.5e9,
    
    "edelay" : 73.19, 
    
}

### create instrument driver from "VNA_Keysight" class, which inherits BaseDriver
PNA_X = VNA_Keysight(VNA_Keysight_InstrConfig, debug=True)  

PNA_X.update_configs(**VNA_Keysight_InstrConfig)
    
# %%
Measurement_Configs = {
    "n_points" : 30001,
    "if_bandwidth" : 1000,
    "power" : -20,
    "averages" : 2,
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

# %% 
# ### sets everything up for a measurement without turning on the 
### power and recording data
PNA_X.setup_s2p_measurement()

### start measurement BUT DOES NOT SEND DATA TO LAB PC
PNA_X.run_measurement() 

# %%
### download data from instrument and plot
s2p_df = PNA_X.return_data_s2p(get_memory=True)

### save data
save_dir = "./cooldown59/"
expt_category = "Line2_RG_Nb_Qb02"

# meas_name = "Line1_RG_Nb_Ta_01_-20dBm_Zoomed"
meas_name = "Line2_RG_Nb_Qb02"

all_axes = qh.plot_s2p_df(s2p_df, title=meas_name, unwrap=True, plot_complex=False)

filename, filepath = qh.archive_data(PNA_X, s2p_df, meas_name=meas_name, expt_category=expt_category, all_axes=all_axes[0])

# %%

find_peaks_kwargs = {
    "height" : None,
    "threshold" : None,
    "distance" : 10,
    "prominence" : 10,
    "width" : None,
}

all_axes = qh.find_resonators(s2p_df, find_peaks_kwargs=find_peaks_kwargs, fig_title=f"\n{expt_category}\n{meas_name}") 

filename, filepath = qh.archive_data(PNA_X, s2p_df, meas_name=meas_name, expt_category=expt_category, all_axes=all_axes)

# %%

