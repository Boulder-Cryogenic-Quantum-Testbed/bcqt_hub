
"""
    Example implementation of quick_helpers (eventually DataProcessor object) to
    plot csv data from the TakeMeasurements.py script.
    
"""

# %%

from pathlib import Path
import sys
from datetime import datetime

dstr = datetime.today().strftime("%m_%d_%I%M%p")
current_dir = Path(".")
script_filename = Path(__file__).stem

sys.path.append(r"C:\Users\Lehnert Lab\GitHub")

import bcqt_hub.experiments.quick_helpers as qh

# %%

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