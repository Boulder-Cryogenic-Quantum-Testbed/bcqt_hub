# %%
import numpy as np
import pandas as pd
import json
from varname import argname
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
    
    def __init__(self, csv_path=None, data_frame=None):
        """

        """
        if csv_path == None and isinstance(data_frame, pd.DataFrame):
            self.data = data_frame
        elif isinstance(csv_path, Path)  and data_frame == None:
            self.data = self.load_csv(csv_path)
            self.file_name = csv_path
        
    
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
        if csv_path_string.suffix != ".csv":
            return pd.DataFrame()   # TODO: how will we handle errors? empty dataframe? None?
        else:
            return pd.read_csv(csv_path_string, index_col=0)
            
    def get_data(self):
        return self.data

    def get_file_name(self):
        return str(self.file_name.stem)
    
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
        self.key = 0
        self.metadata = {}

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
    def load_sets(self, path:Path, mdict:dict, overwrite_flag=False):
        
        # check if path is a directory or a single csv
        self.create_metadata_file_for_directory(path, mdict, overwrite_flag)
        self.load_data_directory_rec(path)
    
        pass

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
# Loading directory/dataset into datahandler

    # Load a a directory containing csv objects into the datahandler recursively
    def load_data_directory_rec(self, path:Path):
        list_of_file_or_directory = list(path.glob("*"))
        for file_or_dirctory in list_of_file_or_directory:
            if ".json" in str(file_or_dirctory):
                # display(f"{file_or_dirctory}")
                continue
            if file_or_dirctory.is_dir() is True:
                self.load_data_directory_rec(file_or_dirctory)
            elif file_or_dirctory.is_file() is True:
                self.load_dataset(file_or_dirctory)
            else:
                print(f"Directory/File that is incorrect {str(file_or_dirctory)}")


    # Load a directory of path objects and create a corresponding dataset object for all of them
    # def load_data_directory(self, path:Path, mdict:dict):
    #     if path.is_dir() is False:
    #         raise TypeError("argument 'path' is not a directory object.")
    #     data_dir_files = list(path.glob("*"))
    #     self.create_metadata_for_directory(path, mdict)
    #     for file in data_dir_files:
    #         self.load_dataset(file, mdict)
    
    # Load a singular dataset from a given path object
    def load_dataset(self, file_path: Path):
        if isinstance(file_path, Path) is False :
            raise TypeError("argument 'file_path' is not a Path object.")
        
        dset = self.create_dataset(file_path)
        self[self.key] = dset
        self.key += 1
        
    def create_dataset(self, csv_path):
        dset = DataSet(csv_path)
        return dset
    
    
    def display_datasets(self, number_of_rows=3, num_dsets_to_display=5):
        for idx, (key, value) in enumerate(self.items()):
            if (idx % (len(self.items())//num_dsets_to_display)) != 0:
                continue
            display(f"Index: {key}")
            # Uncomment the print if not using the juypter notebook and comment out the display
                # print(value.head(number_of_rows))
            if isinstance(value, DataSet) is True:
                display(value.get_file_name())
                display(value.data.head(number_of_rows))
            else:
                display(value)
            
            # display(value.get_meta_data())

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
# Metadata Stuff

    def create_metadata_file(self, dir_path:Path, mdict:dict = None):
        with open(dir_path  / "metadata.json", "w", encoding="utf8") as json_file:
                if mdict == None:
                    mdict = self.metadata
                json.dump(mdict, json_file, indent=4)

    def create_metadata_file_for_directory(self, dir_path:Path, mdict:dict, overwrite_flag=False):
        current_json = list(dir_path.glob("*.json"))
        if len(current_json) == 0:
            self.append_metadata(mdict, 3, "mdict") # THIS LINE NEEDS TO BE CHECKED ON 
            self.create_metadata_file(dir_path, mdict)
            # self.metadata = self.read_metadata(dir_path)
        elif overwrite_flag is True:
            display("Overwriting metadata.json file")
            # self.metadata.update({argname('mdict', 2):mdict})
            self.append_metadata(mdict, 3, "mdict") # THIS LINE NEEDS TO BE CHECKED ON 
            self.create_metadata_file(dir_path, mdict)
            # self.metadata = self.read_metadata(dir_path)
        else:
            display("Json file already exists")

    def read_metadata(self, dir_path):
        with open(dir_path / "metadata.json", 'r', encoding='utf8') as json_file:
                metadata = json.load(json_file)
        return metadata

    def append_metadata(self, dict_to_add:dict, backframe=1, str_dict:str = 'dict_to_add'):
        # display(argname('dict_to_add'))
        self.metadata.update({argname(f"{str_dict}", frame=backframe):dict_to_add})

        # NEED TO TEST 
    def load_metadata_and_display(self, dir_path:Path):
        current_json = list(dir_path.glob("*.json"))
        # display(current_json)
        # display(dir_path / "metadata.json")
        if len(current_json) == 1:
            metadata = self.read_metadata(dir_path)
            display(metadata)
        elif (len(current_json) == 0) and dir_path.is_dir():
            display("There is no metadata, please call 'create_metadata_for_directory' to create one")
        else:
            display("There is more than one metadata file, please check")

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
# Saving data to datahandler

    def save_array(self, arr:list):
        if isinstance(arr, np.ndarray) is True:
            self[self.key] = arr.tolist()
        else:
            self[self.key] = arr
        self.key += 1
        
    def save_array_dict(self, dict:dict):
        for idx, value in dict.items():
            self.save_array(value)

    # Private function
    def __convert_array_into_dataset(self, idx, column_name):
        value = self[idx]
        # display(value)
        if isinstance(value, list) is True:
            temp_frame = pd.DataFrame(value, columns=[column_name])
            self[idx] = DataSet(None, temp_frame)

    # Private function 
    def __join_inner_dataframes_for_array(self, list_of_idx:list):
        smallest_value = min(list_of_idx)
        list_of_relevant_dataframes = [value.data for idx, value in self.items()]
        # Check if each relevant dataframe is only size one (indicating that they were made from 
            # an array/np_array)
        for dframe in list_of_relevant_dataframes:
            if len(dframe.columns) != 1:
                display(f"You tried to append an array to an already existing dataframe")
                return

        temp_frame = pd.concat(list_of_relevant_dataframes, axis=1)
        self[smallest_value] = DataSet(None, temp_frame)
        for index in list_of_idx:
            if index is not smallest_value:
                self.pop(index)
                self.key -= 1

    def convert_arrays_to_dataframes(self, list_of_lists:list, column_name_list:list):
        for item_in_list in list_of_lists:
            self.save_array(item_in_list)
        
        column_key = 0
        list_of_idx = []
        for idx, value in self.items():
            if isinstance(value, list) is True:
                self.__convert_array_into_dataset(idx, column_name_list[column_key])
                list_of_idx.append(idx)
                column_key += 1
        
        self.__join_inner_dataframes_for_array(list_of_idx)
        pass

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
# Exporting data from datahandler

    def export_from_type_pandas(self, path:Path):
        for idx, value in self.items():
            if isinstance(value, DataSet) or isinstance(value, pd.DataFrame):
                if isinstance(value, DataSet):
                    value.data.to_csv(path)
                else:
                    value.to_csv(path)

    def export_data(self, measurement:str, save_dir:str = "./data", experiment_category:str = ""):
        if not isinstance(save_dir, Path):
            save_dir = Path(save_dir).absolute()
        
        file_dir = save_dir / experiment_category / measurement

        if not file_dir.exists():
            display(f"Creating experiment category: {experiment_category}")
            display(f"  under the save directory: {save_dir}")
            file_dir.mkdir(exist_ok=True, parents=True)

        expt_no = len(list(file_dir.glob("*.csv"))) + 1    
        filename = f"{measurement}_{expt_no:03d}.csv"
        final_path = file_dir / filename
        self.create_metadata_file(file_dir)
        self.export_from_type_pandas(final_path)

        
## Get / Set functions
    def get_metadata(self):
        return self.metadata

    def get_key(self):
        return self.key

# %%


# Test Code for metadata
if __name__ == "__main__":
    # Initializing
    data_dir = Path("../../experiments/TWPA Calibration/data/cooldown59/Line6_SEG_PdAu_02/Line6_SEG_PdAu_02_01_21_0108PM_TWPA_Calibration")
    parent_data_dir = Path("../../experiments/TWPA Calibration/data/cooldown59/Line6_SEG_PdAu_02")
    assert data_dir.exists()
    
    # data_dir_list = [data_path.absolute() for data_path in data_dir.glob("*")]
    # display(data_dir_list)

    dh = DataHandler()
    
    # csv_list = [x for x in list(data_dir.glob("*"))if "DS" not in x.name]
    # for direct in csv_list:
    #     dh.load_data_directory(direct, None)
    metadata_info = {
        "Instrument name": "TWPA",
        "Timestamp": f"{datetime.now().date()}{"_"}{datetime.now().time().hour}:{datetime.now().time().minute}",
        "Power": 7990
    }

    metadata_info2 = {
        "Instrument name": "Catci",
        "Timestamp": f"{datetime.now().date()}{"_"}{datetime.now().time().hour}:{datetime.now().time().minute}",
        "Power": 200
    }
    dh.load_sets(parent_data_dir, metadata_info, True)
    # dh.create_metadata_for_directory(parent_data_dir, {"cats":"fish"})
    # dh.load_data_directory_rec(parent_data_dir, None)

    # dh.load_metadata_and_display(parent_data_dir)

    dh.append_metadata(metadata_info2)
    display(dh.get_metadata())
    dh.create_metadata_file(parent_data_dir)
    # dh.display_datasets()

    # for index in range(len(dh)):
    #     display(dh[index].data)
    


    # %%
    
    """
        2/18/25 - currently, our DataHandler can load an entire directory of csv files, or load csv files one by one.
        
        However, we also want DataHandler to save the data we've taken, not just load data from a past experiment
        
        Here are some possible implementations of how we'd actually *use* DataHandler during the measurement process
    
    """
    
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
    
    dh_save.save_array_dict(data_to_save)  # XXX - 03/04 jorge: I'd rather just call 'save_array' in a loop than use a method like this
    
    dh_save.display_datasets()
    
    #### method 3 - pass datahandler object to measurement method, this is the final goal for the project
    
    """
    
    dh_save = DataHandler()
    experiment.take_data(dh_save)
    
    #           . 
    #           .
    #    measurement code
    #           .
    #           .
    
    dh_save.display_datasets()
    dh_save.save_experiment_data()
    
    """
    
    
    # XXX - 03/04 jorge:    there should be a way for the dataset (or the datahandler) to handle errors
    #                               that arise from invalid objects, like "DS_Store". Perhaps the simplest
    #                               way would be for the DataSet to set itself equal to None, and have the 
    #                               DataHandler watch out for that and remove if it arises? Or maybe a flag
    #                               within DataSet that's called "error_state" or something. The point is
    #                               that instead of crashing the entire experiment, an invalid DataSet will
    #                               will just take itself out to the trash
    # TODO:                  can we incorporater the python tabulate module?
    
