import pytest
import numpy as np
import pandas as pd
import json
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from bcqthub.src.DataHandler_Num2 import DataSet, DataHandler, DataSetLoader, MetadataManager


@pytest.fixture
def example_dataframe():
    return pd.DataFrame({
        "time": np.linspace(0, 10, 5),
        "signal": np.sin(np.linspace(0, 10, 5))
    })


def test_dataset_save_and_load(example_dataframe):
    with TemporaryDirectory() as tmpdirname:
        tmpdir = Path(tmpdirname)
        dataset = DataSet(example_dataframe)
        path = tmpdir / "test.csv"
        DataSetLoader.save_csv(dataset, path)
        loaded = DataSetLoader.load_csv(path)
        pd.testing.assert_frame_equal(dataset.data, loaded.data)


def test_metadata_save_and_load():
    metadata = {"experiment": "pytest_test"}
    with TemporaryDirectory() as tmpdirname:
        tmpdir = Path(tmpdirname)
        MetadataManager.create_metadata_file(tmpdir, metadata)
        loaded = MetadataManager.read_metadata_file(tmpdir)
        assert metadata == loaded


def test_datahandler_add_and_save(example_dataframe):
    handler = DataHandler()
    handler.add_dataset(DataSet(example_dataframe))
    handler.metadata = {"info": "pytest_handler_test"}

    with TemporaryDirectory() as tmpdirname:
        tmpdir = Path(tmpdirname)
        handler.save_all(tmpdir)
        handler.save_metadata(tmpdir)

        # Check that files exist
        assert (tmpdir / "dataset_0.csv").exists()
        assert (tmpdir / "metadata.json").exists()

        # Check metadata round trip
        handler.load_metadata(tmpdir)
        assert handler.metadata["info"] == "pytest_handler_test"

        # Check dataset reload
        loaded = DataSetLoader.load_csv(tmpdir / "dataset_0.csv")
        pd.testing.assert_frame_equal(handler.get_dataset(0).data, loaded.data)

