import time, datetime

from ..BaseDriver import BaseDriver


class SA_RnS_FSEB20(BaseDriver):

    def __init__(self, InstrConfig_Dict, instr_resource=None, instr_address=None, debug=False, **kwargs):
        super().__init__(InstrConfig_Dict, instr_resource, instr_address, debug, **kwargs)
        self.write_check("TRIG:SOUR IMM")   # TODO: ???
          
    def read_check(self, fmt = str):
        return super().read_check(fmt=fmt)
    
    def write_check(self, cmd: str):
        return super().write_check(cmd=cmd)
    
    def query_check(self, cmd: str, fmt = str):
        return super().query_check(cmd=cmd, fmt=fmt)
    
    def check_instr_error_queue(self, print_output=False):
        return super().check_instr_error_queue(print_output)
    
    def return_instrument_parameters(self, print_output=False):
        return super().return_instrument_parameters(print_output)
    
        
    def strip_specials(self, ret):
        return ret.replace("\\r","").replace("\\n","")

    
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # ~~~  get/set Instr Parameters
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    def get_IF_bandwidth(self, fmt=float):
        return self.query_check('SENS:BAND?', fmt=fmt)

    def set_IF_bandwidth(self, IFBW):
        self.write_check(f'SENS:BAND {IFBW}')
        setBwHz = self.get_IF_bandwidth()
        if self.debug is True:
            self.print_console(f'    Set spectrum analyzer IF bandwidth = {setBwHz} Hz')
    
    
    # ~~~~

    def get_freq_center_Hz(self, fmt=float):
        return self.query_check('FREQ:CENT?', fmt=fmt)
        
    def set_freq_center_Hz(self, freq_center_Hz):
        self.write_check(f'FREQ:CENT {freq_center_Hz} Hz')
        setCenterFreqHz = self.get_freq_center_Hz()
        if self.debug is True:
            self.print_console(f'    Set spectrum analyzer center freq = {setCenterFreqHz} Hz')
    
    # ~~~~
    
    def get_freq_span_Hz(self, fmt=float):
        return self.query_check('FREQ:SPAN?', fmt=fmt)
    
    def set_freq_span_Hz(self, freq_span_Hz):
        self.write_check(f'FREQ:SPAN {freq_span_Hz}')
        setFreqSpanHz = self.get_freq_span_Hz()
        if self.debug is True:
            self.print_console(f'Set spectrum analyzer freq span = {setFreqSpanHz} Hz')
    

    # ~~~~
    
    def set_num_averages(self, fmt=int):
        return self.query_check('AVER:COUN?', fmt=fmt)

    def set_num_averages(self, numAvg):
        self.write_check(f'AVER:COUN {numAvg}')
        setNumAvg = self.set_num_averages()
        if self.debug is True:
            self.print_console(f'Set spectrum analyzer averaging = {setNumAvg}')
    

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # ~~~  Instr Methods
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


    def toggle_continuous_sweep(self, sweep_mode : bool = None):
        if sweep_mode is None: 
            currentState = self.query_check('INIT:CONT?')[0]
            self.print_debug(f"{currentState=}")
            newState = "ON" if currentState == '0' else "OFF"
        else:
            newState = "ON" if sweep_mode == True else "OFF"
            
        self.write_check(f'INIT:CONT {newState}' )
        continuousSweepState = self.query_check('INIT:CONT?')
        if self.debug is True:
            self.print_console(f'    Continuous sweep mode = {continuousSweepState}')
    

    def set_averaging(self, num_averages : int ):
        self.write_check(f'AVER {num_averages}')
        setAvgState = self.query_check('AVER:COUN?')
        if self.debug is True:
            self.print_console(f'    Set spectrum analyzer averaging = {setAvgState}')

    def trigger_sweep(self):
        
        dstr = datetime.datetime.today().strftime("%m/%d/%Y @ %I:%M%p")
        
        sweep_time = float(self.strip_specials(self.query_check("SENSE:SWE:TIME?")))
        self.print_debug(f"{sweep_time = }")
        
        self.write_check("*TRG")
        self.write_check('INIT:DISP ON')
        time.sleep(sweep_time)
        
        check = False
        tstart = time.time()   
        while check is False:
            time.sleep(0.5)
            t_elapsed = time.time() - tstart
            print(f"\n      Time elapsed: [{t_elapsed:1.2f}s]", end="\r")
            
            # check_str is a string, "0" = busy or "1" = complete
            check_str = self.query_check('STAT:OPER:COND?')[1]
            self.print_debug(f"{check_str = }")

            # once it is "1", print that we're finished
            if check_str != "0":
                print(f"\n[{dstr}] Trace finished. Uploading now.")
                print(f"\n   Total time elapsed: {t_elapsed:1.2f} seconds", end="\r")
                if t_elapsed >= 600:
                    print(f"                     = {t_elapsed/60:1.1f} minutes \n")
                
                # update the variable and let the while finish
                check = bool(check_str)
        
        # finish off by turning off scanning
        self.write_check('INIT:CONT OFF')
            
    
    def send_marker_to_max(self):
        self.write_check('CALC:MARK:MAX')
        if self.debug is True:
            self.print_console('    Marker set to max peak')


    def read_marker_freq_amp(self):
        markerFreqHz = self.query_check('CALC:MARK:X?')
        markerAmpldBm = self.query_check('CALC:MARK:Y?')
        
        if self.debug is True:
            self.print_console(f'    Marker: freq = {markerFreqHz} MHz\tamp = {markerAmpldBm} dBm')
        
        return markerFreqHz, markerAmpldBm
         
         
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # ~~~  Instr Scripts
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        
    def return_data(self, trace_num=1):
        
        traceStr = self.query_check(f'TRAC:DATA? TRACE{trace_num}')
        traceData = [float(x) for x in traceStr.split(',')]
        
        return traceData
    
    
         
if __name__ == '__main__':
    
    # %load_ext autoreload
    # %autoreload 2 
    
    SA_RnS_InstrConfig = {
        "instrument_name" : "SA_RnS",
        "rm_backend" : None,
        "instr_address" : 'GPIB::20::INSTR',  
        
    }
    
    test_SA = SA_RnS_FSEB20(SA_RnS_InstrConfig, debug=True)
    test_SA.check_instr_error_queue()
    msg = test_SA.idn
    test_SA.print_console(msg, prefix="self.write(*IDN?) ->")
    
    test_SA.print_class_members()
    
    display(test_SA.query_check("*IDN?"))
    
    ##
    
    method_list = [func for func in dir(test_SA) if callable(getattr(test_SA, func)) and "get" in func and "__" not in func] 
    display(method_list)

    callable_method_list = [getattr(test_SA, func) for func in method_list]
    display(callable_method_list)

    for method in method_list:
        func = getattr(test_SA, method) 
        try:
            test_SA.print_console(f"testing:  {method}")
        except pyvisa.VisaIOError as e:
            print("failed: \n")
            print(e)
            
        result = func()
        display(result)
        