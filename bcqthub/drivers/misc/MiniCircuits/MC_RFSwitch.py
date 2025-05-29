"""
    MiniCircuits RF Switch
    
    Coded specifically for the RC-4SPDT-A18 model

    Loosely based on their example python code on their website
    
    https://www.minicircuits.com/WebStore/pte_example_download.html?fam=Mechanical%20Switch%20Box
    
    # TODO: could combine with other minicircuits drivers with an abstract class...
    #       probably not worth the effort?

"""

from urllib.request import urlopen
import sys, time

class MC_RFSwitch():
    
    def __init__(self, device_address="192.168.0.115", timeout=5, debug=True):
        
        self.debug = debug
        self.device_name = "RF Switch"
        self.device_address = device_address
        self.timeout = timeout
        
    
        if self.debug is True:
            print(self.Get_Model_Name())
            print(self.Get_Serial_No())
            print()
    
    
    def Format_PTE_Return(self, PTE_Return):
        # example output:
        #   b'MN=RCDAT-8000-30'
        # split and return the parts on either side
        #   of the '=', and remove b and '
        
        PTE_Return = str(PTE_Return).replace("b'", "").replace("'","").strip()
        
        if "=" in PTE_Return:
            var, result = PTE_Return.split("=")
        else:
            var, result = self.device_name, PTE_Return
            
        
        return var, result
    
    
    def Get_HTTP_Result(self, Cmd):

        # Specify the IP address of the switch box
        CmdToSend = f"http://{self.device_address}/:{Cmd}"
        
        # Send the HTTP command and try to read the result
        try:
            HTTP_Result = urlopen(CmdToSend, timeout=self.timeout)
            PTE_Return = HTTP_Result.read()

            # The switch displays a web GUI for unrecognised commands
            if len(PTE_Return) > 100:
                print("Error, command not found:", CmdToSend)
                PTE_Return = "Invalid Command!"

        # Catch an exception if URL is incorrect (incorrect IP or disconnected)
        except Exception as e:
            print(f"Error: {e} \nError, no response from device; check IP address and connections.")
            PTE_Return = "No Response!"
            raise ConnectionError

        var, result = self.Format_PTE_Return(PTE_Return)
        
        # Return the response
        return var, result


    def Get_Model_Name(self):
        return self.Get_HTTP_Result("MN?")


    def Get_Serial_No(self):
        return self.Get_HTTP_Result("SN?")


    def Set_Switch_State(self, switch: str, contact: int):
        # switch = A, B, C, D
        # contact = 0 for blue (left), 1 for red (right)
        
        
        contact -= 1  # shift 1/2 to 0/1 to have input (GUI) match the code
        
        try:
            contact = int(contact)
        except:
            pass
        
        if len(switch) != 1:
            raise ValueError("Switch variable must ba a string of length 1 -> e.g. 'A', 'B', 'C', or 'D'")
        
        if type(contact) != int:
            raise ValueError("Contact argument must be an integer - either '0' for blue, or '1' for red switch state!")
        
        cmd = f"SET{switch}={contact}"
        
        if self.debug is True:
            print(f"Sending {cmd = }")
        
        status = self.Get_HTTP_Result(cmd)   # Send switch command
        
        if self.debug is True:  # Print switch position
            print(f" - new switch status {self.Get_HTTP_Result("SWPORT?")}")       
        
        time.sleep(0.5)
        
        return status


if __name__ == "__main__":
    
    ip_addr = "192.168.0.115"  
    
    atten = MC_RFSwitch(ip_addr, debug=True)
    
    pass