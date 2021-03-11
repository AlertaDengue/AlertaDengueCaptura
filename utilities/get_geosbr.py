import json
import logging
import os

import numpy as np
from dotenv import load_dotenv
from geobr import read_municipality

from utilities.initials import initials

load_dotenv()


path_ = os.getenv("GEOJSON_PATH")


def get_geobr():
    for k, v in initials.items():
        ufs = v.upper()
        df = read_municipality(code_muni=ufs, year=2019)
        cols = ['code_muni', 'code_state', 'code_region']
        df[cols] = df[cols].applymap(np.int64)
        result = df.to_json()
        parsed = json.loads(result)
        fname = f"{v}-municipalities.json"
        to_path = os.path.join(path_, fname)

        with open(to_path, 'w') as f:
            json.dump(parsed, f)
            logging.warning(f"Saving the JSON to {k} state in {to_path}")


if __name__ == "__main__":
    get_geobr()
