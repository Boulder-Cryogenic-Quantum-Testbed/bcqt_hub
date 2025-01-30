# %%
"""
    Analysis script for Calibrate_TWPA
        - plots csv's and shows TWPA ON & TWPA OFF side by side
        - shows best frequency & best amplitude for TWPA
        
"""

import sys
import numpy as np
import matplotlib.pyplot as plt

import regex as re
import pandas as pd
from pathlib import Path
from datetime import datetime

dstr = datetime.today().strftime("%m_%d_%H%M")
current_dir = Path(".")
# github_dir = Path("/Users/jlr7/Library/CloudStorage/OneDrive-UCB-O365/GitHub")
github_dir = Path(r"C:\Users\Lehnert Lab\GitHub")

script_filename = Path(__file__).stem

# import bcqt_hub.experiments.quick_helpers as qh
sys.path.append(github_dir)


data_dir = current_dir / r"data" / "cooldown59"


# %%

# use glob to grab all files
all_measurements = list(data_dir.glob("Line1*/*TWPA*"))

# for measurement in all_measurements:

meas_idx = 0
measurement = all_measurements[meas_idx]

print(f"Measurement [{meas_idx}/{len(all_measurements)}]:  {measurement.name}")
all_traces = sorted(list(measurement.glob("*TWPA*")))

packaged_data = []
for idx in range(len(all_traces) // 2):
    
    csv_TWPA_OFF = list(all_traces[2*idx].glob("*"))[0]
    csv_TWPA_ON = list(all_traces[2*idx+1].glob("*"))[0]

    filename = str(csv_TWPA_OFF.stem)
    
    freq_str = re.search(r"\d{7}KHz", filename).captures()[0]
    pump_freq = float(freq_str.replace("KHz",""))*1e3  # KHz -> Hz
    
    power_str = re.search(r"-\d{2}.\d{1,2}dBm", filename).captures()[0]
    pump_power = float(power_str.replace("dBm",""))
    
    print(f"Measurement [{idx}/{len(all_traces)}]:  {all_traces[2*idx].name}\n               {all_traces[2*idx+1].name}")

    df_TWPA_OFF = pd.read_csv(csv_TWPA_OFF, index_col=0)
    df_TWPA_ON = pd.read_csv(csv_TWPA_ON, index_col=0)

    fig, axes = plt.subplots(3,1, figsize=(10,7))
    ax1, ax2, ax3 = axes

    freqs, magn_TWPA_OFF, phase_TWPA_OFF = df_TWPA_OFF["Frequency"], df_TWPA_OFF["S21 magn_dB"], df_TWPA_OFF["S21 phase_rad"] 
    freqs, magn_TWPA_ON, phase_TWPA_ON = df_TWPA_ON["Frequency"], df_TWPA_ON["S21 magn_dB"], df_TWPA_ON["S21 phase_rad"]

    ax1.plot(freqs, magn_TWPA_ON, color='b')
    ax2.plot(freqs, magn_TWPA_OFF, color='r')
    ax3.plot(freqs, magn_TWPA_ON / magn_TWPA_OFF, color='g')
    
    ax1.sharey(ax2)
    
    ax1.set_title("TWPA On")
    ax2.set_title("TWPA Off")
    ax3.set_title("TWPA On / TWPA Off")
    fig_title = f"TWPA Calibration - {dstr}\n\n$f_{'{pump}'}$ = {pump_freq/1e9:1.6f} GHz \n$P_{'{pump}'}$ = {pump_power} dBm"
    fig.suptitle(fig_title, size=16)
    
    
    fig.tight_layout()
    plt.show()
    
    


# %%







# %%








