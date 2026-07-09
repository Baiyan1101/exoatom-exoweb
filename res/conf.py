import os
from pathlib import Path

exoatom_path = os.environ.get(
    "EXOATOM_PROJECT_PATH",
    "/mnt/data/bzhang/exoatom-work/exoatom",
)
DATA_DIR = Path(os.environ.get("EXOATOM_DATA_DIR", "/mnt/data/bzhang/exoatom_data"))
