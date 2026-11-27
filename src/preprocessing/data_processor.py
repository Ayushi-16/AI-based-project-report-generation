
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


def preprocess_project_data(df: pd.DataFrame):
    """
    Clean and preprocess project management data.
    Returns cleaned data and a list of quality issues.
    """

    df = df.copy()
    issues = []

    # 1. Validate required columns

    missing_columns = [
        col for col in REQUIRED_COLUMNS
        if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing columns: {missing_columns}"
        )

    # 2. Clean text columns

    text_columns = [
        "Task", "Owner", "Status",
        "Dependency", "Update"
    ]

    for column in text_columns:
        df[column] = (
            df[column]
            .fillna("")
            .astype(str)
            .str.strip()
        )

    # 3. Handle progress values

    df["Progress"] = pd.to_numeric(
        df["Progress"],
        errors="coerce"
    )

    invalid_progress = df["Progress"].isna()

    if invalid_progress.any():
        issues.append(
            f"{invalid_progress.sum()} records "
            "have missing or invalid progress."
        )

    invalid_range = (
        df["Progress"].notna()
        & ~df["Progress"].between(0, 100)
    )

    if invalid_range.any():
        issues.append(
            f"{invalid_range.sum()} records have "
            "progress outside 0-100."
        )

    # 4. Parse dates

    df["Due_Date"] = pd.to_datetime(
        df["Due_Date"],
        errors="coerce"
    )

    invalid_dates = df["Due_Date"].isna()

    if invalid_dates.any():
        issues.append(
            f"{invalid_dates.sum()} records "
            "have invalid or missing due dates."
        )

    # 5. Validate status

    invalid_status = (
        ~df["Status"].isin(VALID_STATUSES)
    )

    if invalid_status.any():
        issues.append(
            f"{invalid_status.sum()} records "
            "have invalid task statuses."
        )

    # 6. Identify potential duplicates

    duplicate_tasks = df.duplicated(
        subset=["Task"],
        keep=False
    )

    if duplicate_tasks.any():
        issues.append(
            f"{duplicate_tasks.sum()} records "
            "have potentially duplicated task names."
        )

    # 7. Identify missing important information

    for column in ["Task", "Owner", "Update"]:
        missing = df[column].eq("")

        if missing.any():
            issues.append(
                f"{missing.sum()} records have "
                f"missing {column} information."
            )

    return df, issues

def validate_dependencies(df):
    """
    Identify dependencies that reference
    tasks not present in the project dataset.
    """

    known_tasks = set(df["Task"].dropna())

    invalid_dependencies = []

    for _, row in df.iterrows():

        dependency = row["Dependency"]

        if not dependency or dependency.lower() == "none":
            continue

        if dependency not in known_tasks:
            invalid_dependencies.append({
                "Task": row["Task"],
                "Invalid Dependency": dependency
            })

    return invalid_dependencies