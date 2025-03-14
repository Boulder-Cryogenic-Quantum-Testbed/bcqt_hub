from bcqt_hub.drivers.BaseDriver import BaseDriver


import math, copy

"""

    took a bunch of useful methods from:
        https://github.com/psmd-iberutaru/Keysight-E3631A-Python/blob/master/Keysight_E3631A.py

    however, that is for the older E3631A. Here is the manual for the new E36311A we have -
        https://www.keysight.com/us/en/assets/9921-01393/programming-guides/EDU36311A-DC-Power-Supply-Programming-Guide.pdf

"""

# These are constant values used for checking and establishing 
# power supply limits.
# These values are obtained from the factory manufactor. See 
# http://literature.cdn.keysight.com/litweb/pdf/E3631-90002.pdf#page=186&zoom=100,177,108

_FACTORY_MIN_CH1_VOLTAGE = 0.0      # P6V
_FACTORY_MAX_CH1_VOLTAGE = 6.18
_FACTORY_MIN_CH2_VOLTAGE = 0.0      # P30V
_FACTORY_MAX_CH2_VOLTAGE = 30.9
_FACTORY_MIN_CH3_VOLTAGE = 0.0      # N30V
_FACTORY_MAX_CH3_VOLTAGE = 30.9

_FACTORY_MIN_CH1_CURRENT = 0.002    # P6V
_FACTORY_MAX_CH1_CURRENT = 5.15
_FACTORY_MIN_CH2_CURRENT = 0.001    # P30V
_FACTORY_MAX_CH2_CURRENT = 1.03    
_FACTORY_MIN_CH3_CURRENT = 0.001    # N30V
_FACTORY_MAX_CH3_CURRENT = 1.03


# These values are user created limitations to the output of the
# power supply. Default to the factory limitations.
_USER_MIN_CH1_VOLTAGE = copy.deepcopy(_FACTORY_MIN_CH1_VOLTAGE)
_USER_MAX_CH1_VOLTAGE = copy.deepcopy(_FACTORY_MAX_CH1_VOLTAGE)
_USER_MIN_CH2_VOLTAGE = copy.deepcopy(_FACTORY_MIN_CH2_VOLTAGE)
_USER_MAX_CH2_VOLTAGE = copy.deepcopy(_FACTORY_MAX_CH2_VOLTAGE)
_USER_MIN_CH3_VOLTAGE = copy.deepcopy(_FACTORY_MIN_CH2_VOLTAGE)
_USER_MAX_CH3_VOLTAGE = copy.deepcopy(_FACTORY_MAX_CH2_VOLTAGE)

_USER_MIN_CH1_CURRENT = copy.deepcopy(_FACTORY_MIN_CH1_CURRENT)
_USER_MAX_CH1_CURRENT = copy.deepcopy(_FACTORY_MAX_CH1_CURRENT)
_USER_MIN_CH2_CURRENT = copy.deepcopy(_FACTORY_MIN_CH2_CURRENT)
_USER_MAX_CH2_CURRENT = copy.deepcopy(_FACTORY_MAX_CH2_CURRENT)
_USER_MIN_CH3_CURRENT = copy.deepcopy(_FACTORY_MIN_CH2_CURRENT)
_USER_MAX_CH3_CURRENT = copy.deepcopy(_FACTORY_MAX_CH2_CURRENT)

# Default timeout value.
_DEFAULT_TIMEOUT = 15

# The number of resolved digits kept by internal rounding
# by the power supply.
_SUPPLY_RESOLVED_DIGITS = 4


class PSU_Keysight_E36311A(BaseDriver):

    
    """ This is a class that acts as a control for the 
    Keysight_E3631A power supply.
    
        Attributes
        ----------
        --> # = channel 1, 2, or 3
            CH#_voltage : property(float)
                The attribute that controls the CH# output voltage on the 
                power supply.
            CH#_current : property(float)
                The attribute that controls the CH# output current on the 
                power supply.

            MIN_CH#_VOLTAGE : float
                The minimum instance limitation for CH# voltages.
            MAX_CH#_VOLTAGE : float
                The maximum instance limitation for CH# voltages.

            MIN_CH#_CURRENT : float
                The minimum instance limitation for CH# currents.
            MAX_CH#_CURRENT : float
                The maximum instance limitation for CH# currents.
                
    """

    # Internal implementation values.
    _CH1_voltage = float()
    _CH1_current = float()
    
    _CH2_voltage = float()
    _CH2_current = float()
    
    _CH3_voltage = float()
    _CH3_current = float()
    
    # TODO: combine with verify_current_value, by just using if/else statements 
    #           and working with 'min_factory/max_factory' and 'min_user/max_user'
    

    #############################################################
    ###############  Abstract BaseDriver Methods  ###############
    #############################################################
    
    
    def __init__(self, InstrConfig_Dict, instr_resource=None, instr_address=None, debug=False, **kwargs):
        super().__init__(InstrConfig_Dict, instr_resource, instr_address, debug, **kwargs)
    
    def read_check(self, fmt=...):
        return super().read_check(fmt)
    
    def write_check(self, cmd: str):
        return super().write_check(cmd=cmd)
    
    def query_check(self, cmd, fmt=...):
        return super().query_check(cmd, fmt)
    
    def check_instr_error_queue(self, print_output=False):
        return super().check_instr_error_queue(print_output)
    
    def return_instrument_parameters(self, print_output=False):
        return super().return_instrument_parameters(print_output)


    #############################################################
    #####################  Instr Parameters  ####################
    #############################################################
    #############    Just getters and setters!!  ################
    #############################################################
    
    
    def get_output(self, channel):
        
        return reported_status
    
    
    def set_output(self, channel, output):
        
        return None
    
    
    
    
    #############################################################
    #########################  Voltage  #########################
    #############################################################
    
    def get_channel_voltage(self, channel):
        """ 
            This gets the voltage of the powersupply, it also 
            checks the variable value and the one obtained directly.
            
            Input 'channel' can be an integer for channels 1, 2, and 3, or it
            can just be the strings 'ch1', 'ch2', 'ch3'.
        """
        # take input and make into a string 'ch#''
        ch_str = self.convert_channel_var_to_str(channel)
        
        # generate the appropriate command for given channel
        request_command = self._generate_apply_command(
            output=ch_str, voltage=None, current=None, request=True)
        
        # send command and read result
        result = self.send_scpi_command(command=request_command)
        
        volt, __ = result.split(',')
        volt = volt.strip('"')
        reported_voltage = float(volt)
        
        if ch_str == "ch1":
            saved_voltage = self.CH1_VOLTAGE
        elif ch_str == "ch2":
            saved_voltage = self.CH2_VOLTAGE
        elif ch_str == "ch3":
            saved_voltage = self.CH3_VOLTAGE
        
        # Double check that the two voltages are the same.
        assert_bool = math.isclose(reported_voltage, saved_voltage)
        assert_message = ("The supply {ch_str} voltage and the class voltage "
                          "are not the same. Assign a voltage via "
                          "the class before reading the voltage. "
                          "Keep the power supply in remote mode to "
                          "prevent this behavior. \n "
                          "Class: {cls_volt}  Power Supply: {ps_volt}"
                          .format(ch_str=ch_str,
                                  cls_volt=saved_voltage,
                                  ps_volt=reported_voltage))
        assert assert_bool, assert_message
        
        return reported_voltage


    def set_channel_voltage(self, channel, voltage):
        """ 
            Sets the voltage of the power supply at the given channel. 
                Checks the voltage value stored in the object to 
                ensure that the power supply range is not abnormal. 
        """
        
        ch_str = self.convert_channel_value_to_str(channel)
        
        # will raise a ValueError if voltage falls outside the 
        # factory or user defined min/maxes
        assert self.verify_voltage_value(ch_str, voltage)  
        
        voltage = round(voltage, _SUPPLY_RESOLVED_DIGITS)
        
        if ch_str == "ch1":
            self.CH1_VOLTAGE = voltage
            current = self.CH1_CURRENT
        elif channel == "ch2":
            self.CH2_VOLTAGE = voltage
            current = self.CH2_CURRENT
        elif channel == "ch3":
            self.CH3_VOLTAGE = voltage
            current = self.CH3_CURRENT
        
        # Send the command to the power supply.
        command = self._generate_apply_command(
            output=ch_str, voltage=voltage, 
            current=current, request=False)
        
        __ = self.send_scpi_command(command=command)
        
        return None
    
    
    def verify_voltage_value(self, channel, voltage):
        
        """ 
            will raise a ValueError with an appropriate message if the
                given voltage value is outside the bounds of the _FACTORY min/maxes 
                or the _USER min/maxes
        """
        
        ch_str = self.convert_channel_value_to_str(channel)
        
        if channel == "ch1":
            min_factory_voltage, max_factory_voltage = _FACTORY_MIN_CH1_VOLTAGE, _FACTORY_MAX_CH1_VOLTAGE
            min_user_voltage, max_user_voltage = _USER_MIN_CH1_VOLTAGE, _USER_MAX_CH1_VOLTAGE
        elif channel == "ch2":
            min_factory_voltage, max_factory_voltage = _FACTORY_MIN_CH2_VOLTAGE, _FACTORY_MAX_CH2_VOLTAGE
            min_user_voltage, max_user_voltage = _USER_MIN_CH2_VOLTAGE, _USER_MAX_CH2_VOLTAGE
        elif channel == "ch3":
            min_factory_voltage, max_factory_voltage = _FACTORY_MIN_CH3_VOLTAGE, _FACTORY_MAX_CH3_VOLTAGE
            min_user_voltage, max_user_voltage = _USER_MIN_CH3_VOLTAGE, _USER_MAX_CH3_VOLTAGE
            
        # Ensure that the voltage value is not outside the 
        # power supply's manufacture's limit.
        if (min_factory_voltage <= voltage <= max_factory_voltage):
            # The voltage is within the manufacture's limit.
            pass
        else:
            raise ValueError("The attempted voltage value is {volt}. This "
                             "is outside the factory specifications for the "
                             "{ch_str} output: {min} <= V <= {max}."
                             .format(ch_str=ch_str, volt=voltage, 
                                     min=min_user_voltage, max=max_user_voltage))
            
        # Ensure that the voltage value is not outside the user 
        # defined limits, which are at the top of this class.
        if (min_user_voltage <= voltage <= max_user_voltage):
            # The voltage is within the user's limit.
            pass
        else:
            raise ValueError("The attempted voltage value is {volt}. This "
                             "is outside the user limitations for the "
                             "{ch_str}} output: {min} <= V <= {max}."
                             .format(ch_str=ch_str, volt=voltage, 
                                     min=min_user_voltage, max=max_user_voltage))
        
        # if we make it here, we have successfully 
        # validated the voltage value
        return True
    
    #############################################################
    #########################  Current  #########################
    #############################################################

    def get_channel_current(self, channel):
        """ 
            This gets the current of the powersupply, it also 
            checks the variable value and the one obtained directly.
            
            Input 'channel' can be an integer for channels 1, 2, and 3, or it
            can just be the strings 'ch1', 'ch2', 'ch3'.
        """
        # take input and make into a string 'ch#''
        ch_str = self.convert_channel_var_to_str(channel)
        
        # generate a query with appropriate channel
        request_command = self._generate_apply_command(
            output=ch_str, voltage=None, current=None, request=True)
        
        # send command and read result
        result = self.send_scpi_command(command=request_command)
        
        _, current = result.split(',')
        current = current.strip('"')
        reported_current = float(current)
        
        # change to dict?
        if ch_str == "ch1":
            saved_current = self.CH1_CURRENT
        elif ch_str == "ch2":
            saved_current = self.CH2_CURRENT
        elif ch_str == "ch3":
            saved_current = self.CH3_CURRENT
        
        
        # Double check that the two current are the same.
        assert_bool = math.isclose(reported_current, saved_current)
        assert_message = ("The supply {ch_str} current and the class current "
                          "are not the same. Assign a current via "
                          "the class before reading the current. "
                          "Keep the power supply in remote mode to "
                          "prevent this behavior. \n "
                          "Class: {cls_current}  Power Supply: {ps_current}"
                          .format(ch_str=ch_str,
                                  cls_current=saved_current,
                                  ps_current=reported_current))
        
        assert assert_bool, assert_message
        
        return reported_current


    def set_channel_current(self, channel, current):
        """ 
            Sets the current of the power supply. Checks exist to 
             ensure that the power supply range is not abnormal. 
        """
        
        ch_str = self.convert_channel_value_to_str(channel)
        
        # will raise a ValueError if current falls outside the 
        # factory or user defined min/maxes
        self.verify_current_value(ch_str, current)
        
        curr = round(curr, _SUPPLY_RESOLVED_DIGITS)
        
        # save current into object, get voltage value for cmd
        if ch_str == "ch1":
            self.CH1_CURRENT = current
            voltage = self.CH1_VOLTAGE
        elif channel == "ch2":
            self.CH2_CURRENT = current
            voltage = self.CH2_VOLTAGE
        elif channel == "ch3":
            self.CH3_CURRENT = current
            voltage = self.CH3_VOLTAGE
            
        # Send the command to the power supply.
        command = self._generate_apply_command(
            output=ch_str, voltage=voltage, 
            current=current, request=False)
        
        __ = self.send_scpi_command(command=command)
        
        return None


    def verify_current_value(self, channel, current):
        
        """ 
            will raise a ValueError with an appropriate message if the
                given current value is outside the bounds of the 
                _FACTORY min/maxes or the _USER min/maxes
        """
        
        ch_str = self.convert_channel_value_to_str(channel)
        
        if ch_str == "ch1":
            min_factory_current, max_factory_current = _FACTORY_MIN_CH1_CURRENT, _FACTORY_MAX_CH1_CURRENT
            min_user_current, max_user_current = _USER_MIN_CH1_CURRENT, _USER_MAX_CH1_CURRENT
        elif ch_str == "ch2":
            min_factory_current, max_factory_current = _FACTORY_MIN_CH2_CURRENT, _FACTORY_MAX_CH2_CURRENT
            min_user_current, max_user_current = _USER_MIN_CH2_CURRENT, _USER_MAX_CH2_CURRENT
        elif ch_str == "ch3":
            min_factory_current, max_factory_current = _FACTORY_MIN_CH3_CURRENT, _FACTORY_MAX_CH3_CURRENT
            min_user_current, max_user_current = _USER_MIN_CH3_CURRENT, _USER_MAX_CH3_CURRENT
            
        # Ensure that the current value is not outside the 
        # power supply's manufacture's limit.
        if (min_factory_current <= current <= max_factory_current):
            # The current is within the manufacture's limit.
            pass
        else:
            raise ValueError("The attempted current value is {curr}. This "
                             "is outside the factory specifications for the "
                             "{ch} output: {min} <= V <= {max}."
                             .format(ch=ch_str, curr=current, min=min_user_current, 
                                                   max=max_user_current))
            
        # Ensure that the current value is not outside the user 
        # defined limits, which are at the top of this class.
        if (min_user_current <= current <= max_user_current):
            # The current is within the user's limit.
            pass
        else:
            raise ValueError("The attempted current value is {curr}. This "
                             "is outside the user limitations for the "
                             "CH1 output: {min} <= V <= {max}."
                             .format(curr=current, min=min_user_current, 
                                                   max=max_user_current))
        
        # if we make it here, we have successfully 
        # validated the current value
        return True
        
    # #############################################################
    # ####################   Instr Helpers   ######################
    # #############################################################
    
    def convert_channel_value_to_str(self, channel):
        # if "channel" is int or float, format into string
        # if "channel" is string, check if it matches 'ch#'
        
        if type(channel) == int or type(channel) is float:
            if channel.is_integer() and channel in [1, 2, 3]:
                ch_str = f"ch{int(channel)}"
            else:
                raise ValueError("Input to 'convert_channel_value_to_str' must be either an integer, int() or float(), or 'ch1', 'ch2', 'ch3'!")
        elif type(channel) == str:
            if channel in ['ch1', 'ch2', 'ch3']:
                ch_str = channel  # already good!
            elif channel in ['1', '2', '3']:
                ch_str = self.convert_channel_value_to_str(int(channel))  # recursive!
            else:
                raise ValueError("Input to 'convert_channel_value_to_str' must be either an integer, int() or float(), or 'ch1', 'ch2', 'ch3'!")
                            
        return ch_str
    
    
    def _generate_apply_command(self, channel, voltage, current,
                                request=False):
        """ This is just a wrapper function to spit out a string
        that is a APPLy valid command for the function used.
        """
        
        ch_str = self.convert_channel_value_to_str(channel)
        
        # Parameters 'voltage' and 'current' should be strings. 
        # If the parameter 'DEF', 'MIN', or 'MAX' is used, use that instead.
        
        #### Voltage ####
        if ((str(voltage).upper() in ('','DEF','MIN','MAX')) or 
            (voltage is None)):
            voltage = '' if (voltage is None) else voltage  # leave blank if not changing
            voltage_str = str(voltage).upper()
        else:
            voltage_str = '{:6f}'.format(float(voltage))
            
        #### Current ####
        if ((str(current).upper() in ('','DEF','MIN','MAX')) or 
            (current is None)):
            current = '' if (current is None) else current  # leave blank if not changing
            current_str = str(current).upper()
        else:
            current_str = '{:6f}'.format(float(current))

        # perform query if request is True, else just write
        if request is True:    
            apply_command = ('APPLy? {out}'.format(out=ch_str))
        else:  
            apply_command = ('APPLy {out},{volt},{curr}'
                             .format(out=ch_str, 
                                     volt=voltage_str, 
                                     curr=current_str))
        return apply_command
    
    
    def beep(self):
        """ Sends a beep command to the power supply.

        Parameters
        ----------
        None

        Returns
        -------
        response : string
            The response from the power supply.
        """
        # The beep scpi command.
        beep_command = 'SYSTem:BEEPer:IMMediate'
        # Sending the beep command.
        response = self.send_scpi_command(command=beep_command)
        # All done.
        return response
    
    
    
if __name__ == "__main__":
    print("Test")
    
    PSU_Keysight_InstrConfig = {
        "instrument_name" : "PSU_Test",
        "rm_backend" : None,
        "instr_address" : "192.168.0.105",
        
    }
    
    PSU_Keysight = PSU_Keysight_E36311A()
    
    pass
    
    
    
    
    