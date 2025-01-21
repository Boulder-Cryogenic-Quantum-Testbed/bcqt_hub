from datetime import datetime
import numpy as np
import pandas as pd
import time

from ..BaseDriver import BaseDriver



class VNA_Keysight(BaseDriver):
    
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # ~~~  Base Class Features
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def __init__(self, InstrConfig_Dict, instr_resource=None, instr_address=None, debug=False, **kwargs):
        super().__init__(InstrConfig_Dict, instr_resource, instr_address, debug, **kwargs)
        
    def read_check(self, fmt = str):
        return super().read_check(fmt)
    
    def write_check(self, cmd: str):
        return super().write_check(cmd=cmd)
    
    def query_check(self, cmd, fmt = str):
        return super().query_check(cmd, fmt)
    
    def check_instr_error_queue(self, print_output=False):
        return super().check_instr_error_queue(print_output)
    
    def return_instrument_parameters(self, print_output=False):
        return super().return_instrument_parameters(print_output)
    
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # ~~~  config dict methods
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    def init_configs(self):
        
        # create an empty config dict if missing
        if "configs" not in dir(self):
            self.configs = {}
        
        ############################
        #### fix any bad keys in configs
        ############################
        self.filter_configs()
        
        ############################
        #### s-parameters
        ############################
        self.print_debug("setting scattering params")
        self.update_sparam_configs()
        
        ############################
        #### freq bounds
        ############################
        self.determine_frequency_bounds()
        
    def update_configs(self, **kwargs):
        
        self.configs.update(kwargs)
        
        f_choices = [x for x in kwargs if x in ["f_center", "f_span", "f_start", "f_stop"]]
        if len(f_choices) == 1 or len(f_choices) == 2:
            f_choice = f_choices[0]
        else:
            self.print_debug("Found more than two choices from [f_center/f_span] and [f_start/f_stop]!")
            self.print_debug("Defaulting to [f_start/f_stop] for frequency bounds...")
            f_choice = 'f_start'
            
        self.determine_frequency_bounds(f_choice=f_choice)
        self.filter_configs()
        
    
    def update_sparam_configs(self):
        """
            look inside configs for s-param definition, and make sure that
                they are valid + are in a list, especially if there is only
                one s-parameter.
             
            also parses 'all' to all four s parameters.
        """
        
        if "sparam" in self.configs:
            measure_sparam = self.configs["sparam"]
        elif "sparams" in self.configs:
            measure_sparam = self.configs["sparams"]
            del self.configs["sparams"]
            
        # check if value is 'all' as shortcut for all sparameters
        if "all" in measure_sparam:
            measure_sparam = ['S11', 'S12', 'S21', 'S22']
            
        # turn sparam into a list 
        if not isinstance(measure_sparam, list):
            measure_sparam = [measure_sparam]
            
        # overwrite configs
        self.configs["sparam"] = measure_sparam
        
    
    def determine_frequency_bounds(self, f_choice=None):
        """
            Search configs for f_center/f_span, or f_start/f_stop,
                and then make sure that both pairs of values are
                saved to the config. Additionally return
        """
        # if f_choice is given, then use that to calculate start/stop/center/span
        if f_choice in ["f_center", "f_span"]:
            self.print_debug(f"[using center/span] {f_choice = }")
            try: del self.configs["f_start"], self.configs["f_stop"]
            except: pass
        elif f_choice in ["f_start", "f_stop"]:
            self.print_debug(f"[using start/stop] {f_choice = }")
            try: del self.configs["f_center"], self.configs["f_span"]
            except: pass
        
        # get bounds by looking for f_center/f_span or f_start/f_stop!
        if "f_center" in self.configs and "f_span" in self.configs:
            f_center, f_span = self.configs["f_center"], self.configs["f_span"]
            f_half_span = self.configs["f_span"] / 2
            f_start = self.configs["f_center"] - f_half_span
            f_stop = self.configs["f_center"] + f_half_span
        elif "f_start" in self.configs and "f_stop" in self.configs:
            f_start, f_stop = self.configs["f_start"], self.configs["f_stop"]
            f_span = f_stop - f_start
            f_center = f_start + f_span/2
        else:
            self.print_debug(f"Did not find a pair from [f_center, f_span] or [f_start, f_stop]")
            for var in ["f_start", "f_stop", "f_center", "f_span"]:
                try:
                    self.print_debug(self.configs[var])
                except:
                    self.print_debug(f"Did not find {var}")
            
        # set values in config and return a dict for convenience
        self.configs["f_start"] = f_start
        self.configs["f_stop"] = f_stop
        self.configs["f_center"] = f_center
        self.configs["f_span"] = f_span
        
        freq_bounds = {
            "f_start" : f_start,
            "f_stop" : f_stop,
            "f_center" : f_center,
            "f_span" : f_span,
        }
        
        self.configs.update(**freq_bounds)
    
    
    def filter_configs(self):
        # backwards compatability, remove lazy kwargs
        if "fc" in self.configs:
            self.configs["f_center"] = self.configs["fc"]
            del self.configs["fc"]
        if "span" in self.configs:
            self.configs["f_span"] = self.configs["span"]
            del self.configs["f_span"]
        for name in ["points", "n_pts"]:
            if name in self.configs:
                self.configs["n_points"] = self.configs[name]
                del self.configs[name]
        
        # check all kwargs if their equivalent without underscores exists
        #   e.g. check if 'fstart' exists, then replace it with 'f_start'
        entries_to_remove = []
        for name in self.configs: 
            if "_" in name:
                name_pruned = name.replace("_","")
                if name_pruned in self.configs:
                    self.print_console("")
                    self.configs[name] = self.configs[name_pruned]
                    entries_to_remove.append(name_pruned)
                
        # remove all
        for k in entries_to_remove:
            self.configs.pop(name_pruned)
        
        
        
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # ~~~  get/set Instr Parameters
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    
    def get_instr_params(self):
        
        """ 
            this method doesnt make any sense as it is - why not just get self.configs?
            the only way it should exist is if it actually asks the instrument what
            its parameters are, and that's what 'return_instrument_parameters' is for
        """
    
        return Exception("Not implemented, needs to call all 'get_xyz_param' methods")
        
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # ~~~  Instr Methods
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    
    # TODO: remove references to kwargs
    def compute_homophasal_segments(self, Noffres=None, segment_type=None, **kwargs):
        """
            Computes segments needed to perform homophasal measurements
                "segments" are just strings that contain the parameters
                for each frequency "slice" we are splitting our x-axis into
                
                A guide for the meaning of each part of the string
                    example = ', 1, {Noffres}, {fstop*fscale}, {fb}',
                              ', 1, <# of pts>, <start freq>, <stop freq>
        """
        
        if segment_type is None and "segment_type" in self.configs:
            segment_type = self.configs["segment_type"]
        else:
            segment_type = 'homophasal'
        
        if "Noffres" in self.configs:
            Noffres = self.configs["Noffres"]
        elif Noffres is None and "Noffres" not in self.configs:
            self.print_console("Using default Noffres = 5")
            Noffres = 5
        
        # load kwargs into vna configs
        self.filter_configs()
        
        f_center = self.configs["f_center"]
        f_span = self.configs["f_span"]
        n_points = self.configs["n_points"]
        
        # conversion factor for MHz -> Hz
        fscale = 1 if f_center >= 1e6 else 1e6
        
        # conversion factor for GHz -> Hz  (overwrites previous value for fscale)
        fscale = 1 if f_center >= 1e9 else 1e9
        
        # Estimate the number of linewidths per sweep
        Q = 20 * (f_center / f_span) 
        
        # Compute the frequencies
        fstart = f_center - f_span / 2
        fstop  = f_center + f_span / 2
        
        # determine homophasa  XXX: does it matter we always default to pi/32?
        theta0 = np.pi / 32
        Nf = 30 if n_points is None else n_points
        theta = np.linspace(-np.pi + theta0, (np.pi - theta0), Nf + 2)
        freq = f_center * (1 - 0.5 * np.tan(theta / 2) / Q)           
        
        if segment_type == 'homophasal':
            # homophasal for entire freq range
            segments = [f',1,2,{ff1*fscale},{ff2*fscale}'
                    for ff1, ff2 in zip(freq[0::2], freq[1::2])][1:-1]
        
        elif segment_type == 'hybrid':
            assert self.configs["Noffres"] is not None
            
            # split between homophasal and linear
            #   homophasal near resonance   freqs = [fa->fb]
            #   linear off resonance        freqs = [fstart->fa] and [fb->fstop]
            h_segments = [f',1,2,{ff1*fscale},{ff2*fscale}'
                    for ff1, ff2 in zip(freq[0::2], freq[1::2])][1:-1]
            fa = np.min(freq[1:-1]) * fscale
            fb = np.max(freq[1:-1]) * fscale

            segments = [f',1,{Noffres},{fstop*fscale}, {fb}',
                        *h_segments,
                        f',1,{Noffres},{fa},{fstart*fscale}']
            
        elif segment_type == 'linear':
            # simple linear sweep
            segments = [f',1,{n_points},{fstop*fscale}, {fstart*fscale}']
            
        else:
            raise ValueError("Missing segment_type in compute_homophasal_segments for VNA_Keysight driver.")
            
        self.configs["segments"] = segments
        return segments
    
    def setup_s2p_measurement(self, Expt_Config=None):
        """ 
            duplicate of setup_measurement, but with all 
                four sparameters instead of just s21
        """
        
        if Expt_Config is not None:
            self.print_console("Updating Expt_Config...")
            self.init_configs(Expt_Config)
        
        self.print_console("Initializing VNA for all four s-parameter measurement...")
        # self.write_check('*RST')
        # self.write_check('*CLS')

        # self.write_check('SYSTem:FPRESet')
        # self.write_check('SYSTem:UPRESet')
        time.sleep(0.05)
        self.write_check('OUTPut:STATe OFF')

        # Initial setup for measurement
        ## Query the existing measurements
        measurements = self.query_check('CALC1:PAR:CAT:EXTended?')

        ## If any measurements exist, delete them all
        if measurements != 'NO CATALOG':
            self.write_check('CALC1:PARameter:DELete:ALL')
        
        # just in case they have not been set yet, but should be by init_configs()
        measure_sparam = self.configs['sparam']
        
        # create measurements, create vna display windows, and set all of them to log format
        for idx, sparam in enumerate(measure_sparam):
            self.write_check(f'CALC1:MEASure{idx+1}:DEFine \"{sparam}\"')
            self.write_check(f'CALC1:PAR:MNUM {idx+1}')  # select ch
            self.write_check(f'DISPlay:WINDow{idx+1} ON')  # create window
            self.write_check(f'DISPlay:MEAS{idx+1}:FEED {idx+1}')  # display meas 1 on window 1
            self.write_check(f'CALC1:CORRection:EDELay:TIME {self.configs["edelay"]}NS')
            self.write_check(f'CALC1:MEASure{idx+1}:FORMat MLOGarithmic')
            
        # set frequency sweep
        if "segments" in self.configs and self.configs["segments"] is not None:
            num_segments = len(self.configs["segments"])
            seg_data = ''.join([s for s in self.configs["segments"]])
            self.write_check(f"SENSe1:SWEep:TYPE SEGment")
            self.write_check(f'SENSe1:SEGMent:LIST SSTOP, {num_segments}{seg_data}')
        else:
            self.write_check("SENSe1:SWEep:TYPE LINear")
            self.write_check(f'SENSe1:SWEep:POINts {self.configs["n_points"]}')
            self.write_check(f'SENSe1:FREQuency:CENTer {self.configs["f_center"]}HZ')
            self.write_check(f'SENSe1:FREQuency:SPAN {self.configs["f_span"]}HZ')
            self.write_check(f'SENSe1:SWEep:TIME:AUTO ON')
        
        # TODO: figure out how to set port1 and port2 both as inputs and outputs for s2p measurements 
        
        # raise NotImplemented
    
        self.write_check(f'SOUR1:POW1 {self.configs["power"]}')
        self.write_check(f'SENSe1:AVERage:STATe ON')
        self.write_check(f'SENSe1:AVERage:Count {self.configs["averages"] // 1}')
        self.write_check(f'SENSe1:BANDwidth {self.configs["if_bandwidth"]}HZ')

        # autoscale for visibility on the display
        # self.write_check(f'DISPlay:WINDow1:TRACe1:Y:SCAle:AUTO')
        # self.write_check(f'DISPlay:WINDow2:TRACe1:Y:SCAle:AUTO')


    def setup_measurement(self, Expt_Config=None):
        
        '''
            set parameters for the PNA for the sweep (number of points, center
            frequency, span of frequencies, IF bandwidth, power, electrical delay and
            number of averages)

            XXX: Do not change this order:

            1.  Define a measurement
            2.  Turn on display
            3.  Set the number of points
            4.  Set the center frequency, span
            5.  Turn on sweep time AUTO
            6.  Set the electrical delay
            7.  Turn on interpolation
            8.  Set the calibration
            9.  Set the power
            10. Turn on averaging
            11. Set the IF bandwidth

        '''
        
        if Expt_Config is not None:
            self.print_console("Updating Expt_Config...")
            self.init_configs(Expt_Config)
        
        self.print_console("Initializing VNA...")
        self.write_check('*RST')
        self.write_check('*CLS')

        # self.write_check('SYSTem:FPRESet')
        self.write_check('SYSTem:UPRESet')
        time.sleep(0.01)
        self.write_check('OUTPut:STATe OFF')

        # Initial setup for measurement
        ## Query the existing measurements
        measurements = self.query_check('CALC1:PAR:CAT:EXTended?')

        ## If any measurements exist, delete them all
        if measurements != 'NO CATALOG':
            self.write_check('CALC1:PARameter:DELete:ALL')
        
        # create measurements
        self.write_check(f'CALC1:MEASure1:DEFine \"{self.configs["sparam"]}\"')
        self.write_check(f'CALC1:MEASure2:DEFine \"{self.configs["sparam"]}\"')

        
        if self.configs["segments"] is not None:
            num_segments = len(self.configs["segments"])
            seg_data = ''.join([s for s in self.configs["segments"]])
            self.write_check(f"SENSe1:SWEep:TYPE SEGment")
            self.write_check(f'SENSe1:SEGMent:LIST SSTOP, {num_segments}{seg_data}')
        else:
            self.write_check("SENSe1:SWEep:TYPE LINear")
            self.write_check(f'SENSe1:SWEep:POINts {self.configs["n_points"]}')
            self.write_check(f'SENSe1:FREQuency:CENTer {self.configs["f_center"]}HZ')
            self.write_check(f'SENSe1:FREQuency:SPAN {self.configs["f_span"]}HZ')
            self.write_check(f'SENSe1:SWEep:TIME:AUTO ON')
        
        self.write_check(f'SOUR1:POW1 {self.configs["power"]}')
        self.write_check(f'SENSe1:AVERage:STATe ON')
        self.write_check(f'SENSe1:BANDwidth {self.configs["if_bandwidth"]}HZ')

        # configure ch 1 measurement 1
        self.write_check(f'CALC1:PAR:MNUM 1')  # select ch 1, meas 1
        self.write_check(f'DISPlay:WINDow1 ON')  # create window
        self.write_check(f'DISPlay:MEAS1:FEED 1')  # display meas 1 on window 1
        self.write_check(f'CALC1:CORRection:EDELay:TIME {self.configs["edelay"]}NS')
        self.write_check(f'CALC1:MEASure1:FORMat MLOGarithmic')

        # configure ch 1 measurement 2
        self.write_check(f'CALC1:PAR:MNUM 2')  # select ch 1, meas 2
        self.write_check(f'DISPlay:WINDow2 ON')  # create window 2
        self.write_check(f'DISPlay:MEAS2:FEED 2')  # display meas 2 on window 2
        self.write_check(f'CALC1:CORRection:EDELay:TIME {self.configs["edelay"]}NS')
        self.write_check(f'CALC1:MEASure2:FORMat PHASe')

        # autoscale for visibility on the display
        self.write_check(f'DISPlay:WINDow1:TRACe1:Y:SCAle:AUTO')
        self.write_check(f'DISPlay:WINDow2:TRACe1:Y:SCAle:AUTO')

        # make sure to have averages as an integer
        self.write_check(f'SENSe1:AVERage:Count {self.configs["averages"] // 1}')

    
    def run_measurement(self):
        """
            Run the measurement and continuously query until it reports finished
        """
        dstr = datetime.today().strftime("%m/%d/%Y @ %I:%M%p")
        
        self.write_check('*CLS')
        
        # initiate display and turn on output
        self.write_check('OUTPut:STATe ON')
        self.write_check('INITiate:CONTinuous OFF')
        self.write_check('FORMat ASCII')
        self.write_check('DISPlay:WINDow1:Y:AUTO')
        self.write_check('DISPlay:WINDow2:Y:AUTO')
    
        # self.write_check('SENS1:SWE:MODE SINGle')  
        # self.write_check('INIT:IMM')  # just use INIT:IMM to trigger one sweep
        self.write_check('INITiate:CONTinuous ON')
        
        # initiate display and turn on output
        self.write_check('FORMat ASCII')
        self.write_check('DISPlay:WINDow1:Y:AUTO')
        self.write_check('DISPlay:WINDow2:Y:AUTO')
                
        # check if the VNA has finished every second, in my experience the *OPC? or *WAI command isnt very reliable
        check = False
        tstart = time.time()   
        
        print()
        self.print_console(f"Beginning measurement at {dstr}")
        while check is False:
            time.sleep(0.5)
            t_elapsed = time.time() - tstart
            
            # check_str is a string, "0" = busy or "1" = complete
            check_str = self.strip_specials(self.query_check('STAT:OPER:AVER1:COND?'))[0]
            print(f"      Time elapsed: [{t_elapsed:1.1f}s]", end="\r")
            
            # once it is "1", print that we're finished
            if check_str != "0":
                dstr_end = datetime.today().strftime("%m/%d/%Y @ %I:%M%p")
                print(f"\n[{dstr_end}] Trace finished. Uploading now.")
                print(f"\n   Total time elapsed: {t_elapsed:1.2f} seconds")
                if t_elapsed >= 600:
                    print(f"                     = {t_elapsed/60:1.1f} minutes \n")
                
                # update the variable and let the while finish
                check = bool(check_str)
            
        # self.write_check('OUTPut:STATe OFF')
        # self.write_check('INITiate:CONTinuous OFF')


    # TODO: only written like this to not break previous scripts
    #         need to fix across the board!!
    def return_data(self):

        print("########################################################################")##")
        print("########################################################################")#")
        print("###############  return_data will be changed to return #################")
        print("###############   a dict of all datasetes, instead of  #################")
        print("###############       just (freqs, magn, phase)!!!     #################")
        print("########################################################################")###")
        print("########################################################################")###")
        
        data_dict = self.return_data_s2p()
        
        if len(data_dict) == 1:
            sparam = data_dict.keys()  # only one key, probably s21
            freqs, magn, phase = data_dict[sparam]
        else:
            print("called return_data but measuring more than one sparam... use return_data_s2p()")
            return self.return_data_s2p()
        
        return freqs, magn, phase
    
    def return_data_s2p(self, archive_complex=False):
        
        """
            Transfer data from VNA to PC, organized into a dict
              with each key as the s-parameter and the value
               equal to [freqs, magn_dB, phase_rad]
        """
        
        if "segments" in self.configs and self.configs["segments"] is not None:
            # Read the list of all segments
            freqs = np.array([])
            for s in self.configs["segments"]:
                ssplit = s.replace(" ", "").split(',')
                
                # int() doesnt want a string of a float like '12.0', so if it has  
                # a decimal point, turn it into a float first
                nf = int(ssplit[2]) if '.' not in ssplit[2] else int(float(ssplit[2]))  
                f1 = float(ssplit[3])
                f2 = float(ssplit[4])
                f = np.linspace(f1, f2, nf)
                freqs = np.hstack((freqs, f))
        else:
            n_points = self.query_check(f'SENSe1:SWEep:POINts?', fmt=int)
            f_start = self.query_check('SENSe1:FREQuency:START?', fmt=float)
            f_stop = self.query_check('SENSe1:FREQuency:STOP?', fmt=float)
            freqs = np.linspace(f_start, f_stop, n_points)
        
        self.update_sparam_configs()
        
        data_dict = {}
        for idx, sparam in enumerate(self.configs["sparam"]):
            self.print_console(f"[{idx+1}/{len(self.configs["sparam"])}] Downloading {sparam} from VNA ")
            # read in magn
            self.write_check(f'CALC1:PAR:MNUM {idx+1}')  # select ch 1, meas (idx+1)
            self.write_check('CALC1:FORMat UPHASe') # read in the unwrapped phase
            phase = self.query_check_ascii('CALC1:DATA? FDATA', container=np.array)
            self.write_check('CALC1:FORMat MLOG') # read in the magn_dB
            magn_dB = self.query_check_ascii('CALC1:DATA? FDATA', container=np.array)
            phase_rad = np.deg2rad(phase)
                    
            # possible to use CALC:DATA:MFD? "1,2,3,4" which returns traces 1->4

            data_dict[sparam] = [freqs, magn_dB, phase_rad]
        
        ############################################################
        ### used to be its own function, 'make_dfs', but decided to 
        ### merge with return_data_s2p 
        ############################################################
        
        """
            takes a dict whose values are lists of 3 np.arrays 
                and the keys correspond to the associated sparam
                i.e.
                    "sparam" : [freq, magn, phase_rad]
            aka the output of return_data_s2p
            
            returns 
                df : single dataframe with 'freqs' as the first col 
                        followed by magn/phase data of each entry
                e.g.
                  | freqs | 'sparam' Magn_dB | 'sparam' Phase_rad | ...
        """
        
        all_dfs = []
        for sparam, (freqs, magn_dB, phase_rad) in data_dict.items():
            if archive_complex is False:
                all_arrays = np.array([freqs, magn_dB, phase_rad])
                all_columns = ["Frequency", f"{sparam} magn_dB", f"{sparam} phase_rad"]
            else:
                magn_lin = 10**(magn_dB/20)
                cmplx = magn_lin * np.exp(1j*phase_rad)
                all_arrays = np.array([freqs, cmplx])
                all_columns = ["Frequency", f"{sparam} complex"]
            df = pd.DataFrame.from_records(all_arrays.T, columns=all_columns)
            df.apply(lambda x: np.real(x))
            all_dfs.append(df)
            
        # every day I grow resentful of pandas for making my life harder for no reason
        # merge, join, concat, pd.DataFrame... and in the end I had to google this crap
        # just to have the first column be 'frequency' and the rest the data........ >:(
        combined_df = pd.concat(all_dfs, axis=1)
        combined_df = combined_df.loc[:,~combined_df.columns.duplicated()].copy()
    
        # add datetime to first row for archiving purposes
        # first_row = {col : val for col, val in zip(combined_df.columns, [datetime.now()]*len(combined_df.columns))}
        # datetime_row = pd.DataFrame(first_row, index=["datetime.now()"])
        # final_df = pd.concat([datetime_row, combined_df.iloc[:]])
        
        
        return combined_df
    
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # ~~~  Instr Scripts
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def take_single_trace(self, Expt_Config = None):
        """
            (0) before running this, the instrument should already have 
                - init_configs()
                - setup_measurement()
            (1)
        """
        # self.print_debug("Taking Single Trace")
        
        # TODO: separate "instr_config" and "expt_config"
        # if self.configs is None and Expt_Config is not None: 
        #     self.print_debug("Updating ExptConfig")
        #     self.configs = Expt_Config
        #
        # self.configs["segments"] = self.compute_homophasal_segments(**self.configs)
        # self.init_configs(Expt_Config)
        # self.get_instr_params()
        # self.setup_measurement()
        # self.check_instr_error_queue()
        # self.run_measurement() 
        # freqs, magn_dB, phase_deg = self.return_data()
        
        # self.print_debug("Finished Taking Trace")
        
        # return freqs, magn_dB, phase_deg
        raise NotImplemented