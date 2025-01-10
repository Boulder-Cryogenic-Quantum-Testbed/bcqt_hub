# quick_methods

# hopefully this isnt permanent :D

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy as sp
from datetime import datetime
from pathlib import Path

def archive_data(VNA, s2p_df:pd.DataFrame, meas_name:str, expt_category:str = '', save_dir:str = "./data", all_axes=None):
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

def load_csv(filepath):
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


## TODO: these should go in the DataProcessor object
def unpack_df(df): 
    freqs = df["Frequency"]
    try:
        magn_dB = df["S21 [dB]"]
    except:
        magn_dB = df["S21 magn_dB"]
        
    try:
        phase_rad = df["Phase [rad]"]
    except:
        phase_rad = df["S21 phase_rad"]
        
    return freqs, magn_dB, phase_rad

def strip_first_row_datetimes(df):
    # use .loc to get the index="datetime.now()", value is identical for all cols
    timestamp = df.loc["datetime.now()"].values[0]  
    
    # drop datetime from df once we have the timestamp
    stripped_df = df.drop(index='datetime.now()', inplace=False)
    
    return stripped_df, timestamp

def plot_s2p_df(df, axes=None, plot_complex=True, track_min=True, title="", do_edelay_fit=False,):
    
    """
        assumes df was returned by the VNA driver's 'return_data_s2p' function
            if not, the format of the df is simply:
                  | Frequency | 'sparam' magn_dB | 'sparam' phase_rad | ...
            for however many sparam columns 
            
        this will also check if there is a row with the index "datetime.now()" with
            the value of that function in each entry to use as the time
    """
    
    # remove first row of datetimes 
    try:
        fixed_df, timestamp = strip_first_row_datetimes(df)
    except:
        fixed_df = df
    
    for col in df:
        if "complex" in col:
            cmplx = fixed_df[col].astype(complex).values
            magn_lin = np.abs(cmplx)
            magn_dB = 20 * np.log10(magn_lin/1e3)
            phase_rad = np.angle(magn_lin)
            
            magn_dB_str = col.replace("complex", "magn_dB")
            phase_rad_str = col.replace("complex", "phase_rad")
            
            fixed_df[magn_dB_str] = np.log10(magn_dB)
            fixed_df[phase_rad_str] = np.log10(phase_rad)
            
            # remove original column
            fixed_df.drop(columns=col, inplace=True)
            
            fixed_df["Frequency"] = fixed_df["Frequency"].to_numpy().real 
    
    # grab the first three letters of each column
    # then remove duplicates so we have a list of all s-parameters
    all_col_sparams = [col[:3] for col in fixed_df.columns]
    sparams = list(set([x for x in all_col_sparams if all_col_sparams.count(x) > 1]))
    
    freqs = fixed_df["Frequency"].apply(lambda x: x.real)  # force freq to be a float

    # now go through all the s-parameters and grab the magn and phase data using filter()
    all_axes = []
    for sparam in sparams:
        magn_and_phase = fixed_df.filter(like=sparam)
        magn_dB, phase_rad =  magn_and_phase.iloc[:,0].values.astype(float), magn_and_phase.iloc[:,1].values.astype(float)
        axes = plot_data_with_pandas(freqs, magn_dB=magn_dB, phase_rad=phase_rad)

        fig = axes[0].get_figure()
        fig.suptitle(f"{sparam} - {title}", fontsize=18)
        fig.tight_layout()
        all_axes.append(axes)
        
    return all_axes
        

# TODO: add functionality for taking dataframes instead of individual np arrays
def plot_data_with_pandas(freqs=None, magn_dB=None, axes=None, phase_deg=None, phase_rad=None, plot_dict=None):

    # lazy way to pass custom args for separate plots
    if plot_dict is None:
        plot_complex=True 
        do_edelay_fit=False
        track_min=False
        suptitle=None
        magn_color = "r"   
        phase_color = "b"  
        magn_label = None
        phase_label = None
        
    else:
        plot_complex=plot_dict["plot_complex"] 
        do_edelay_fit=plot_dict["do_edelay_fit"] 
        track_min=plot_dict["track_min"] 
        suptitle=plot_dict["suptitle"] 
        magn_color = plot_dict["magn_color"]    
        phase_color = plot_dict["phase_color"]    
        magn_label = plot_dict["magn_label"]    
        phase_label = plot_dict["phase_label"]    
        
        
    if phase_rad is None and phase_deg is not None:
        # degrees were given
        phase_rad = np.unwrap(np.deg2rad(phase_deg))
    elif phase_rad is not None and phase_deg is None:
        # radians were given
        pass
    elif phase_rad is None and phase_deg is None:
        # both are None
        raise ValueError("One of phase_rad and phase_deg must be given!")
    else:
        # both were given
        if phase_rad != np.deg2rad(phase_deg):
            raise ValueError(f"Both radians and degrees were given, but they don't match!\n  {phase_rad != np.deg2rad(phase_deg) = }")
    
    ## convert dataset to linear, real, and imag
    magn_lin = 10**(magn_dB/20)
    cmpl = magn_lin * np.exp(1j * phase_rad)
    
    if do_edelay_fit is True:
        try:
            slope, intercept, _, _, _ = sp.stats.linregress(freqs, phase_rad - np.mean(phase_rad))  # force intercept = 0 by subtracting x_0
            edelay_correction = np.exp(1j * np.abs(slope) * freqs * 2*np.pi)
            plt.figure()
            plt.plot(freqs, phase_rad)
            plt.plot(freqs, slope*freqs+intercept)
            cmpl = cmpl * edelay_correction
            plt.plot(freqs, phase_rad)
            plt.show()
            print(f"{intercept=}")
            print(f"{slope*1e9=:1.3f}\n{slope=:1.3f}\n{slope*freqs[0]=:1.3f}\n{slope*freqs[-1]=:1.3f}")
        except Exception as e:
            print("Failed to do edelay correction, going back to regular phase_rad")
            print(e)
            
    # update values
    real, imag = np.real(cmpl), np.imag(cmpl)
    magn_lin = np.abs(cmpl)
    magn_dB, phase_rad = 20*np.log10(magn_lin), np.unwrap(np.angle(cmpl))

    # create a new plot or use one given as arg
    # # %% plot data
    
    if axes is None:
        mosaic = "AACC\nBBCC"
        fig, axes = plt.subplot_mosaic(mosaic, figsize=(13,5))
        ax1, ax2, ax3 = axes["A"], axes["B"], axes["C"]
        axes = [ax1, ax2, ax3]
    else:
        if axes is list:
            axes = axes[0]
        fig = axes[0].get_figure() 
        if len(axes) == 2:
            ax1, ax2 = axes
            ax3 = None
        elif len(axes) == 3:
            ax1, ax2, ax3 = axes
    
    if ax3 is not None:
        ax3.plot(real, imag, 'o', markersize=6)
        ax3.axhline(0, linestyle=':', linewidth=1, color='k')
        ax3.axvline(0, linestyle=':', linewidth=1, color='k')
        ax3.set_aspect("equal")
        ax3.set_title("Real vs Imag")
        ax3.set_xlabel("Real")
        ax3.set_ylabel("Imag")
    
    freq_argmin = magn_lin.argmin()
    freq_min = freqs[freq_argmin]

    if track_min is True:
        new_freqs = (freqs - freq_min)/1e3
        freq_min_label = f"$f_{"{min}"}$ = {freq_min/1e6:1.3f} MHz"
        ax1.axvline(0, linestyle='--', color='k', linewidth=1)
        ax2.axvline(0, linestyle='--', color='k', linewidth=1)
        if ax3 is not None:
            ax3.plot(real[freq_argmin], imag[freq_argmin], 'y*', markersize=8, label=freq_min_label)
        fig.legend(loc="upper left")
        ax1.set_xlabel("Frequency $\\Delta f$ [MHz]")
        ax2.set_xlabel("Frequency $\\Delta f$ [MHz]")
        ax1.set_title(f"Freq vs Magn [$f_{"{min}"}$ = {freq_min/1e9:1.6f} GHz]")
        ax2.set_title(f"Freq vs Phase [$f_{"{min}"}$ = {freq_min/1e9:1.6f} GHz]")
    else:
        new_freqs = freqs/1e9
        ax1.set_xlabel("Frequency [GHz]")
        ax2.set_xlabel("Frequency [GHz]")
        ax1.set_title(f"Frequency vs Magnitude")
        ax2.set_title(f"Frequency vs Phase")
    
    # magn and phase
    ax1.plot(new_freqs, magn_dB, ".", color=magn_color, markersize=3, label=magn_label)
    ax2.plot(new_freqs, phase_rad, ".", color=phase_color, markersize=3, label=phase_label)

    ax1.set_ylabel("S21 [dB]")
    ax2.set_ylabel("Phase [Rad]")
    
    if plot_complex is False:
        if ax3 is not None:
            fig.delaxes(ax3)
            x_title, y_title = 0.27, 0.98
        else:
            x_title, y_title = 0.5, 0.98
            
        axes = [ax1, ax2]
        
        
    if suptitle is not None:
        fig.suptitle(suptitle, fontsize=18, x=x_title, y=y_title)
        
    
    if plot_dict is not None and plot_dict["do_legend"] is True:
            ax1.legend()
        
    fig.tight_layout()
    
    return axes
