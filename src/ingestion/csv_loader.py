
import pandas as pd
from io import BytesIO


def load_csv(file_source) -> pd.DataFrame:
    """
    Load project data from a CSV file.

    Parameters:
        file_source: File path or uploaded file object.

    Returns:
        pandas DataFrame
    """

    if file_source is None:
        raise ValueError("No CSV file was provided.")

    try:
        df = pd.read_csv(
            file_source,
            encoding="utf-8"
        )

        if df.empty:
            raise ValueError(
                "The uploaded CSV file is empty."
            )

        return df

    except UnicodeDecodeError:
        raise ValueError(
            "Unsupported file encoding. "
            "Please upload a UTF-8 CSV file."
        )

    except pd.errors.EmptyDataError:
        raise ValueError(
            "The CSV file contains no data."
        )

    except pd.errors.ParserError:
        raise ValueError(
            "Unable to parse CSV. "
            "Please check its structure."
        )


def get_dataset_info(df: pd.DataFrame) -> dict:
    """
    Return basic information about the dataset.
    """

    return {
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": df.columns.tolist(),
        "memory_usage": df.memory_usage(
            deep=True
        ).sum()
    }
