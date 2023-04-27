"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
import json
from typing import Any
from pathlib import Path

# * Gid Imports ----------------------------------------------------------------------------------------->

import importlib.resources as importlib_resources

# endregion [Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion [Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()
JSON_DATA_DIR = importlib_resources.files("gidapptools.data.json")
WEBCOLORS_JSON = JSON_DATA_DIR.joinpath("webcolors.json")

# endregion [Constants]


def _load_webcolors_data() -> tuple[dict[str:tuple[int, int, int, float]]]:
    with WEBCOLORS_JSON.open('r', encoding='utf-8', errors='ignore') as f:
        data = json.load(f)
    _out = []
    for item_data in data:
        new_item_data = {}
        new_item_data["name"] = item_data.get("name").casefold()
        new_item_data["value"] = (item_data.get("rgb").get('r'), item_data.get("rgb").get('g'), item_data.get("rgb").get('b'), 1.0)
        _out.append(new_item_data)
    return tuple(_out)


ALL_WEBCOLORS: tuple[dict[str:tuple[int, int, int, float]]] = _load_webcolors_data()

ALL_WEBCOLORS_BY_NAME: dict[str, tuple[int, int, int, float]] = {i["name"]: i["value"] for i in ALL_WEBCOLORS}

ALL_WEBCOLORS_BY_VALUE: dict[tuple[int, int, int, float], str] = {i["value"]: i["name"] for i in ALL_WEBCOLORS}


# region [Main_Exec]


if __name__ == '__main__':
    pass

# endregion [Main_Exec]
