import os
from pathlib import Path

# database.py uses open("../data_json/food.json") which is relative to CWD.
# Setting CWD to data_models/ makes that path resolve correctly.
os.chdir(Path(__file__).parent.parent / "data_models")