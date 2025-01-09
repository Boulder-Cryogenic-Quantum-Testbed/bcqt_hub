import numpy as np
import pandas as pd
from datetime import datetime
# %%

class DataSet():
    """
        this class compartmentalizes just one set of data
        
        the data will be saved in pandas dataframes in self.data
        
        the scope of the methods include:
            - initialization requires a dataset, an experiment name, and units
            - methods for handling different input data types (dict, list, np.array, dataframe)
            - stores metadata such as units and experimental configs
            - generates relevant metadata such as timestamps, filepaths
       
    """
    
    def __init__(self, data, expt_name:str, meas_label:str, units:str, **kwargs):
        
        self.data = pd.DataFrame()
        
        """ check type of arg 'data', then use appropriate method """
        if isinstance(data, pd.DataFrame):
            self.append_df(data)
        elif isinstance(data, np.ndarray) or isinstance(data, list):
            self.append_array(data, meas_label)
        else:
            self.append_dict(data)
        
        
        self.expt_name = expt_name
        self.meas_label = meas_label
        
        self.metadata = {
            "expt_name" : expt_name,
            "label" : meas_label,
            "units" : units,
            "creation_time" : datetime.now(),
        }
        
        if "configs" in kwargs:
            self.add_configs(kwargs["configs"])
        
    
    #### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
    
    def append_df(self, data_df, axis=1):
        """ if a DataFrame is given, concat with existing """
        self.data = pd.concat([self.data, data_df], axis=axis)
        self.data.reset_index(drop=True, inplace=True)
        
    def append_row_df(self, data_row):
        self.append_df(data_row, axis=0)
        
    def append_dict(self, data_dict):
        """ if a dict is given, append to dataframe as a column or row """
        data_df = pd.DataFrame.from_dict(data_dict)
        self.append_df(data_df)
            
    def append_array(self, data, label):
        """ if an array is given, require a label and append to dataframe  """
        self.append_dict( {label : data} )
            
            
    #### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
    
    
    def generate_metadata(self):
        pass
    
    def display_metadata(self, print_output=False):
        data, metadata = self.data, self.metadata
        str_repr = f"label: {metadata["label"]}\n" + " "*11 + \
                   f"len(data) = {len(data)}\n" + " "*11 + \
                   f"units = {metadata["units"]}\n" + " "*11
        
        if print_output is True:
            print(str_repr)
        else:
            return str_repr
    
    def append_to_metadata(self, **kwargs):
    
        for key, val in kwargs.items():
            if key in self.metadata:
                self.print_datahandler(f"        [DataSet] Overwriting {key}={self.metadata[key]} with {key}={val}")
            else:
                print(f"Saving {key}={val}")
    
            self.metadata[key] = val
            
            
    #### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
        
        
    def add_configs(self, configs:dict):
        self.configs = configs
    
    def update_configs(self, new_configs):
        self.configs.update(new_configs)
        
            
    #### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
            
    def __str__(self):
        return f"DataSet -> {self.display_metadata()}"
    
    def __len__(self):
        return len(self.data)
    
    def __repr__(self):
        return f"DataSet: {len(self) = }"
    
    
class DataHandler(dict):
    
    """
        modified dict that has built-in support for:
            - creating DataSet objects to compartmentalize data
            - combining DataSets into one pandas dataframe
            - saving multiple datasets as csv files
    """
    
    def __init__(self, *args, **kwargs):
      self.__dict__ = self
      super().__init__(*args, **kwargs)
      


    def load_dataset(self, dset):
        
        if isinstance(dset, DataSet) is False:
            raise TypeError("argument 'dset' is not a DataSet object.")
        
        self[expt_name] = DataSet(data, expt_name, units)
        
        expt_name = dset

    # def 
# %%
