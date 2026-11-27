
import pandas as pd

REQUIRED_COLUMNS = [
    "Task",
    "Owner",
    "Status",
    "Progress",
    "Due_Date",
    "Dependency",
    "Update"
]

VALID_STATUSES = [
    "Completed",
    "In Progress",
    "Delayed",
    "Pending"
]


def validate_schema(df):
    """Check whether required columns exist."""

    missing_columns = [
        col for col in REQUIRED_COLUMNS
        if col not in df.columns
    ]

    return {
        "valid": len(missing_columns) == 0,
        "missing_columns": missing_columns
    }



def validate_missing_values(df):
    """
    Identify missing values in important fields.

    Dependency is optional, so missing dependencies
    are not treated as data quality problems.
    """

    optional_columns = ["Dependency"]

    missing = {}

    for column in REQUIRED_COLUMNS:

        if column in optional_columns:
            continue

        if column in df.columns:

            count = df[column].isna().sum()

            if count > 0:
                missing[column] = int(count)

    return missing


def validate_progress(df):
    """Validate numeric progress values."""

    progress = pd.to_numeric(
        df["Progress"],
        errors="coerce"
    )

    invalid = (
        progress.isna()
        | ~progress.between(0, 100)
    )

    return {
        "valid": not invalid.any(),
        "invalid_rows": df.index[invalid].tolist()
    }


def validate_status(df):
    """Check whether task statuses are valid."""

    invalid = ~df["Status"].isin(VALID_STATUSES)

    return {
        "valid": not invalid.any(),
        "invalid_values": (
            df.loc[invalid, "Status"]
            .dropna()
            .unique()
            .tolist()
        )
    }


def validate_dates(df):
    """Identify invalid due dates."""

    dates = pd.to_datetime(
        df["Due_Date"],
        errors="coerce"
    )

    invalid = dates.isna()

    return {
        "valid": not invalid.any(),
        "invalid_rows": df.index[invalid].tolist()
    }


def validate_duplicates(df):
    """Identify potentially duplicated task names."""

    duplicates = df[
        df["Task"].duplicated(keep=False)
    ]

    return {
        "valid": duplicates.empty,
        "duplicate_tasks": (
            duplicates["Task"].dropna().unique().tolist()
        )
    }


def validate_dependencies(df):
    """Check whether referenced tasks exist."""

    known_tasks = set(
        df["Task"].dropna().astype(str).str.strip()
    )

    invalid = []

    for _, row in df.iterrows():

        dependency = str(
            row["Dependency"]
        ).strip()

        if dependency.lower() in ("", "none", "nan"):
            continue

        if dependency not in known_tasks:
            invalid.append({
                "task": row["Task"],
                "dependency": dependency
            })

    return invalid


def validate_project_data(df):

    schema = validate_schema(df)

    if not schema["valid"]:
        return {
            "valid": False,
            "schema": schema,
            "message": "Required columns are missing."
        }

    results = {
        "schema": schema,
        "missing_values": validate_missing_values(df),
        "progress": validate_progress(df),
        "status": validate_status(df),
        "dates": validate_dates(df),
        "duplicates": validate_duplicates(df),
        "dependencies": validate_dependencies(df)
    }

    results["valid"] = (
        not results["missing_values"]
        and results["progress"]["valid"]
        and results["status"]["valid"]
        and results["dates"]["valid"]
        and results["duplicates"]["valid"]
        and not results["dependencies"]
    )

    return results
