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

# %%
from bcqt_hub.src.modules.DataAnalysis import DataAnalysis
import bcqt_hub.experiments.quick_helpers as qh

from bcqt_hub.src.drivers.instruments.VNA_Keysight import VNA_Keysight

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

PNA_X = VNA_Keysight(VNA_Keysight_InstrConfig, debug=True)

PNA_X.init_configs(VNA_Keysight_InstrConfig)

# %%

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

    
    #########################

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


PNA_X.check_instr_error_queue()
PNA_X.filter_configs()

PNA_X.update_configs(**Measurement_Configs)
# PNA_X.get_instr_params()
display(PNA_X.configs)

PNA_X.setup_s2p_measurement()


# %%
PNA_X.run_measurement() 

s2p_df = PNA_X.return_data_s2p()
all_axes = qh.plot_s2p_df(s2p_df)

save_dir = "./cooldown57"
expt_category = "Fast_Qi_Measurements"
meas_name = "Line4_TonyTa_NbSi_03"

filename, filepath = qh.Archive_Data(PNA_X, s2p_df, meas_name=meas_name, expt_category=expt_category, all_axes=all_axes)


# %% manually load data

load_filepath = r"C:\Users\Lehnert Lab\GitHub\bcqt-ctrl\prototype_msmt_code\experiments\VNA Experiments\VNA Characterization\data_jin_characterization\S12_MXC\001_Input_Line24_to_Attenuators\Input_Line24_to_Attenuators_001.csv"

loaded_df, all_magns, all_phases, freqs = qh.Load_CSV(load_filepath)

all_axes = qh.plot_s2p_df(loaded_df, plot_complex=True, track_min=False, title=meas_name, do_edelay_fit=False)
