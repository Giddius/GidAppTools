# region [Imports]

import pytest
from pytest import param
from typing import TypedDict, NamedTuple, Any
from pytest_lazyfixture import lazy_fixture

from pathlib import Path
from gidapptools.gid_config.interface import get_config, ResolvedSection, ResolvedEntry, MissingDefaultValue

# endregion[Imports]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion [Constants]

# region [Helper]


class ResultItem(TypedDict):
    get_checks: dict[tuple[str, str], object]

    set_checks: dict[tuple[str, str], object]

# endregion [Helper]

# region [test_1]


result_item_1 = ResultItem(get_checks={("first_section", "entry_one"): "one",
                                       ("first_section", "entry_two"): Path("c:/path/to/two"),
                                       ("first_section", "entry_three"): 3},
                           set_checks={("first_section", "entry_one"): "two"})

test_complete_gid_config_params = [param(lazy_fixture("basic_configspec_path"), lazy_fixture("basic_ini_file_not_existing"), False, result_item_1, id="basic_1")]


@pytest.mark.parametrize(["in_spec_path", "in_config_path", "preload_ini", "result_item"], test_complete_gid_config_params)
def test_complete_gid_config(in_spec_path: Path, in_config_path: Path, preload_ini: bool, result_item: ResultItem):
    config = get_config(in_spec_path, in_config_path, preload_ini_file=preload_ini)
    for entry_path, result_value in result_item["get_checks"].items():
        assert config.get(*entry_path) == result_value

    for entry_path, result_set_value in result_item["set_checks"].items():
        config.set(*entry_path, result_set_value)

        assert config.get(*entry_path) == result_set_value

# endregion [test_1]
