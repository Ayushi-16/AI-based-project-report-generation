import pandas as pd
import pytest
import sys
from pathlib import Path

root = Path.cwd().resolve()
sys.path.insert(0, str(root))

from src.ingestion.csv_loader import (
    load_csv,
    get_dataset_info
)


def test_load_csv():

    df = load_csv("sample_updates.csv")

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 5
    assert len(df.columns) == 7


def test_dataset_info():

    df = load_csv("sample_updates.csv")

    info = get_dataset_info(df)

    assert info["rows"] == 5
    assert info["columns"] == 7


def test_empty_file_source():

    with pytest.raises(ValueError):
        load_csv(None)


def test_missing_file():

    with pytest.raises(FileNotFoundError):
        load_csv("missing_file.csv")
