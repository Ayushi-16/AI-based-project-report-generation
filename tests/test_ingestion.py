import sys
from pathlib import Path

root = Path.cwd().resolve()
sys.path.insert(0, str(root))

from src.ingestion.csv_loader import load_csv, get_dataset_info

df = load_csv("sample_updates.csv")

print(df.head())

print("\nDataset information:")

print(get_dataset_info(df))