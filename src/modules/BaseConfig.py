from abc import ABC, abstractmethod

# Abstract Base Class for Configuration
class BaseConfiguration(ABC):
    
    # why abstract methods?
    #   each new class that extends BaseConfiguration
    # will have its own method for save/load, but by
    # making an abstract method, we give a template!
    
    @abstractmethod
    def load(self):  
        pass

    @abstractmethod
    def save(self):
        pass

# Experiment Configuration Class
class ExperimentConfiguration(BaseConfiguration):
    def __init__(self, experiment_name, parameters):
        self._experiment_name = experiment_name
        self._parameters = parameters
    
    @property
    def name(self):
        return self._experiment_name

    @property
    def settings(self):
        return self._parameters

    def load(self):
        print(f"Loading experiment configuration for {self.name}...")

    def save(self):
        print(f"Saving experiment configuration for {self.name}...")


# Instrument Configuration Class
class InstrumentConfiguration(BaseConfiguration):
    def __init__(self, instrument_name, settings):
        self._instrument_name = instrument_name
        self._settings = settings

    @property
    def name(self):
        return self._instrument_name

    @property
    def settings(self):
        return self._settings

    def load(self):
        print(f"Loading instrument configuration for {self.name}...")

    def save(self):
        print(f"Saving instrument configuration for {self.name}...")
        
        
        
        
# Experiment Configuration Class
class ExptConfig():
    def __init__(self, ExptConfig_Dict):
        print("ExptConfig")
        
        self.experiment_name = ExptConfig_Dict["experiment_name"]
        self.ExptConfig_Dict = ExptConfig_Dict

    def __del__(self):
        """
            Deconstructor to free resources
        """
        if self.rm:
            self.rm.close()
            
    def print_class_members(self):
        """
            Prints all members in the class
        """
        for k, v in self.__dict__.items():
            print(f'{k} : {v}')
            
    def load_config(self):
        print(f"Loading experiment configuration for (placeholder)...")

    def save_config(self):
        print(f"Saving experiment configuration for (placeholder)...")


    def add_parameter(self, parameter):
        """
            provide the new parameter as a dict or tuple with a name and value
                parameter = {"name" : value}
                    or
                parameter = (name, value)
        """
        
        if type(parameter) == dict:
           self.ExptConfig_Dict = self.ExptConfig_Dict | parameter
           
        elif type(parameter) == tuple:
            key, value = parameter
            self.ExptConfig_Dict[key] = value
        else:
            raise TypeError("\n\n    Input parameter must be a dict or tuple.\n\n")
        
        

