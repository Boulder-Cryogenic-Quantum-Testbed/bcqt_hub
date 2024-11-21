import numpy as np
from datetime import datetime

class DataSet():
    """
        this class compartmentalizes just one set of data. it doesn't exactly extend
        
        the scope of the methods include:
            - initialization requires a dataset, an experiment name, and units
            - storing metadata such as units, date, 
        
        The data is expected to be either a 1xN trace, or an NxM array of N traces with M data points each.
    """
    def __init__(self, data:np.array, expt_name:str, units:str):
        
        self.metadata = {
            "expt_name" : expt_name,
            "units" : units,
            "creation_time" : datetime.now(),
        }
        
        self.data = data
        
    def append_to_metadata(self, **kwargs):
    
        for k, v in kwargs.items():
            if k in self.metadata:
                self.print_datahandler(f"        [DataSet] Overwriting {k}={self.metadata[k]} with {k}={v}")
            else:
                print(f"Saving {k}={v}")
    
        self.metadata = {
            **self.metadata,
            **kwargs,
        }
        
        
class DataHandler(dict):
    
    """
        modified dict that has built-in support for:
            - creating DataSet objects to compartmentalize data
            - saving and loading CSV's
    """
    
    def __init__(self, *args, **kwargs):
      self.__dict__ = self
      super().__init__(*args, **kwargs)


    def save_data(self, data, expt_name, units):
        self[expt_name] = DataSet(data, expt_name, units)
        
        
        
        
        
    def load_data(self, data):
        print("Loading data into storage...")
        self.data_storage.append(data)

        
            
    def get_data(self):
        return self.data_storage


    # def 