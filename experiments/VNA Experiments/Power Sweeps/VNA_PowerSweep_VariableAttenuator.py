# %%
"""
    Test implementation of VNA Power Sweep with Variable Attenuator
"""

from pathlib import Path
import sys, time, datetime
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


current_dir = Path(".")
script_filename = Path(__file__).stem

sys.path.append(r"C:\Users\Lehnert Lab\GitHub")
sys.path.append(r"C:\Users\Lehnert Lab\GitHub\bcqt_hub\bcqt_hub\drivers\misc\MiniCircuits")
sys.path.append(r"C:\Users\Lehnert Lab\GitHub\bcqt_hub\bcqt_hub\drivers\instruments")

from MC_VarAttenuator import MC_VarAttenuator
from bcqt_hub.bcqt_hub.modules.DataAnalysis import DataAnalysis
import bcqt_hub.experiments.quick_helpers as qh

from bcqt_hub.bcqt_hub.drivers.instruments.VNA_Keysight import VNA_Keysight

# %% import VNA driver

### create dict to hold "default" configurations
VNA_Keysight_InstrConfig = {
    "instrument_name" : "VNA_Keysight",
    # "rm_backend" : "@py",
    "rm_backend" : None,
    "instr_address" : 'TCPIP0::192.168.0.105::inst0::INSTR',
    "edelay" : 61.25,
    "averages" : 2,
    "sparam" : ['S21'],  
    
    # "segment_type" : "linear",                    
    # "segment_type" : "hybrid",
    "segment_type" : "homophasal",
}

### create instrument driver from "VNA_Keysight" class, which inherits BaseDriver
PNA_X = VNA_Keysight(VNA_Keysight_InstrConfig, debug=True)
MC_Variable_Atten = MC_VarAttenuator("192.168.0.113")  

    

# %%

#all_freqs =  [   
            # MQC_BOE_SOLV1
#            4.3389418e9,
#            4.7333838e9,
#            5.1108957e9,
#            5.4838248e9,
#            5.8733538e9,
#            6.2299400e9,  # very low Q
#            6.6206182e9,  # very low Q
#            6.9972504e9   # very low Q
                      
#           ]

all_freqs = [
             # MQC_BOE_02
             4.363937e9,
             4.736494e9,
             5.106847e9,
             5.474224e9,
             5.871315e9,
             6.230610e9,  # very low Q
             6.624036e9,  # very low Q
             7.010525e9  # very low Q
            ] 

vna_power = -90
var_attens = np.arange(1, 30, 1)

Measurement_Configs = {
    "f_span" : 0.5e6,
    "n_points" : 201,
    "if_bandwidth" : 1000,
    "sparam" : ['S21'],  
    "Noffres" : 10,
}



# %%
dstr = datetime.datetime.today().strftime("%m_%d_%H%M")

all_f_res = []
all_resonator_data = {}

tstart_all = time.time()
for idx, freq in enumerate(all_freqs):  # loop over all resonators
    
    freq_str = f"{freq/1e9:1.3f}".replace('.',"p")
    Measurement_Configs["f_center"] = freq
    resonator_name = f"Res{idx}_{freq_str}"
    
    res_power_sweep_dict = {}
    
    tstart_res = time.time()
    
    Measurement_Configs["power"] = vna_power
    Measurement_Configs["averages"] = 30000
    
    for ext_atten in var_attens:  # for each resonator, loop over all powers
            
        """ 
            use VNA to take & download data
        """
        
        MC_Variable_Atten.Set_Attenuation(ext_atten)
        
        if ext_atten >= 25:
             Measurement_Configs["averages"] = 35000
        
        elif ext_atten >= 15:
             Measurement_Configs["averages"] = 23000
             
        else:
            Measurement_Configs["averages"] = 5000
            
        print(f"\n    Power: {vna_power} dBm\n    Var. Attenuator: {ext_atten} dB\n    Averages set to {Measurement_Configs["averages"]}\n")
            
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
        axes = qh.plot_s2p_df(s2p_df, plot_complex=True, zero_lines=False)
        
        freqs = s2p_df["Frequency"][1:].to_numpy()
        magn = s2p_df["S21 magn_dB"][1:].to_numpy()
        
        f_res = round(freqs[magn.argmin()]/1e9,7)
        print(f"the data's lowest point is at {f_res=}")
        all_f_res.append(f_res)
        
        ### save data
        save_dir = r"./data/cooldown59/Line3_MQC_BOE_02"
        expt_category = rf"Line3_MQC_BOE_02_{dstr}"
        num_avgs = Measurement_Configs["averages"]
        meas_name = rf"{freq_str}GHz_{vna_power:1.1f}dBm_{ext_atten}dBAtten_{num_avgs}avgs".replace(".","p")

        filename, filepath = qh.archive_data(PNA_X, s2p_df, meas_name=meas_name, save_dir=save_dir, expt_category=expt_category, all_axes=axes)

        
    tstop_res = time.time() - tstart_res
    display(f"Resonator {idx} (f_res={freq}) - {tstop_res:1.2f} seconds elapsed ({tstop_res/60:1.1f}) mins")
    
tstop_all = time.time() - tstart_all
display(f"Measurement finished - {tstop_all:1.2f} seconds elapsed ({tstop_all/60:1.1f}) mins")

