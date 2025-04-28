# %%
import sys, os
sys.path.append(r"C:\Users\user\Documents\GitHub\bcqt-ctrl\resonator_measurements\helper_scripts")
sys.path.append(r"C:\Users\user\Documents\GitHub\scresonators")

import misc_functions as mf
import helper_fit as hf
import helper_misc as hm
import helper_load as hl
import regex as re
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from pathlib import Path

# %%
%load_ext autoreload
%autoreload 2

# %%  Get sample name and device information

####################################################################################
#### Need to put UserFile_Analyze_Wei_Ren.py into the folder we want to analyze ####
#### For example, in the folder named "Line_5-NW_Ta2O5_15nm_01"                 ####
####################################################################################
current_dir = Path(".").absolute()
line_num, sample_name = re.split(r"-", current_dir.name, maxsplit=1) 
print(f'line_num = {line_num}\nsample_name = {sample_name}')

#%% Define the search folder
#####################################################################################
#### Need to enter which folder we want to do the analysis                       ####
#### In this folder, we should be placed folder named Resonator_i_{frequency}GHz ####
#####################################################################################
folder_name = 'most_recent_data'

search_folder = current_dir / folder_name
# List all directories in the search folder
chosen_resonators = [x for x in search_folder.glob("*") if x.is_dir()]
# Print the number of directories
print(f"There are {len(chosen_resonators)} folders in {search_folder}.")


# %% perform power sweep

for resonator_path in chosen_resonators:
  
  ################################################################################
  #### external_attenuation : the sum over the attenuation outside the fridge ####
  #### internal_attenuation : the sum over the attenuation inside the fridge  ####
  #### If we change the configuration of the system, we need to care about it ####
  ################################################################################
  external_attenuation = 0  
  internal_attenuation = -70 
  
  # Find all the raw data in csv file
  all_resonator_csvs_paths = [x for x in resonator_path.glob("*GHz*.csv")]
  all_resonator_csvs_names = [x.name for x in all_resonator_csvs_paths]

  ##########################################
  #### Define the temperature by manual ####
  ##########################################
  temperature = 10 # in mK
  
  all_powers = [hm.get_power_from_filename(fname) for fname in all_resonator_csvs_names if 'dBm' in fname] 
  
  # placeholder
  init_conds = [None]*len(all_resonator_csvs_names)

  all_fits_save_dir = str(resonator_path)
  qiqc_fit_save_dir = str(resonator_path)
  save_fit_dirs = [all_fits_save_dir, qiqc_fit_save_dir]
  print(all_resonator_csvs_names)
  
  hf.power_sweep_fit_drv(
    # IMPORTANT SETTINGS
    sample_name=sample_name,
    temperature=temperature,
    powers_in=all_powers, 
    all_paths=all_resonator_csvs_paths, 
    atten=[external_attenuation, internal_attenuation], 
    save_fit_dirs=save_fit_dirs, 
    data_dir=resonator_path, 
    
    # perform tan delta loss fit!! 
    plot_fit=True,
    plot_extra=False,
    save_dcm_plot=False, 
    show_plots=False,
    
    # NOT VERY IMPORTANT
    use_error_bars=True, temp_correction='', phi0=0.,
    use_gauss_filt=False, use_matched_filt=False,
    use_elliptic_filt=False, use_mov_avg_filt=False,
    # use_gauss_filt=True, use_matched_filt=True,
    # use_elliptic_filt=True, use_mov_avg_filt=True,
    loss_scale=1e-6, preprocess_method='circle',
    ds = {'QHP' : 1.288e5, 'nc' : 520, 'Fdtls' : 1.284e-6},
    plot_twinx=False,  QHP_fix=True, 
    manual_init_list=init_conds,
    # show_dbm=True
    show_dbm=False
    )

  plt.show()

# %%
