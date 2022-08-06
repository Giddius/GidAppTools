# region [Imports]

from pathlib import Path

# endregion [Imports]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion [Constants]


FILES = [THIS_FILE_DIR.joinpath("basic_configspec.json")]


FILES_MAP = {p.name.casefold(): p for p in FILES}


def get_file_path(name: str) -> Path:
    return FILES_MAP[name.casefold()]
