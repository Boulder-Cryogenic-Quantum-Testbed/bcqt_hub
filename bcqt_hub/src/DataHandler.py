# %%
import numpy as np
import pandas as pd
import copy
import json
from collections import UserDict
from pathlib import Path
from datetime import datetime


class DataSet():
    """
        this class compartmentalizes just one set of data
        
        One Dataset should correspond to one measurement

        Basically the DataSet is the book and the DataHandler is the bookshelf
    """
    
    # def __init__(self, data, expt_name:str, meas_label:str, units:str, **kwargs):
        
    #     self.data = pd.DataFrame()
        
    #     """ check type of arg 'data', then use appropriate method """
    #     if isinstance(data, pd.DataFrame):
    #         self.append_df(data)
    #     elif isinstance(data, np.ndarray) or isinstance(data, list):
    #         self.append_array(data, meas_label)
    #     else:
    #         self.append_dict(data)
        
        
    #     self.expt_name = expt_name
    #     self.meas_label = meas_label
        
    #     self.metadata = {
    #         "expt_name" : expt_name,
    #         "label" : meas_label,
    #         "units" : units,
    #         "creation_time" : datetime.now(),
    #     }
        
    #     if "configs" in kwargs:
    #         self.add_configs(kwargs["configs"])
    
    def __init__(self, csv_path, metadata_dict):
        """

        """
        self.data = self.load_csv(csv_path)
        self.file_name = csv_path
        self.metadata = metadata_dict
        
    
    #### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
    
    # def append_df(self, data_df, axis=1):
    #     """ if a DataFrame is given, concat with existing """
    #     self.data = pd.concat([self.data, data_df], axis=axis)
    #     self.data.reset_index(drop=True, inplace=True)
        
    # def append_row_df(self, data_row):
    #     self.append_df(data_row, axis=0)
        
    # def append_dict(self, data_dict):
    #     """ if a dict is given, append to dataframe as a column or row """
    #     data_df = pd.DataFrame.from_dict(data_dict)
    #     self.append_df(data_df)
            
    # def append_array(self, data, label):
    #     """ if an array is given, require a label and append to dataframe  """
    #     self.append_dict( {label : data} )

    def load_csv(self, csv_path_string):
        return pd.read_csv(csv_path_string, index_col=0)
            
    def get_data(self):
        return self.data

    def get_file_name(self):
        return str(self.file_name.stem)
    
    def get_meta_data(self):
        return self.metadata
    
    #### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###

    # Make metadata editor if needed

    # def display_metadata(self, print_output=False):
    #     data, metadata = self.data, self.metadata
    #     str_repr = f"label: {metadata["label"]}\n" + " "*11 + \
    #                f"len(data) = {len(data)}\n" + " "*11 + \
    #                f"units = {metadata["units"]}\n" + " "*11
        
    #     if print_output is True:
    #         print(str_repr)
    #     else:
    #         return str_repr
    
    # def append_to_metadata(self, **kwargs):
    
    #     for key, val in kwargs.items():
    #         if key in self.metadata:
    #             self.print_datahandler(f"        [DataSet] Overwriting {key}={self.metadata[key]} with {key}={val}")
    #         else:
    #             print(f"Saving {key}={val}")
    
    #         self.metadata[key] = val
            
    #### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
            
    def __str__(self):
        return f"DataSet -> {self.display_metadata()}"
    
    def __len__(self):
        return len(self.data)
    
    def __repr__(self):
        return f"DataSet obj of length {len(self)}"
    
    
class DataHandler(UserDict):
    
    """
        modified dict that has built-in support for:
            - creating individual DataSet objects that compartmentalize data
            - organize multiple DataSets while bookkeeping metadata 
            - handle the loading and saving of csv files & json metadata
            
            
        philosophy:
            - I never want to interface with a DataSet object myself, since its scope is strictly 
                holding data.

            - The DataHandler object should load all data in a directory, or load a specific 
                file, with associated JSON metadata.

            - Then, if I want to look at a previous measurement result, I just 
                init a DataHandler object and provide a filepath/dirpath. The 
                the DataHandler does all the work for me 🙂
                
    """
    
    
    def __init__(self):
        super().__init__()
        # if isinstance(path, Path) is False :
        #     raise TypeError("argument 'file_path' is not a Path object.")
        # self.path = path
        self.list_of_datasets = {}
        self.key = 0


        """
            we need to figure out what the keyword for each dataset should be
            
            dH = DataHandler(path)  # decide later whether path goes in init or load_dsets
            dH.load_dsets()
            
            ***
            
            for key, dset in dH.items():
                
                print(key, dset)
                
                

            previous code
                key is integer, to mimic enumerate()
                but also keeps keys static when removing
                an element
            
            
        """
        # FIX FOR LATER
    def load_sets():
        
        # check if path is a directory or a single csv
        
        # if path.is_dir() is True:
        #     self.load_data_directory(self.path, {})
        #     self.display_datasets()
        #     # self.create_metadata_for_directory(self.path, {})
        #     self.load_metadata_and_display(self.path)
        # elif path.is_file() is True:
        #     self.load_dataset(self.path, {})
        #     self.display_datasets()
        # if directory: create multiple dsets that load all csvs, then load json if it exists
        
        # if file: create on dset that loads a single csv
        pass

    # Load a directory of path objects and create a corresponding dataset object for all of them
    def load_data_directory(self, path:Path, mdict:dict):
        if path.is_dir() is False:
            raise TypeError("argument 'path' is not a directory object.")

        data_dir_files = list(path.glob("*"))
        self.create_metadata_for_directory(path, mdict)
        for file in data_dir_files:
            self.load_dataset(file, mdict)
            
    
    # Load a singular dataset from a given path object
    def load_dataset(self, file_path: Path, metadict:dict):
        if isinstance(file_path, Path) is False :
            raise TypeError("argument 'file_path' is not a Path object.")
        
        dset = self.create_dataset(file_path, metadict)
        # file_name = str(file_path.stem)
        self.list_of_datasets[self.key] = dset
        # Look INTO Ordered dict
        self.key += 1
        

    # Create a dataset object from a path object 
    def create_dataset(self, csv_path, metadict):
        dset = DataSet(csv_path, metadict)
        return dset
    
    def display_datasets(self, number_of_rows=2):
        for key, value in self.list_of_datasets.items():
            # print(key)
            display(f"Index: {key}")
            # Uncomment the print if not using the juypter notebook and comment out the display
                # print(value.head(number_of_rows))
            display(value.get_file_name())
            display(value.data.head(number_of_rows))
            # display(value.get_meta_data())

    def create_metadata_for_directory(self, dir_path:Path, mdict:dict):
        current_json = list(dir_path.glob("*.json"))
        if len(current_json) == 0:
            with open("metadata.json", "w", encoding="utf8") as json_file:
                json.dump(mdict, json_file, indent=4)
        else:
            display("Json file already exists")

        # NEED TO TEST 
    def load_metadata_and_display(self, dir_path:Path):
        current_json = list(dir_path.glob("*.json"))
        if len(current_json) == 1:
            with open('metadata.json', 'w', encoding='utf8') as json_file:
                metadata = json.load(json_file)
            display(metadata)
        elif (len(current_json) == 0) and dir_path.is_dir():
            display("There is no metadata, please call 'create_metadata_for_directory' to create one")
        else:
            display("There is more than one metadata file, please check")
     
    # Come back to do to insert a json file (in skele form)
    # do we (2) want to try to store the actual metadata

    # For point 2 could see creating different amoutns of columns for each dataset
    #   which could be tedious but overall more helpful as it is more accessible

    # How do we want to handle export the datahandler and/or all the datasets?

    # HW: Test the datahandler/dataset on the massive amount of CSV files directory and 
    #   make sure the datahandler creates all the respective dataframes 
    #   and creates the corresponding json file for the relevant metadata / directory 
    #       (make metadata simple like name)
    #   Make sure in juypter notebook

# %%

# TODO (2/18/2025)
    # Fix using the object as a dict
    # Save data
        # Let datahandler accept pandasframe, array, list
        # Export/Saves the data into a csv
        # 

# Test Code for metadata
if __name__ == "__main__":
    # Initializing
    # dHandler = DataHandler()
    # cur_dir = Path("./")
    # test_csv = list(cur_dir.glob("*.csv"))[0]
    # # print(test_csv)
    # dHandler = DataHandler(test_csv)

    data_dir = Path("../../experiments/TWPA Calibration/data/cooldown59/Line6_SEG_PdAu_02/Line6_SEG_PdAu_02_01_21_0108PM_TWPA_Calibration")
    # data_dir_list = list(data_dir.glob("*"))
    # display(data_dir_list)

    dh = DataHandler()
    
    csv_list = [x for x in list(data_dir.glob("*"))if "DS" not in x.name]
    for direct in csv_list:
        dh.load_data_directory(direct, None)
        
    # dh.display_datasets()


    display(dh.list_of_datasets[0].data)
    
    

    # for indx, dset_result in dh.items():
    #     display(indx)
    #     display(dset_result)
    #     pass
    # dh.display_datasets()
    

        
    # innerdict = {"fish":"yellow"}
    # mdict = {"file_name": str(test_csv.stem), "cat":"joe", 5:"big", "innerdict": innerdict}
    # # dHandler.store_metadata_into_dataset(test_csv, mdict)
    # dHandler.load_dataset(test_csv, mdict)
    # dHandler.display_datasets()
    # dHandler.create_metadata_for_directory(test_csv, mdict=mdict)


    # %%
    
    """
        2/18/25 - currently, our DataHandler can load an entire directory of csv files, or load csv files one by one.
        
        However, we also want DataHandler to save the data we've taken, not just load data from a past experiment
        
        Here are some possible implementations of how we'd actually *use* DataHandler during the measurement process
    
    """
    
    #           . 
    #           .
    #  some measurement code
    #           .
    #           .
    
    
    data_to_save = {1 : [1,2,3,"a","b","c"],
                    2 : [1,2,3,"a","b","c"],
                    3 : [1,2,3,"a","b","c"],}
    
    dh_save =  DataHandler()
    

    #### method 1 - one array at a time
    # likely will be used by #2
    
    for idx, result in data_to_save.items():
        dh_save.save_array(result)
        
    #### method 2 - many arrays at once
    # not a big fan since this means data will be saved all at once
    # in the end, but can be useful when taking small amounts of data
    
    dh_save.save_array_dict(data_to_save)
    
    
    #### method 3 - pass datahandler object to measurement method, this is the final goal for the object
    """
    
    experiment.take_data(dh_save)
    
    #           . 
    #           .
    #    measurement code
    #           .
    #           .
    
    dh_save.display_datasets()
    
    """
    
    # print(dHandler)

# %%
