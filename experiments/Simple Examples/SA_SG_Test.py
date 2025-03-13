
# %%
"""
    test with signal generator clean tone
    
    example implementation of bcqt-hub (name??)
"""

# %load_ext autoreload
# %autoreload 2

import time, sys
import numpy as np
import matplotlib.pyplot as plt


import bcqt_hub
from bcqt_hub.src.DataHandler import DataHandler, DataSet

from bcqt_hub.drivers.instruments.SG_Anritsu import SG_Anritsu
from bcqt_hub.drivers.instruments.SA_RnS_FSEB20 import SA_RnS_FSEB20

# %%

SA_RnS_InstrConfig = {
    "instrument_name" : "SA_RnS",
    "rm_backend" : None,
    "instr_address" : 'GPIB::20::INSTR',      
}

SG_Anritsu_InstrConfig = {
    "instrument_name" : "SG_Anritsu",
    "rm_backend" : None,
    "instr_address" : 'GPIB::8::INSTR',  # 3691A  (as of 3/13/25)
    # "instr_address" : 'GPIB::9::INSTR',  # 3692C
}


# %%

print("\n~~ Initializing test of SA with SG connected directly ~~")
time.sleep(0.5)

print("\n~~ Initializing SG ~~")
time.sleep(0.5)
SigGen = SG_Anritsu(SG_Anritsu_InstrConfig, debug=True)

print("\n~~ Initializing SA ~~")
time.sleep(0.5)
test_SA = SA_RnS_FSEB20(SA_RnS_InstrConfig, debug=True)


# %%

SigGen.check_instr_error_queue(print_output=True)
SigGen.print_console(SigGen.idn, prefix="self.write(*IDN?) ->")
SigGen.return_instrument_parameters(print_output=True)

SigGen.set_freq(4.5e9)
SigGen.set_power(-20)
SigGen.set_output(True)

SigGen.return_instrument_parameters(print_output=True)

# %%

test_SA.check_instr_error_queue(print_output=True)
test_SA.print_console(test_SA.idn, prefix="self.write(*IDN?) ->\n    ")

test_SA.return_instrument_parameters(print_output=True)


# %%

SigGen.set_freq(3e9)
SigGen.set_power(-20)
SigGen.set_output(True)

test_SA.set_freq_center_Hz(3e9)
test_SA.set_freq_span_Hz(10e6)
test_SA.set_IF_bandwidth(20000)
test_SA.trigger_sweep()
test_SA.write_check("*OPC")

test_SA.check_instr_error_queue(print_output=True)

# test_SA.write_check("*OPC")
# test_SA.set_freq_center_Hz(5.1e9)
# test_SA.set_freq_span_Hz(0.3e9)
# test_SA.set_IF_bandwidth(1000)
# test_SA.trigger_sweep()
# test_SA.write_check("*WAI")

# test_SA.check_instr_error_queue(print_output=True)
# %%
# test_SA.query_check("*OPC?")
# result = test_SA.query_check("*ESR?")
display(result)

# %%

test_SA.check_instr_error_queue(print_output=True)

freqCenterHz = test_SA.get_freq_center_Hz()
freqSpan = test_SA.get_freq_span_Hz()

traceStr = test_SA.query_check(f'TRAC:DATA? TRACE{1}') 

traceData = [float(x) for x in traceStr.split(',')]
freqs = np.linspace(freqCenterHz - freqSpan / 2, freqCenterHz + freqSpan / 2, len(traceData));


display(SigGen.return_instrument_parameters())
display(test_SA.return_instrument_parameters())
 # %%

"""
    data archiving

"""
archiver = DataHandler()
archiver.append_metadata(SA_RnS_InstrConfig)
archiver.append_metadata(SG_Anritsu_InstrConfig)

from pathlib import Path
cur_dir = Path("./SA_SG_test_experiments")
archiver.create_metadata_file(cur_dir)

archiver.save_array(freqs)
archiver.save_array(traceData)

# %%

from scipy.signal import find_peaks
peaks, _ = find_peaks(traceData, prominence=10)

fig, ax = plt.subplots(1, 1, figsize=(8,5))
ax.plot(freqs, traceData, '.')
for idx in peaks:
    ax.plot(freqs[idx], traceData[idx], "o", fillstyle="none", markeredgewidth=2, markersize=10,
             label=f"{freqs[idx]/1e6:1.2f} MHz")
    
ax.set_title("Spectrum Analyzer Output")
fig.legend()

plt.show()

# %%
# %%
# *OPC? places a 1 on the output queue when operation is complete. *OPC raises 
# bit 0 in the event status register when operation is complete. Both outputs are used for client synchronization.
# For example, the client may wait until it receives 1 on the output queue from *OPC?