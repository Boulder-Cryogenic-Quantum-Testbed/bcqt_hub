"""
    PID Controller using the open loop control on the Janis
    gas handling control system.

    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    Original Author: Nick Materise
    Date:   09/21/19
    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

    Transcribed & truncated by Jorge Ramirez on 1/15/2024

    Renamed from "janis_ctrl.py" to "ghs_ctrl.py" to keep the two
    versions distinct. This code was written from the ground up 
    by graciously copying and pasting sections of janis_ctrl.py
    with the intention of "flattening" the code structure

    i.e. by turning this ctrl script into a driver, I've removed
    all code that does not directly interface with the dilution
    refrigerator or its sensors. All code that sweeps, loops, 
    fits, etc, will be moved to another directory.

"""

## %% imports
import sys, os
import socket, time

from datetime import datetime
from pathlib import Path


### TODO: fix imports
sys.path.append(r"C:\Users\Lehnert Lab\GitHub")

import bcqt_hub.experiments.quick_helpers as qh
from bcqt_hub.bcqt_hub.drivers.instruments.VNA_Keysight import VNA_Keysight



class GHS_Controller():
    """
        scope:
            sending cmds & receiving data from
                - temp, water, pressure, valve sensors
                - Janis Automated Control Box (JACOB)
                
    """
    
    
    ### TODO: fix this garbage initialization
        #  - remove bypass entirely? idk it was helpful for when the code broke, since 
        # if a connection failed then it couldnt measure
    def __init__(self, TCP_IP='192.168.0.111', TCP_PORT='5559',  VNA_IP='TCPIP0::192.168.0.105::inst0::INSTR', init_socket=True, bypass_janis=False, verbose=True):
        
        # default IP addresses and ports, as well as init_socket
        #      which allows the user to init without connecting
        # TODO: grab these parameters from bcqt_instruments.json
        
        self.TCP_IP = TCP_IP  
        self.TCP_PORT = int(TCP_PORT)
        self.VNA_IP = VNA_IP
        self.init_socket = init_socket
        self.bypass_janis = bypass_janis
        self.verbose = verbose

        # Expected base temperature of the fridge 
        self.T_base = 0.011
        
        # timestamp
        self.dstr = datetime.today().strftime('%m%d_%I%M%p')
        
        # the labels for each channel on the Lakeshore Temp Controller
        self.channel_dict = {'50K'     : 1, '10K'    : 2, '3K'  : 3,
                             'JT'      : 4, 'still'  : 5, 'ICP' : 6,
                             'MC JRS'  : 7, 'Cernox' : 8, 'CMN' : 9,}
        
        if self.verbose: 
            self.print_console(f" Initializing JanisCtrl object:")
            self.print_console(f"      {self.dstr = }:")
            self.print_console(f"      {self.VNA_IP = }:")
            self.print_console(f"      FakeJacob {self.TCP_IP = }")
            self.print_console(f"                {self.TCP_PORT = }")
        
        if self.bypass_janis is True:
            self.print_console(f"Note!! {self.bypass_janis = }")
            time.sleep(2)
        
        
        # Create socket connection to the Janis Gas Handling System
        if self.init_socket and (not self.bypass_janis):
            # if self.verbose is True: 
            self.print_console("\nNow connecting to Janis GHS (fakejacob)...\n")
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.TCP_IP, self.TCP_PORT))
            
            # host = socket.gethostbyname("localhost")  #Note the extra letters "by"
            # self.socket.bind((host, self.TCP_PORT))
            
    def __del__(self):
        # When object is deleted, close socket to save resources
        # Set the current to zero and close the socket connection
        if self.verbose: self.print_console('Calling destructor ...')
        self.close_socket()
        
        
    def close_socket(self):
        if self.socket is not None:
            if self.verbose is True: 
                self.print_console('Setting current to 0 ...')
            # self.set_current(0.)   # TODO: causing crashes?
            self.socket.close()
            self.socket = None
        else:
            self.print_console(f'Socket already closed? ({self.socket=})')
        
        
    def reset_socket(self):
        if self.socket is not None:
            self.print_console(f'Resetting socket ...')
            self.socket.close()
            self.socket = None
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.TCP_IP, self.TCP_PORT))
        else:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.TCP_IP, self.TCP_PORT))
        
    def tcp_send(self, message):
        length = len(message)
        length = length.to_bytes(4, 'big')
        exceptions = (socket.error, socket.error, KeyboardInterrupt, Exception)
        try:
            self.socket.send(length)
            self.socket.send(message.encode('ASCII'))
        except exceptions as error:
            raise RuntimeError(f'tcp_send: {error}')
    
    
    def tcp_recv(self):
        exceptions = (socket.error, socket.error, KeyboardInterrupt, Exception)
        try:
            buffer = self.socket.recv(4)
        except exceptions as error:
            raise RuntimeError(f'tcp_recv: {error}')

        buffer = int.from_bytes(buffer, 'big')
        data = self.socket.recv(buffer)
        data = data.decode('ascii')
        return data
    

    def read_temp_lakeshore(self, print_output=True):
        """
            Reads the temperature of one of the channels from the Lakeshore
            
            Instead of asking for a channel_name, this will now always return
                a dictionary with every channel reading
        """
        if self.bypass_janis:
            return '-1', '-1'
            
        temp_dict = {}
        for ch_name, ch in self.channel_dict.items():
            
            impedance, temp, timestamp, status = data.split(',')
            self.tcp_send(f'readTemp({ch})')
            data = self.tcp_recv()
            temp, timestamp, status = data.split(',')
            timestamp = timestamp.split(' ')
            timestamp = timestamp[0].split('.')[0]
            timestamp_formatted = datetime.strptime(timestamp, "%H:%M:%S")
            
            status = bool(status)
            temp = float(temp) 
            if print_output is True:
                self.print_console(f'{timestamp_formatted}, {ch_name}: {temp:.4g} K')
            temp_dict[ch_name] = temp
            
            if status is False:
                self.print_console(f'tcp_send(read_temp_lakeshore({ch})) failed with status: {status}')
                return '-1', '-1'
        
        return temp_dict, timestamp_formatted
        
            
    def read_temp_cmn(self):
        """
            Reads just the CMN temperature sensor for convenience
                and backwards compatability
        """
        if self.bypass_janis:
            return None
        
        temp_dict, timestamp_formatted = self.read_temp_lakeshore(print_output=False)

        return temp_dict["CMN"], timestamp_formatted


    def read_flow_meter(self):
        """
            Reads the flow meter and returns the flow rate in umol / s, and
            the timestamp
        """
        
        if self.bypass_janis:
            return -1, -1
        
        self.tcp_send('readFlow(1)')
        data = self.tcp_recv()
        flow_V, flow_umol_s, timestamp, status = data.split(',')
        timestamp = timestamp.split(' ')
        timestamp = timestamp[0].split('.')[0]
        timestamp_formatted = datetime.strptime(timestamp, "%H:%M:%S")
        
        status = bool(status)
        flow_umol_s = float(flow_umol_s)
        
        if status is True:
            return flow_umol_s, timestamp_formatted
        else:
            self.print_console(f'tcp_send(readFlow(1)) failed with status: {status}')
            return '-1', '-1'

    def read_pressure(self, print_output=True):
        """
            Reads the pressure of one of the channels from the Lakeshore
        """
        
        if self.bypass_janis:
            return '-1', '-1'
        
        pressure_dict = {}
        all_channels = [1, 2, 3, 4]
        for ch in all_channels:
            self.tcp_send(f'readPressure({ch})')
            data = self.tcp_recv()
            P_volt, P_mbar, timestamp, status = data.split(',')
            timestamp = timestamp.split(' ')
            timestamp = timestamp[0].split('.')[0]
            timestamp_formatted = datetime.strptime(timestamp, "%H:%M:%S")
            
            P_mbar = float(P_mbar)
            status = bool(status)
            
            pressure_dict[f"G{ch}"] = P_mbar
            
            if print_output is True:
                self.print_console(f'{timestamp_formatted}, G{ch}: {P_mbar:.4e} mbar')
            
        return pressure_dict, timestamp_formatted



    # def get_heater_rng_lvl(self, x):
    #     """
    #         This function takes the pid output (Current in mA) and
    #         converts it to heater settings. Used in set_mxc_current
    #     """
    #     if abs(x - 0) < 1e-8:
    #         Range = 0
    #         level = 0
    #     elif x < 0.0316:
    #         Range = 1
    #         level = x*100/0.0316
    #     elif 0.0316 < x <= 0.1:
    #         Range = 2
    #         level = x*100/0.1
    #     elif 0.1 < x <= 0.316:
    #         Range = 3
    #         level = x*100/0.316
    #     elif 0.316 < x <= 1.0:
    #         Range = 4
    #         level = x*100/1.0
    #     elif 1.0 < x <= 3.16:
    #         Range = 5
    #         level = x*100/3.16
    #     # Extended ranges added on 211111
    #     elif 3.16 < x <= 10:
    #         Range = 6
    #         level = x*100/10
    #     elif 10 < x <= 31.6:
    #         Range = 7
    #         level = x*100/31.6
    #     elif 31.6 < x <= 100:
    #         Range = 8
    #         level = x*100/100
    #     else:
    #         self.print_console("DON'T MELT THE FRIDGE")
    #         Range = 0
    #         level = 0
    #     return Range, level
    
    # # TODO: handle output from these cmds
    # def set_mxc_current(self, current_mA):
    #     """
    #         Uses self.get_heater_rng_lvl to convert
    #             current_mA to percentage output
                
    #         [Jorge] note, changed the first parameter from 
    #             1 (HW PID) to 3 (Open Loop). I dont intend
    #             to use PID control in the near future
    #     """
    #     Range, level = self.get_heater_rng_lvl(current_mA)
    #     self.tcp_send(f'setHtrCntrlModeOpenLoop(3,{level},{Range})')
    #     _ = self.tcp_recv()  

    # def set_still_heater_voltage(self, voltage):
    #     """
    #         Sets the still heater voltage
    #     """
    #     # Check that the voltage is zero
    #     if voltage < 1e-6:
    #         self.print_console('Turning off still heater')
    #         self.tcp_send(f'setHtrCntrlModeOpenLoop(2, 0, 0)')
    #         _ = self.tcp_recv()
    #     else:
    #         self.print_console(f'Turning on still heater with {voltage} V ...')
    #         self.tcp_send(f'setHtrCntrlModeOpenLoop(2, {voltage}, {max(voltage, 3)})')
    #         _ = self.tcp_recv()


    # TODO: read GHS_Manual in the bcqt google drive, and look through the interestin
    #           cmds in section 10.3.3. Some that might be interesting are:
    #
    #               - readHtrPwr, setHtrRange
    #               - getErrorText (XXX)
    #               - readValveStatus
    #               - setLogging, getLoggingState (XXX)


    ############################
    #####  Helper methods  #####
    ############################


    def print_console(self, msg : str = "", prefix : str = None, **kwargs):
        if prefix is None:
            new_msg = f"[GHS_Controller]  {msg.replace("\n","")}".strip()
        else:
            new_msg = f"[GHS_Controller]  {prefix} {msg.replace("\n","")}".strip()
        
        if msg[:1] == "\n":
            self.print_console()  # print an empty line with prefix
            print(new_msg, **kwargs)
        else:   
            print(new_msg, **kwargs)
            
    def print_debug(self, msg : str = "", **kwargs):
        if self.debug is True:
            self.print_console(msg, prefix=" **[DEBUG]  ", **kwargs)
        
        

# debug
if __name__ == "__main__":
    
    ghs_test = GHS_Controller()
    
    