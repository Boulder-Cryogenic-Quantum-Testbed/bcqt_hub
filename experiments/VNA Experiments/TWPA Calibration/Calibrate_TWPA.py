"""
    TWPA Calibration - VNA Sweep

        Procedure:
            (0) Set initial pump frequency and pump power
            
            (loop i) sweep pump frequency
                (0) change pump frequency
                
                (loop j) sweep pump power
                    (0) change pump power
                    (1) measure S21 with the TWPA on
                    (2) measure S21 with the TWPA off as a reference

            
        At the end, you will have a 2D dataset, a set of TWPA frequencies, each swept over power
        
        You can either see the *raw* gain profile of the TWPA from creating a surface plot of just the "TWPA On" trace, or you
        can see the *effective* gain of the TWPA by creating a surface plot of the "ON" data with the background "OFF" data subtracted
        
        Why do we need two traces? Because, generally we want the pump config that give the best SNR, not the most gain. It is possible 
        that a given config has more gain, but also has a higher noise floor. Thus, we want to have on/off traces so that we can compare
        the *effective* increase in SNR.
        
"""

# %%

from pathlib import Path
import sys, time
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt

dstr = datetime.today().strftime("%m_%d_%H%M")
current_dir = Path(".")
script_filename = Path(__file__).stem

sys.path.append(r"C:\Users\Lehnert Lab\GitHub")

import bcqt_hub.experiments.quick_helpers as qh

data_dir = current_dir / r"data" / rf"Calibrate_TWPA_{dstr}"

# %%

"""
    Instruments - 
        VNA_Keysight
        Signal Generator
""" 

VNA_Keysight_DefaultConfig = {
    "instrument_name" : "VNA_Keysight",
    # "rm_backend" : "@py",
    "rm_backend" : None,
    "instr_address" : 'TCPIP0::192.168.0.105::inst0::INSTR',
    "edelay" : 71e-9,
    "sparam" : ['S21'],  
    
    "segment_type" : "linear",
    # "segment_type" : "hybrid",
}

SG_TWPA_DefaultConfig = {
    "instrument_name" : "SG_MG3692C_TOP",
    "rm_backend" : None,
    "instr_address" : 'GPIB::8::INSTR',  
}

SG_TestTone_DefaultConfig = {
    "instrument_name" : "SG_MG3691A_TestTone",
    "rm_backend" : None,
    "instr_address" : 'GPIB::7::INSTR',  
}


# %% initiate instrument drivers
""" see 'VNA_Experiments/TakeMeasurements.py' or 'Simple_VNA_Sweep' for example usage """

from bcqt_hub.bcqt_hub.drivers.instruments.VNA_Keysight import VNA_Keysight
from bcqt_hub.bcqt_hub.drivers.instruments.SG_Anritsu import SG_Anritsu

PNA_X = VNA_Keysight(VNA_Keysight_DefaultConfig, debug=True)  
SG_MG3692C_TWPA = SG_Anritsu(SG_TWPA_DefaultConfig, debug=True)
# SG_MG3691A_TestTone = SG_Anritsu(SG_TestTone_DefaultConfig, debug=True)


# %% set experimental configs

VNA_Settings = {
    "f_start" : 5.5e9,
    "f_stop" : 7.25e9,
    "n_points" : 5001,
    "if_bandwidth" : 10000,
    "power" : -40,
    "averages" : 2,
    "sparam" : ['S21'],  
}

Sweep_Config = {
    "num_powers" : 10,
    "num_freqs" : 10,
    "freq_sweep_start" : 7.908e9,
    "freq_sweep_stop" : 7.910e9,
    "power_sweep_start" : -15,
    "power_sweep_stop" : -17,
}

power_sweep = np.linspace(Sweep_Config["power_sweep_start"], Sweep_Config["power_sweep_stop"], Sweep_Config["num_powers"]).round(2)
freq_sweep = np.linspace(Sweep_Config["freq_sweep_start"], Sweep_Config["freq_sweep_stop"], Sweep_Config["num_freqs"]).round(0)



# %% prepare instruments for measurements
#### read VNA error queue 

#### update configs with measurement settings
PNA_X.update_configs(**VNA_Settings)

display(PNA_X.get_instr_params())  # show configs in the lab instrument
display(PNA_X.configs)    # show current configs in the code, NOT in the physical lab instrument

# SG_MG3692C_TWPA.return_instrument_parameters()

PNA_X.check_instr_error_queue()
SG_MG3692C_TWPA.check_instr_error_queue()


# %% run experiment!

""" see top of script for explanation of measurement """
data_TWPA_on, data_TWPA_off = {}, {}
    
tstart_all = time.time()
for pump_freq in freq_sweep:
    # loop over several frequencies, and for each freq, sweep the power
    
    for pump_power in power_sweep:
        
        """ configure signal generator """
        SG_MG3692C_TWPA.set_freq(pump_freq)
        SG_MG3692C_TWPA.set_power(pump_power)
        
        time.sleep(1)
        
        """ begin VNA measurement w/ TWPA pump on"""
        SG_MG3692C_TWPA.set_output(True)
        
        # Take data and archive
        PNA_X.setup_s2p_measurement()
        PNA_X.run_measurement()
        df_TWPA_on = PNA_X.return_data_s2p(archive_complex=False)
        
        time.sleep(1)
        
        """ repeat VNA measurement w/ TWPA pump off"""
        SG_MG3692C_TWPA.set_output(False)
        
        # Take data and archive
        PNA_X.setup_s2p_measurement()
        PNA_X.run_measurement()
        df_TWPA_off = PNA_X.return_data_s2p(archive_complex=False)
        
        """ save data into list """
        
        data_TWPA_on[f"{pump_freq}_{pump_power}"] = df_TWPA_on
        data_TWPA_off[f"{pump_freq}_{pump_power}"] = df_TWPA_off
            
            
        ### save data
        save_dir = r"./data/cooldown59/Line1_RG_Nb_Ta_Qb01"
        expt_category = rf"Line1_RG_Nb_Ta_Qb01_{dstr}_TWPA_Calibration"
        meas_name_on = f"TWPA_Calibration_{pump_freq/1e3:1.0f}KHz_{pump_power}dBm_ON"
        meas_name_off = f"TWPA_Calibration_{pump_freq/1e3:1.0f}KHz_{pump_power}dBm_OFF"

        qh.archive_data(PNA_X, df_TWPA_on, meas_name=meas_name_on, save_dir=save_dir, expt_category=expt_category)
        qh.archive_data(PNA_X, df_TWPA_off, meas_name=meas_name_off, save_dir=save_dir, expt_category=expt_category)
        
    
tstop_all = tstart_all - time.time()
display(f"Measurement Finished - {tstop_all:1.2f} seconds elapsed ({tstop_all/60:1.1f}) mins")

 # %%

for (key_on, df_on), (key_off, df_off) in zip(data_TWPA_on.items(), data_TWPA_off.items()):

    pump_freq, pump_power = key_on.split("_")
    pump_freq, pump_power = float(pump_freq), float(pump_power)
    
    print("TWPA On")
    all_axes = qh.plot_s2p_df(df_on, plot_complex=False, plot_title=f"TWPA On\n     $f_{'{pump}'}$ = {pump_freq/1e9:1.4f} GHz\n    $P_{'{pump}'}$ = {pump_power:1.0f} dBm")
    plt.show()
    print("TWPA Off")
    all_axes = qh.plot_s2p_df(df_off, plot_complex=False, plot_title=f"TWPA Off\n    $f_{'{pump}'}$ = {pump_freq/1e9:1.4f} GHz\n    $P_{'{pump}'}$ = {pump_power:1.0f} dBm")
    plt.show()
    
    # break
    
SG_MG3692C_TWPA.set_output(True)
SG_MG3692C_TWPA.set_freq(7.909e9)
SG_MG3692C_TWPA.set_power(-17)


# %%
