import numpy as np
import pandas as pd
from datetime import datetime

class DataSet():
    """
        this class compartmentalizes just one set of data. it doesn't exactly extend a dict or numpy array
        
        the scope of the methods include:
            - initialization requires a dataset, an experiment name, and units
            - storing metadata such as units, date, 
        
        The data is expected to be either a 1xN trace, or an NxM array of N traces with M data points each.
    """
    def __init__(self, data, expt_name:str, dataset_label:str, units:str, **kwargs):
        
        # TODO: treat df and np.arrays separately
        self.data = data
        
        if isinstance(data, pd.DataFrame):
            data_type = "Pandas Dataframe" 
        elif isinstance(data, np.ndarray):
            data_type = "Numpy ndarray" 
        else:
            data_type = type(data)
            
        self.metadata = {
            "expt_name" : expt_name,
            "dataset_label" : dataset_label,
            "units" : units,
            "creation_time" : datetime.now(),
            "data_type" : data_type,
        }
        
        if "configs" in kwargs:
            self.add_configs(kwargs["configs"])
            
    
    def __str__(self):
        return f"DataSet -> {self.parse_metadata()}"
    
    def parse_metadata(self, print_output=False):
        data, metadata = self.data, self.metadata
        str_repr = f"{metadata["dataset_label"]}\n" + " "*11 + \
                   f"{len(data)=}\n" + " "*11 + \
                   f"units={metadata["units"]}\n" + " "*11 + \
                   f"data_type = {metadata["data_type"]}\n"
        
        if print_output is True:
            print(str_repr)
        
        return str_repr
    
    def append_to_metadata(self, **kwargs):
    
        for key, val in kwargs.items():
            if key in self.metadata:
                self.print_datahandler(f"        [DataSet] Overwriting {key}={self.metadata[key]} with {key}={val}")
            else:
                print(f"Saving {key}={val}")
    
            self.metadata[key] = val
        
        
    def add_configs(self, configs:dict):
        self.configs = configs
    
    def update_configs(self, new_configs):
        self.configs.update(new_configs)
        
        
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