import pandas as pd
import sys
from pathlib import Path

root = Path.cwd().resolve()
sys.path.insert(0, str(root))

from src.preprocessing.data_validator import (
    validate_project_data
)


def test_valid_project_data():

    df = pd.read_csv("sample_updates.csv")

    result = validate_project_data(df)

    assert result["valid"] is True


def test_invalid_progress():

    df = pd.read_csv("sample_updates.csv")

    df.loc[0, "Progress"] = 150

    result = validate_project_data(df)

    assert result["progress"]["valid"] is False


def test_invalid_status():

    df = pd.read_csv("sample_updates.csv")

    df.loc[0, "Status"] = "Unknown"

    result = validate_project_data(df)

    assert result["status"]["valid"] is False


def test_missing_column():

    df = pd.read_csv("sample_updates.csv")

    df = df.drop(columns=["Owner"])

    result = validate_project_data(df)

    assert result["valid"] is False


def test_invalid_dependency():

    df = pd.read_csv("sample_updates.csv")

    df.loc[0, "Dependency"] = "Nonexistent Task"

    result = validate_project_data(df)

    assert len(result["dependencies"]) == 1
