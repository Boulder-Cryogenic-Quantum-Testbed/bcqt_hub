import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, Dict
import json


class DataSet:
    def __init__(self, data: pd.DataFrame, file_path: Optional[Path] = None):
        self.data = data
        self.file_path = file_path

    def __len__(self):
        return len(self.data)

    def __str__(self):
        return f"DataSet({len(self.data)} rows)"


class DataSetLoader:
    @staticmethod
    def load_csv(path: Path) -> DataSet:
        df = pd.read_csv(path, index_col=0)
        return DataSet(df, file_path=path)

    @staticmethod
    def save_csv(dataset: DataSet, path: Path):
        dataset.data.to_csv(path)


class MetadataManager:
    @staticmethod
    def create_metadata_file(dir_path: Path, metadata: Dict):
        with open(dir_path / "metadata.json", "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=4)

    @staticmethod
    def read_metadata_file(dir_path: Path) -> Dict:
        with open(dir_path / "metadata.json", "r", encoding="utf-8") as f:
            return json.load(f)


class DataHandler:
    def __init__(self):
        self.datasets: Dict[int, DataSet] = {}
        self.metadata: Dict = {}
        self.key_counter = 0

    def add_dataset(self, dataset: DataSet):
        self.datasets[self.key_counter] = dataset
        self.key_counter += 1

    def get_dataset(self, key: int) -> Optional[DataSet]:
        return self.datasets.get(key)

    def save_all(self, dir_path: Path):
        for key, dataset in self.datasets.items():
            filename = f"dataset_{key}.csv"
            DataSetLoader.save_csv(dataset, dir_path / filename)

    def load_metadata(self, dir_path: Path):
        self.metadata = MetadataManager.read_metadata_file(dir_path)

    def save_metadata(self, dir_path: Path):
        MetadataManager.create_metadata_file(dir_path, self.metadata)


# Test code
if __name__ == "__main__":
    # Create example DataFrame
    df = pd.DataFrame({
        "time": np.linspace(0, 10, 5),
        "signal": np.sin(np.linspace(0, 10, 5))
    })

    # Initialize dataset and handler
    dataset = DataSet(df)
    handler = DataHandler()
    handler.add_dataset(dataset)

    # Define a path to save to (ensure this path exists or adjust accordingly)
    save_path = Path("./test_output")
    save_path.mkdir(parents=True, exist_ok=True)

    # Save dataset and metadata
    handler.save_all(save_path)
    handler.metadata = {"experiment": "sine_wave_test"}
    handler.save_metadata(save_path)

    # Load metadata to verify
    handler.load_metadata(save_path)
    print("Loaded metadata:", handler.metadata)

    # Verify saved CSV
    loaded_dataset = DataSetLoader.load_csv(save_path / "dataset_0.csv")
    print("Loaded dataset:", loaded_dataset)
