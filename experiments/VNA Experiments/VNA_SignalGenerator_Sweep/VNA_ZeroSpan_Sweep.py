# %%
"""
    Measure with the VNA set to zero span and the signal generator sweeping
    
    last update: 1/29/25 - Jorge
"""

# %load_ext autoreload
# %autoreload 2

# %%

from pathlib import Path
from datetime import datetime
import sys, time, pickle
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

current_dir = Path(".")
script_filename = Path(__file__).stem

sys.path.append(r"C:\Users\Lehnert Lab\GitHub\bcqt_hub")

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
    "segment_type" : "linear",
    # "segment_type" : "hybrid",
    
    
}

SG_Bottom_DefaultConfig = {
    "instrument_name" : "SG_MG3692C_Bottom",
    "rm_backend" : None,
    "instr_address" : 'GPIB::8::INSTR', 
}

### create instrument driver from "VNA_Keysight" class, which inherits BaseDriver
PNA_X = VNA_Keysight(VNA_Keysight_InstrConfig, debug=True)  
SG_MG3692C_Bottom = SG_Anritsu(SG_Bottom_DefaultConfig, debug=True)

Measurement_Configs = {
    "edelay" : 73.13, 
    
    # "f_start" : 4.0e9,
    # "f_stop" : 7.6e9,
    "f_center" : 6.5e9,
    "f_span" : 2e9,
    
    "n_points" : 5001,
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

### download data from instrument and plot
s2p_df = PNA_X.return_data_s2p(get_memory=False)

### save data
save_dir = "./cooldown59/"
expt_category = "Line1_RG_Nb_Qb02"

meas_name = "FindResonators"

all_axes = qh.plot_s2p_df(s2p_df, title=meas_name, unwrap=True, plot_complex=False)

# filename, filepath = qh.archive_data(PNA_X, s2p_df, meas_name=meas_name, expt_category=expt_category, all_axes=all_axes[0])


find_peaks_kwargs = {
    "height" : None,
    "threshold" : None,
    "distance" : None,
    "prominence" : 7,
    "width" : None,
}

peak_idxs, all_axes = qh.find_resonators(s2p_df, find_peaks_kwargs=find_peaks_kwargs, fig_title=f"\n{expt_category}\n{meas_name}") 

# filename, filepath = qh.archive_data(PNA_X, s2p_df, meas_name=meas_name, expt_category=expt_category, all_axes=all_axes)

# %% now that we have the resonator frequencies...
dstr = datetime.today().strftime("%m_%d_%H%M")
expt_folder = Path(f"data/ZeroSpan_{dstr}")
expt_folder.mkdir(exist_ok=True)

resonator_freqs = s2p_df["Frequency"][peak_idxs]
# power_array = [5, 0, -5, -10, -15, -20]
power_array = np.linspace(-3, -6, 10).round(1)

QubitSpectroscopy_Measurement_configs = {
    "f_span" : 0,
    "n_points" : 250,
    "if_bandwidth" : 1e3,  
    "power" : -60,
    "averages" : 3,
    "edelay" : 75e-9,
    "spectr_freq_span" : 20e6,
    "spectr_n_points" : 100,
}

expected_f01s = {
    0 : 4.085e9,
    1 : 4.00e9,
    2 : 4.10e9,
    3 : 4.30e9,
    # 4 : 4.05e9,
    # 5 : 4.05e9,
    6 : 4.6e9,
    # 7 : 4.05e9,
}

all_qubit_results = {}
for (idx, f_qubit), f_res in zip(expected_f01s.items(), resonator_freqs):
    
    tstart_qubit = time.time()
    all_power_measurements = {}
    # for power in [0, -2, -3, -4, -6, -8, -10, -12, -14, -16, -18]:
    for power in power_array:
        
        QubitSpectroscopy_Measurement_configs["f_center"] = f_res
            
        PNA_X.update_configs(**QubitSpectroscopy_Measurement_configs)
        PNA_X.setup_s2p_measurement() 
        PNA_X.write_check("SENS:SWE:TIME:AUTO off")
        PNA_X.write_check("SENS:SWE:TIME 0.005ms")
        PNA_X.write_check("SENSe:SWEep:GENeration STEP")
        PNA_X.write_check("SENS:SWE:DWEL 0.005ms")
        PNA_X.print_console(PNA_X.query_check("SENS:SWE:DWEL?"))
        PNA_X.print_console(PNA_X.query_check("SENS:SWE:TIME?"))
        PNA_X.query_check("SYST:ERR?")
        
        SG_MG3692C_Bottom.set_power(power, override_safety=True)
        SG_MG3692C_Bottom.set_output(True)
        
        f_span, n_points = QubitSpectroscopy_Measurement_configs["spectr_freq_span"], QubitSpectroscopy_Measurement_configs["spectr_n_points"]
        # freq_start, freq_stop, n_points = QubitSpectroscopy_Measurement_configs["f_start"], QubitSpectroscopy_Measurement_configs["f_stop"], QubitSpectroscopy_Measurement_configs["n_points"]
        freq_start, freq_stop = f_qubit - f_span/2, f_qubit + f_span/2
        
        qubit_freqs = np.linspace(freq_start, freq_stop, n_points)

        PNA_X.update_configs(**QubitSpectroscopy_Measurement_configs)
        
        single_power = []
        for f_spectr in qubit_freqs:
            SG_MG3692C_Bottom.set_freq(f_spectr)
            
            PNA_X.run_measurement() 
            
            spectroscopy_df = PNA_X.return_data_s2p(archive_complex=True)
            complex_vals = list(spectroscopy_df["S21 complex"])
            
            real, imag = [np.real(x) for x in complex_vals], [np.imag(x) for x in complex_vals]
            
            avg_real, avg_imag = np.average(real), np.average(imag)
            
            single_power.append(avg_real + 1j*avg_imag)
            
        
        #### plotting
        fig, axes = plt.subplots(2, 1, figsize=(12,10))
        ax1, ax2 = axes
        
        magn, phase = np.abs(single_power), np.angle(single_power)
        ax1.plot(qubit_freqs[:len(magn)]/1e6, magn, ".", markersize=10, color='r')    
        ax2.plot(qubit_freqs[:len(magn)]/1e6, phase, ".",  markersize=10, color='b')
        
        ax1.set_title("Magn vs Qubit Freq")
        ax2.set_title("Phase vs Qubit Freq")
        
        ax1.set_xlabel("Frequency [MHz]")
        ax2.set_xlabel("Frequency [MHz]")
        
        ax1.set_ylabel("VNA S21 Magn [dB]")
        ax2.set_ylabel("VNA S21 Phase [rad]")
        
        title_str = f"VNA/SG Qubit Spectroscopy\n f_res = {f_res/1e9:1.3f} GHz\nQubit Drive Power = {power} dBm "
        fig.suptitle(title_str)
        
        fig.tight_layout()
        plt.show()

        res_label = f"{power}dBm_Qubit{idx}_{f_qubit/1e6:1.0f}MHz"
        all_power_measurements[res_label] = single_power
            
        fig_filename = f"{res_label}_ZeroSpan.png"
        fig_filepath = expt_folder / fig_filename
        fig.savefig(fig_filepath)
        
    qubit_label = f"Qubit{idx}_{f_qubit/1e6:1.0f}_MHz"
    all_qubit_results[qubit_label] = complex_vals
    tfinish_qubit = time.time() - tstart_qubit
    
    display(f"Finished {qubit_label} - time elapsed = {tfinish_qubit:1.1f} seconds")
    
    break # work with just first qubit
    

data_filepath = expt_folder / f"vna_spectroscopy_results.pk1"

with open(data_filepath, 'wb') as fp:
    pickle.dump(all_qubit_results, fp)
    print(f'Dictionary saved successfully to file at {expt_folder}')



