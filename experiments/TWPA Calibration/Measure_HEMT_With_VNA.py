
# %%
"""
    TWPA Calibration - VNA Sweep

        Procedure:
        
            (0) Set initial TWPA pump frequency and pump power
            (1) Perform two identical VNA sweeps, one with and one without the TWPA pump
            (2) Repeat (1) for a new pump power but at the same frequency
            (3) Repeat (1)-(2) for a new frequency
            
        At the end, you will have a dataset that consists of two traces swept over power, and swept over frequency.
        
        You can either see the *raw* gain profile of the TWPA from creating a surface plot of just the "TWPA On" trace, or you
        can see the *effective* gain of the TWPA by creating a surface plot of the ratio/difference of the "TWPA On" and "TWPA Off"
        traces.
        
        Why do we need two traces? Because, generally we want the pump config that give the best SNR, not the most gain. It is possible 
        that a given config has more gain, but also has a higher noise floor. Thus, we want to have on/off traces so that we can compare
        the *effective* increase in SNR.
        
"""

from pathlib import Path
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import time, sys

dstr = datetime.today().strftime("%m_%d_%I%M%p")
current_dir = Path(".")
script_filename = Path(__file__).stem

sys.path.append(r"C:\\Users\\Lehnert Lab\\GitHub")
import bcqt_hub

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
def strip_specials(input):
    return input.replace("\\r","").replace("\\n","")

def Archive_Data(VNA, s2p_df:pd.DataFrame, meas_name:str, expt_category:str = '', save_dir:str = "./data", all_axes=None):
    # check if save_dir is a path or string
    if not isinstance(save_dir, Path):
        save_dir = Path(save_dir).absolute()
        
    timestamp = datetime.today().strftime("%m_%d_%I%M%p")
    # file_dir = save_dir / expt_category / meas_name / timestamp
    file_dir = save_dir / expt_category / meas_name
    
    # check if file_dir exists
    if not file_dir.exists():
        VNA.print_console(f"Creating category {expt_category}")
        VNA.print_console(f"    under save directory {save_dir}")
        file_dir.mkdir(exist_ok=True, parents=True)
    
    # append number to end of filename and save to csv
    expt_no = len(list(file_dir.glob("*.csv"))) + 1    
    filename = f"{meas_name}_{expt_no:03d}.csv"
    VNA.print_console(f"Saving data as {filename}")
    VNA.print_console(f"    under '{str(Path(*file_dir.parts[-6:]))}'")
    
    final_path = file_dir / filename
    print(final_path)
    s2p_df.to_csv(final_path)
    
    if all_axes is not None:
        for axes in all_axes:
            ax = axes[0]
            fig = ax.get_figure()
            title = fig.get_suptitle().replace(" - ","_") + f"{expt_no:03d}.png"
            fig_filename = file_dir / title
            fig.tight_layout()
            fig.savefig(fig_filename)
            plt.show()
            print(fig_filename)
            
    
    return filename, final_path.parent

def Load_CSV(filepath):
    """
        convenience method - take csv filepath and return df, magns, phases, and freqs
    """
    
    if not isinstance(filepath, Path):
        filepath = Path(filepath).absolute()
    
    df = pd.read_csv(filepath, index_col=0)
    
    all_magns, all_phases = [], []
    
    for col in df:
        if "magn" in col.lower():
            series = df[col].values[1:]
            all_magns.append(series)
        if "phase" in col.lower():
            series = df[col].values[1:]
            all_phases.append(series)
        if "freq" in col.lower():
            freqs = df[col].values[1:]
    
    return df, all_magns, all_phases, freqs


# %%

import bcqt_hub.experiments.quick_helpers as qh
from bcqt_hub.src.drivers.instruments.VNA_Keysight import VNA_Keysight
from bcqt_hub.src.drivers.instruments.SG_Anritsu import SG_Anritsu

VNA_Keysight_InstrConfig = {
    "instrument_name" : "VNA_Keysight",
    # "rm_backend" : "@py",
    "rm_backend" : None,
    "instr_address" : 'TCPIP0::192.168.0.105::inst0::INSTR',
    "n_points" : 1001,
    "f_start" : 4e9,
    "f_stop" : 9e9,
    "if_bandwidth" : 5000,
    "power" : -30, 
    "edelay" : 0,
    "averages" : 2,
    "sparam" : ['S21'],  
    "segment_type" : "linear",
}

SG_Generator_InstrConfig = {
    "instrument_name" : "SG_MG3692C",
    "rm_backend" : None,
    "instr_address" : 'GPIB::8::INSTR',  
}

PNA_X = VNA_Keysight(VNA_Keysight_InstrConfig, debug=True)
SG_MG3692C = SG_Anritsu(SG_Generator_InstrConfig, debug=True)


# %%
all_instr = [PNA_X, SG_MG3692C]
for instr in all_instr:
    instr.write_check("*CLS")
    print(f"Checking [{instr.model} {instr.model_no}] for communication:")
    # instr.check_instr_error_queue(print_output=True)
    instr.print_console(instr.query_check("*IDN?"), prefix="self.write(*IDN?) ->")
    # instr.return_instrument_parameters(print_output=True)

# %%
# estimate time
start, stop = 7.809e9, 8.309e9
npts = 501
sweep_pump_freqs = np.linspace(start, stop, npts)
diff = np.diff(sweep_pump_freqs)[0]
sweep_time = 0.5
time_elapsed = npts * sweep_time
print(f"{start/1e6 = } MHz, {stop/1e6 = } MHz")
print(f"step = {diff/1e6:1.2f} MHz, {npts = }")
print(f"estimated time: {time_elapsed/60:1.2f} mins")

# %%

# defaults
pump_freq = 7.909e9
pump_power = -17

# sweeps
sweep_pump_freqs = np.linspace(start, stop, npts)
sweep_pump_powers = np.linspace(-15, -18, 101)

save_dir = "./cooldown57"
# expt_category = "HEMT Calibration #1 - Pump Frequency"
expt_category = "HEMT Calibration #1 - Pump Power"

# for pump_freq in sweep_pump_freqs:
for pump_power in sweep_pump_powers:
    PNA_X.check_instr_error_queue()
    SG_MG3692C.check_instr_error_queue()
    
    assert pump_freq > 1e9
    assert pump_power < -12

    meas_name = f"TestMeas_PumpFreq_{pump_freq/1e6:1.0f}MHz_PumpPower_{pump_power}dBm"
    
    # configure  instruments
    SG_MG3692C.set_freq(pump_freq)
    SG_MG3692C.set_power(pump_power)
    SG_MG3692C.set_output(True)

    # prepare instrument
    PNA_X.init_configs(VNA_Keysight_InstrConfig)
    PNA_X.get_instr_params()

    # Take data
    PNA_X.setup_s2p_measurement()
    PNA_X.run_measurement()
    

    # download and archive data
    s2p_df = PNA_X.return_data_s2p(archive_complex=False)
    all_axes = qh.plot_s2p_df(s2p_df, title=meas_name)


    filename, filepath = Archive_Data(PNA_X, s2p_df, meas_name=meas_name, expt_category=expt_category, all_axes=all_axes)



# %%
